"""Configurações centralizadas do PNCP Scanner."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação via variáveis de ambiente."""

    # API
    pncp_base_url: str = Field(
        default="https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao",
        description="URL base da API PNCP",
    )
    api_timeout: int = Field(default=15, description="Timeout em segundos")
    page_size: int = Field(default=50, ge=1, le=500, description="Itens por página")
    max_pages: int = Field(default=10, ge=1, description="Máximo de páginas por query")
    request_delay: float = Field(default=0.05, ge=0, description="Delay entre requests")

    # Geocoding
    geolocator_user_agent: str = Field(default="pncp_scanner_v1")
    geocode_timeout: int = Field(default=2)

    # App
    app_name: str = Field(default="LicitaScan")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Retorna settings cacheadas."""
    return Settings()


# Estados brasileiros disponíveis
ESTADOS_BRASIL: dict[str, str] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Modalidades de licitação
MODALIDADES: dict[int, str] = {
    1: "Leilão",
    2: "Diálogo Competitivo",
    3: "Concurso",
    4: "Concorrência",
    5: "Concorrência Internacional",
    6: "Pregão",
    7: "Pré-qualificação",
    8: "Dispensa",
    9: "Inexigibilidade",
    10: "Manifestação de Interesse",
    12: "Credenciamento",
    13: "IRP",
}

# Keywords padrão para diferentes áreas
DEFAULT_KEYWORD_PRESETS: dict[str, dict[str, list[str]]] = {
    "Agronomia": {
        "core": [
            r"\bprad\b",
            r"\bplano de manejo\b",
            r"\bplano de arborizacao\b",
            r"\bprojeto de reflorestamento\b",
            r"\bcompensacao ambiental\b",
            r"\bsupressao vegetal\b",
            r"\bcadastro ambiental rural\b",
            r"\bgeorreferenciamento\b",
            r"\bcertificacao incra\b",
            r"\bsigef\b",
            r"\bccir\b",
            r"\blaudo agronomico\b",
            r"\blaudo de vegetacao\b",
            r"\blaudo arboreo\b",
            r"\blaudo fitossanitario\b",
            r"\binventario florestal\b",
            r"\binventario arboreo\b",
            r"\beia.?rima\b",
            r"\blicenciamento ambiental\b",
        ],
        "related": [
            r"\bpoda de arvore\b",
            r"\bpoda arbore\b",
            r"\bmanejo arboreo\b",
            r"\btratamento fitossanitario\b",
            r"\bviveiro de muda\b",
            r"\bpaisagismo\b",
            r"\birrigacao\b",
            r"\bdrenagem agricola\b",
            r"\bconsultoria ambiental\b",
        ],
    },
    "Tecnologia da Informação": {
        "core": [
            r"\bdesenvolvimento de software\b",
            r"\bdesenvolvimento de sistema\b",
            r"\bfabrica de software\b",
            r"\bsustentacao de sistema\b",
            r"\bmanutencao de sistema\b",
            r"\banalise de dados\b",
            r"\bbusiness intelligence\b",
            r"\bciencia de dados\b",
            r"\binteligencia artificial\b",
            r"\bmachine learning\b",
        ],
        "related": [
            r"\bsuporte tecnico\b",
            r"\binfra.?estrutura de ti\b",
            r"\bcloud computing\b",
            r"\bseguranca da informacao\b",
            r"\bconsultoria em ti\b",
        ],
    },
    "Engenharia Civil": {
        "core": [
            r"\bprojeto estrutural\b",
            r"\bconstrucao de\b",
            r"\breforma de\b",
            r"\bampliacao de\b",
            r"\bpavimentacao\b",
            r"\bobra de\b",
            r"\bfiscalizacao de obra\b",
        ],
        "related": [
            r"\blevantamento topografico\b",
            r"\btopografia\b",
            r"\bsondagem\b",
            r"\bterraplanagem\b",
        ],
    },
    "Personalizado": {
        "core": [],
        "related": [],
    },
}

# Blacklist padrão
DEFAULT_BLACKLIST: list[str] = [
    # Compras/Aquisições
    r"\baquisicao de\b",
    r"\bfornecimento de\b",
    r"\bcompra de\b",
    r"\bmaterial de\b",
    r"\bequipamento\b",
    r"\bveiculo\b",
    r"\bcaminhao\b",
    r"\btrator\b",
    r"\bmaquina\b",
    r"\bpneu\b",
    r"\bpeca\b",
    # Saúde
    r"\bmedico\b",
    r"\benfermagem\b",
    r"\bhospital\b",
    r"\bmedicamento\b",
    # Alimentação/Limpeza
    r"\bmerenda\b",
    r"\balimentacao escolar\b",
    r"\blimpeza\b",
    r"\bvigilancia\b",
    # Eventos
    r"\bshow\b",
    r"\bevento\b",
    r"\bpalco\b",
    r"\bcarnaval\b",
    # Transporte
    r"\blocacao de veiculo\b",
    r"\btransporte escolar\b",
    r"\btransporte de passageiro\b",
]
