"""Cliente assíncrono para API do PNCP."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta

import httpx

from src.config import get_settings
from src.models.schemas import Licitacao

logger = logging.getLogger(__name__)


class PNCPClientError(Exception):
    """Erro no cliente PNCP."""

    pass


class PNCPClient:
    """Cliente assíncrono para consulta à API do PNCP."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "PNCPClient":
        """Context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.api_timeout),
            headers={"Accept": "application/json"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Retorna o cliente HTTP."""
        if self._client is None:
            raise PNCPClientError("Client não inicializado. Use async with.")
        return self._client

    async def buscar_pagina(
        self,
        uf: str,
        data_inicial: str,
        data_final: str,
        modalidade: int,
        pagina: int = 1,
    ) -> dict | None:
        """Busca uma página de resultados da API."""
        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "codigoModalidadeContratacao": modalidade,
            "uf": uf,
            "tamanhoPagina": self.settings.page_size,
            "pagina": pagina,
        }

        try:
            response = await self.client.get(self.settings.pncp_base_url, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            logger.warning(f"Timeout na busca: {uf}/{modalidade}/pag{pagina}")
            return None

        except httpx.HTTPStatusError as e:
            logger.warning(
                f"HTTP {e.response.status_code}: {uf}/{modalidade}/pag{pagina}"
            )
            return None

        except httpx.RequestError as e:
            logger.error(f"Erro de conexão: {e}")
            return None

    async def buscar_licitacoes(
        self,
        uf: str,
        data_inicial: str,
        data_final: str,
        modalidade: int,
    ) -> AsyncGenerator[Licitacao, None]:
        """Busca todas as licitações com paginação automática."""
        pagina = 1

        while pagina <= self.settings.max_pages:
            resultado = await self.buscar_pagina(
                uf, data_inicial, data_final, modalidade, pagina
            )

            if not resultado or not resultado.get("data"):
                break

            itens = resultado.get("data", [])

            for item in itens:
                yield self._parse_item(item)

            if len(itens) < self.settings.page_size:
                break

            pagina += 1
            await asyncio.sleep(self.settings.request_delay)

    def _parse_item(self, item: dict) -> Licitacao:
        """Converte item da API para Licitacao."""
        unidade = item.get("unidadeOrgao", {})

        return Licitacao(
            numero_pncp=item.get("numeroControlePNCP", ""),
            objeto=item.get("objetoCompra", ""),
            valor_estimado=item.get("valorTotalEstimado"),
            modalidade=item.get("modalidadeNome", ""),
            situacao=item.get("situacaoCompraLicitacaoNome", ""),
            data_publicacao=item.get("dataPublicacaoPncp"),
            data_encerramento=item.get("dataEncerramentoProposta"),
            orgao=unidade.get("nomeUnidade", ""),
            municipio=unidade.get("municipioNome", ""),
            uf=unidade.get("ufSigla", ""),
            link=item.get("linkSistemaOrigem", ""),
        )

    @staticmethod
    def gerar_intervalos_mensais(meses: int = 1) -> list[tuple[str, str]]:
        """Gera intervalos de datas para busca."""
        intervalos = []
        hoje = datetime.now()

        for i in range(meses):
            fim = hoje - timedelta(days=30 * i)
            inicio = fim - timedelta(days=30)
            intervalos.append((inicio.strftime("%Y%m%d"), fim.strftime("%Y%m%d")))

        return intervalos
