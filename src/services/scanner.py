"""Serviço principal de varredura do PNCP."""

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
    ) -> None:
        self.config = config
        self.progress_callback = progress_callback
        self.matcher = KeywordMatcher(
            keywords_core=config.keywords_core,
            keywords_related=config.keywords_related,
            blacklist=config.blacklist,
        )
        self._progress = ScanProgress()

    def _update_progress(self, **kwargs) -> None:
        """Atualiza e notifica progresso."""
        for key, value in kwargs.items():
            if hasattr(self._progress, key):
                setattr(self._progress, key, value)

        if self.progress_callback:
            self.progress_callback(self._progress)

    async def executar(self) -> ScanResult:
        """Executa varredura completa."""
        inicio = time.time()
        licitacoes: list[Licitacao] = []
        total_varrido = 0
        keywords_count: Counter = Counter()
        erros: list[str] = []

        # Calcular total de operações para percentual
        intervalos = PNCPClient.gerar_intervalos_mensais(self.config.meses_historico)
        total_ops = (
            len(self.config.estados) * len(self.config.modalidades) * len(intervalos)
        )
        ops_completas = 0

        self._update_progress(status="running", percentual=0)

        async with PNCPClient() as client:
            for uf in self.config.estados:
                self._update_progress(estado_atual=uf)

                for cod_mod in self.config.modalidades:
                    modalidade_nome = MODALIDADES.get(cod_mod, str(cod_mod))
                    self._update_progress(modalidade_atual=modalidade_nome)

                    for data_ini, data_fim in intervalos:
                        try:
                            async for licitacao in client.buscar_licitacoes(
                                uf, data_ini, data_fim, cod_mod
                            ):
                                total_varrido += 1
                                self._update_progress(total_processado=total_varrido)

                                # Processar com matcher
                                resultado = self.matcher.processar_licitacao(licitacao)
                                if resultado is None:
                                    continue

                                # Filtrar apenas abertas se configurado
                                if (
                                    self.config.apenas_abertas
                                    and not resultado.is_aberta
                                ):
                                    continue

                                # Calcular score
                                resultado.score = self._calcular_score(resultado)

                                licitacoes.append(resultado)
                                keywords_count[resultado.keyword_match] += 1

                                self._update_progress(total_matches=len(licitacoes))

                        except Exception as e:
                            erro = f"{uf}/{cod_mod}: {str(e)}"
                            logger.error(erro)
                            erros.append(erro)

                        ops_completas += 1
                        percentual = (ops_completas / total_ops) * 100
                        self._update_progress(percentual=percentual)

        # Ordenar por score
        licitacoes.sort(key=lambda x: x.score, reverse=True)

        tempo_total = time.time() - inicio
        self._update_progress(status="completed", percentual=100)

        return ScanResult(
            licitacoes=licitacoes,
            total_varrido=total_varrido,
            total_encontrado=len(licitacoes),
            total_abertas=sum(1 for lic in licitacoes if lic.is_aberta),
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
) -> ScanResult:
    """Helper function para executar scan."""
    scanner = Scanner(config, progress_callback)
    return await scanner.executar()
