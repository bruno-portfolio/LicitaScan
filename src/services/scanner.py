"""Serviço principal de varredura do PNCP."""

import asyncio
import logging
import time
from collections import Counter
from collections.abc import Callable

from src.api.pncp_client import PNCPClient
from src.config import MODALIDADES
from src.filters.matcher import KeywordMatcher
from src.models.schemas import FilterConfig, Licitacao, ScanProgress, ScanResult

logger = logging.getLogger(__name__)


class Scanner:
    """Orquestra a varredura de licitações no PNCP."""

    def __init__(
        self,
        config: FilterConfig,
        progress_callback: Callable[[ScanProgress], None] | None = None,
        stop_check: Callable[[], bool] | None = None,
    ) -> None:
        self.config = config
        self.progress_callback = progress_callback
        self.stop_check = stop_check
        self.matcher = KeywordMatcher(
            keywords_core=config.keywords_core,
            keywords_related=config.keywords_related,
        )
        self._progress = ScanProgress()
        self._stopped = False

    def _update_progress(self, **kwargs) -> None:
        """Atualiza e notifica progresso."""
        for key, value in kwargs.items():
            if hasattr(self._progress, key):
                setattr(self._progress, key, value)

        if self.progress_callback:
            self.progress_callback(self._progress)

    def _should_stop(self) -> bool:
        """Verifica se deve parar a execução."""
        if self._stopped:
            return True
        if self.stop_check and self.stop_check():
            self._stopped = True
            return True
        return False

    async def _buscar_estado(
        self,
        client: PNCPClient,
        uf: str,
        intervalos: list[tuple[str, str]],
    ) -> tuple[list[Licitacao], int, list[str]]:
        """Busca licitações de um estado (todas modalidades em paralelo)."""
        licitacoes: list[Licitacao] = []
        total = 0
        erros: list[str] = []

        async def buscar_modalidade(cod_mod: int) -> tuple[list[Licitacao], int, list[str]]:
            mod_lics: list[Licitacao] = []
            mod_total = 0
            mod_erros: list[str] = []

            for data_ini, data_fim in intervalos:
                if self._should_stop():
                    break
                try:
                    async for licitacao in client.buscar_licitacoes(
                        uf, data_ini, data_fim, cod_mod
                    ):
                        if self._should_stop():
                            break
                        mod_total += 1
                        mod_lics.append(licitacao)
                except Exception as e:
                    mod_erros.append(f"{uf}/{cod_mod}: {str(e)}")

            return mod_lics, mod_total, mod_erros

        # Buscar todas modalidades em paralelo
        tasks = [buscar_modalidade(cod_mod) for cod_mod in self.config.modalidades]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                erros.append(str(result))
            else:
                mod_lics, mod_total, mod_erros = result
                licitacoes.extend(mod_lics)
                total += mod_total
                erros.extend(mod_erros)

        return licitacoes, total, erros

    async def executar(self) -> ScanResult:
        """Executa varredura completa (paralela por estado)."""
        inicio = time.time()
        all_licitacoes: list[Licitacao] = []
        total_varrido = 0
        keywords_count: Counter = Counter()
        erros: list[str] = []

        intervalos = PNCPClient.gerar_intervalos_mensais(self.config.meses_historico)
        total_estados = len(self.config.estados)
        estados_completos = 0

        self._update_progress(status="running", percentual=0)

        async with PNCPClient() as client:
            # Buscar estados em paralelo (máximo 3 simultâneos para não sobrecarregar)
            semaphore = asyncio.Semaphore(3)

            async def buscar_com_limite(uf: str):
                async with semaphore:
                    if self._should_stop():
                        return [], 0, []
                    self._update_progress(estado_atual=uf)
                    return await self._buscar_estado(client, uf, intervalos)

            tasks = [buscar_com_limite(uf) for uf in self.config.estados]

            for coro in asyncio.as_completed(tasks):
                if self._should_stop():
                    break

                try:
                    lics_raw, count, state_erros = await coro
                    total_varrido += count
                    erros.extend(state_erros)

                    # Processar licitações com matcher
                    for lic in lics_raw:
                        resultado = self.matcher.processar_licitacao(lic)
                        if resultado is None:
                            continue
                        if self.config.apenas_abertas and not resultado.is_aberta:
                            continue
                        resultado.score = self._calcular_score(resultado)
                        all_licitacoes.append(resultado)
                        keywords_count[resultado.keyword_match] += 1

                    estados_completos += 1
                    percentual = (estados_completos / total_estados) * 100
                    self._update_progress(
                        total_processado=total_varrido,
                        total_matches=len(all_licitacoes),
                        percentual=percentual,
                    )

                except Exception as e:
                    logger.error(f"Erro: {e}")
                    erros.append(str(e))

        # Ordenar por score
        all_licitacoes.sort(key=lambda x: x.score, reverse=True)

        tempo_total = time.time() - inicio
        status = "stopped" if self._stopped else "completed"
        self._update_progress(status=status, percentual=100 if not self._stopped else self._progress.percentual)

        return ScanResult(
            licitacoes=all_licitacoes,
            total_varrido=total_varrido,
            total_encontrado=len(all_licitacoes),
            total_abertas=sum(1 for lic in all_licitacoes if lic.is_aberta),
            keywords_contagem=dict(keywords_count),
            tempo_execucao=round(tempo_total, 2),
            erros=erros,
        )

    def _calcular_score(self, licitacao: Licitacao) -> int:
        """Calcula score de relevância."""
        score = 0

        # Categoria
        if licitacao.categoria == "core":
            score += 30
        elif licitacao.categoria == "related":
            score += 15

        # Status
        if licitacao.is_aberta:
            score += 40

        # Valor (licitações maiores = mais relevantes)
        if licitacao.valor_estimado > 100_000:
            score += 20
        elif licitacao.valor_estimado > 50_000:
            score += 10

        return score


async def executar_scan(
    config: FilterConfig,
    progress_callback: Callable[[ScanProgress], None] | None = None,
    stop_check: Callable[[], bool] | None = None,
) -> ScanResult:
    """Helper function para executar scan."""
    scanner = Scanner(config, progress_callback, stop_check)
    return await scanner.executar()
