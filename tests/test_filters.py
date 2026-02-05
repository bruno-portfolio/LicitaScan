"""Testes do módulo de filtros."""


from src.filters.matcher import KeywordMatcher
from src.models.schemas import KeywordCategory, Licitacao


class TestKeywordMatcher:
    """Testes para KeywordMatcher."""

    def test_normalizar_texto_acentos(self) -> None:
        """Remove acentos corretamente."""
        assert KeywordMatcher.normalizar_texto("São Paulo") == "sao paulo"
        assert (
            KeywordMatcher.normalizar_texto("Georreferenciamento")
            == "georreferenciamento"
        )
        assert KeywordMatcher.normalizar_texto("PRAD") == "prad"

    def test_normalizar_texto_none(self) -> None:
        """Trata None."""
        assert KeywordMatcher.normalizar_texto(None) == ""
        assert KeywordMatcher.normalizar_texto("") == ""

    def test_match_core_keyword(self) -> None:
        """Match em keyword core."""
        matcher = KeywordMatcher(
            keywords_core=[r"\bgeorreferenciamento\b"],
            keywords_related=[],
        )

        result = matcher.match("Serviço de georreferenciamento de imóveis")

        assert result.matched is True
        assert result.category == KeywordCategory.CORE
        assert result.keyword is not None

    def test_match_related_keyword(self) -> None:
        """Match em keyword relacionada."""
        matcher = KeywordMatcher(
            keywords_core=[r"\bprad\b"],
            keywords_related=[r"\bpaisagismo\b"],
        )

        result = matcher.match("Projeto de paisagismo urbano")

        assert result.matched is True
        assert result.category == KeywordCategory.RELATED

    def test_core_has_priority(self) -> None:
        """Core tem prioridade sobre related."""
        matcher = KeywordMatcher(
            keywords_core=[r"\bprad\b"],
            keywords_related=[r"\bprad\b"],  # Mesmo pattern
        )

        result = matcher.match("Elaboração de PRAD")

        assert result.category == KeywordCategory.CORE

    def test_no_match(self) -> None:
        """Sem match retorna False."""
        matcher = KeywordMatcher(
            keywords_core=[r"\bprad\b"],
            keywords_related=[],
        )

        result = matcher.match("Compra de materiais de escritório")

        assert result.matched is False
        assert result.category is None

    def test_word_boundary(self) -> None:
        """Word boundary funciona."""
        matcher = KeywordMatcher(
            keywords_core=[r"\bcar\b"],
            keywords_related=[],
        )

        # Não deve dar match em "carro"
        assert matcher.match("Compra de carro").matched is False

        # Deve dar match em "CAR" isolado
        assert matcher.match("Cadastro CAR rural").matched is True

    def test_processar_licitacao(self, sample_licitacao: Licitacao) -> None:
        """Processa licitação corretamente."""
        matcher = KeywordMatcher(
            keywords_core=[r"\bgeorreferenciamento\b"],
            keywords_related=[],
        )

        resultado = matcher.processar_licitacao(sample_licitacao)

        assert resultado is not None
        assert resultado.categoria == KeywordCategory.CORE
        assert resultado.keyword_match is not None
        assert resultado.is_aberta is True

    def test_processar_licitacao_sem_match(self, sample_licitacao: Licitacao) -> None:
        """Retorna None se não houver match."""
        matcher = KeywordMatcher(
            keywords_core=[r"\bxyzabc\b"],  # Não vai dar match
            keywords_related=[],
        )

        resultado = matcher.processar_licitacao(sample_licitacao)

        assert resultado is None

    def test_adicionar_keyword_dinamica(self) -> None:
        """Adiciona keyword em runtime."""
        matcher = KeywordMatcher()

        assert matcher.match("teste prad").matched is False

        matcher.adicionar_keyword(r"\bprad\b", KeywordCategory.CORE)

        assert matcher.match("teste prad").matched is True

    def test_total_patterns(self) -> None:
        """Conta patterns corretamente."""
        matcher = KeywordMatcher(
            keywords_core=[r"\ba\b", r"\bb\b"],
            keywords_related=[r"\bc\b"],
        )

        totais = matcher.total_patterns

        assert totais["core"] == 2
        assert totais["related"] == 1
