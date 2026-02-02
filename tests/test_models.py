"""Testes dos models/schemas."""

from datetime import datetime, timedelta

from src.models.schemas import FilterConfig, Licitacao, ScanResult


class TestLicitacao:
    """Testes para modelo Licitacao."""

    def test_parse_datetime_string(self) -> None:
        """Parse de datetime string ISO."""
        lic = Licitacao(
            numero_pncp="123",
            objeto="Teste",
            data_publicacao="2024-01-15T10:00:00Z",
        )

        assert isinstance(lic.data_publicacao, datetime)
        assert lic.data_publicacao.year == 2024

    def test_parse_datetime_none(self) -> None:
        """Parse de datetime None."""
        lic = Licitacao(
            numero_pncp="123",
            objeto="Teste",
            data_publicacao=None,
        )

        assert lic.data_publicacao is None

    def test_parse_valor_float(self) -> None:
        """Parse de valor float."""
        lic = Licitacao(
            numero_pncp="123",
            objeto="Teste",
            valor_estimado=50000.50,
        )

        assert lic.valor_estimado == 50000.50

    def test_parse_valor_none(self) -> None:
        """Parse de valor None vira 0."""
        lic = Licitacao(
            numero_pncp="123",
            objeto="Teste",
            valor_estimado=None,
        )

        assert lic.valor_estimado == 0.0

    def test_verificar_aberta_true(self) -> None:
        """Licitação aberta quando encerramento no futuro."""
        lic = Licitacao(
            numero_pncp="123",
            objeto="Teste",
            data_encerramento=datetime.now() + timedelta(days=5),
        )

        assert lic.verificar_aberta() is True

    def test_verificar_aberta_false(self) -> None:
        """Licitação fechada quando encerramento no passado."""
        lic = Licitacao(
            numero_pncp="123",
            objeto="Teste",
            data_encerramento=datetime.now() - timedelta(days=5),
        )

        assert lic.verificar_aberta() is False

    def test_verificar_aberta_sem_data(self) -> None:
        """Sem data de encerramento retorna False."""
        lic = Licitacao(
            numero_pncp="123",
            objeto="Teste",
            data_encerramento=None,
        )

        assert lic.verificar_aberta() is False


class TestFilterConfig:
    """Testes para FilterConfig."""

    def test_estados_uppercase(self) -> None:
        """Estados são convertidos para maiúsculas."""
        config = FilterConfig(estados=["sp", "mg"])

        assert config.estados == ["SP", "MG"]

    def test_defaults(self) -> None:
        """Valores padrão."""
        config = FilterConfig()

        assert config.estados == []
        assert config.modalidades == [4, 6, 8, 9]
        assert config.meses_historico == 1
        assert config.apenas_abertas is True


class TestScanResult:
    """Testes para ScanResult."""

    def test_taxa_match_zero_varrido(self) -> None:
        """Taxa de match com zero varrido."""
        result = ScanResult(total_varrido=0, total_encontrado=0)

        assert result.taxa_match == 0.0

    def test_taxa_match_calculo(self) -> None:
        """Cálculo correto da taxa."""
        result = ScanResult(total_varrido=1000, total_encontrado=50)

        assert result.taxa_match == 5.0
