"""Pytest fixtures."""

from datetime import datetime, timedelta

import pytest

from src.models.schemas import FilterConfig, Licitacao


@pytest.fixture
def sample_licitacao() -> Licitacao:
    """Licitação de exemplo."""
    return Licitacao(
        numero_pncp="12345678000190-1-000001/2024",
        objeto="Contratação de serviço de georreferenciamento de imóveis rurais",
        valor_estimado=50000.0,
        modalidade="Pregão",
        situacao="Aberta",
        data_publicacao=datetime.now() - timedelta(days=5),
        data_encerramento=datetime.now() + timedelta(days=10),
        orgao="Prefeitura Municipal de Campinas",
        municipio="Campinas",
        uf="SP",
        link="https://pncp.gov.br/exemplo",
    )


@pytest.fixture
def sample_licitacao_fechada() -> Licitacao:
    """Licitação fechada."""
    return Licitacao(
        numero_pncp="12345678000190-1-000002/2024",
        objeto="Elaboração de laudo fitossanitário",
        valor_estimado=25000.0,
        modalidade="Dispensa",
        situacao="Encerrada",
        data_publicacao=datetime.now() - timedelta(days=30),
        data_encerramento=datetime.now() - timedelta(days=5),
        orgao="Prefeitura Municipal de Sumaré",
        municipio="Sumaré",
        uf="SP",
        link="https://pncp.gov.br/exemplo2",
    )


@pytest.fixture
def filter_config() -> FilterConfig:
    """Configuração de filtro padrão."""
    return FilterConfig(
        estados=["SP"],
        modalidades=[6],
        meses_historico=1,
        keywords_core=[r"\bgeorreferenciamento\b", r"\bprad\b"],
        keywords_related=[r"\bpaisagismo\b"],
        blacklist=[r"\baquisicao de\b"],
        apenas_abertas=True,
    )


@pytest.fixture
def api_response_mock() -> dict:
    """Mock de resposta da API."""
    return {
        "data": [
            {
                "numeroControlePNCP": "12345678000190-1-000001/2024",
                "objetoCompra": "Contratação de georreferenciamento rural",
                "valorTotalEstimado": 50000.0,
                "modalidadeNome": "Pregão",
                "situacaoCompraLicitacaoNome": "Aberta",
                "dataPublicacaoPncp": "2024-01-15T10:00:00Z",
                "dataEncerramentoProposta": "2024-02-15T18:00:00Z",
                "unidadeOrgao": {
                    "nomeUnidade": "Prefeitura de Campinas",
                    "municipioNome": "Campinas",
                    "ufSigla": "SP",
                },
                "linkSistemaOrigem": "https://pncp.gov.br/exemplo",
            }
        ]
    }
