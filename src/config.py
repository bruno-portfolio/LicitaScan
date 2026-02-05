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
    page_size: int = Field(default=50, ge=1, le=50, description="Itens por página (max 50 na API)")
    max_pages: int = Field(default=100, ge=1, description="Máximo de páginas por query")
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

# Keywords padrão para diferentes áreas (simplificadas)
DEFAULT_KEYWORD_PRESETS: dict[str, dict[str, list[str]]] = {
    "Agronomia e Meio Ambiente": {
        "core": [
            "georreferenciamento",
            "licenciamento ambiental",
            "estudo de impacto",
            "prad",
            "plano de manejo",
            "inventario florestal",
            "outorga",
        ],
        "related": [
            "meio ambiente",
            "consultoria ambiental",
            "laudo ambiental",
        ],
    },
    "Tecnologia da Informação": {
        "core": [
            "desenvolvimento de software",
            "desenvolvimento de sistema",
            "fabrica de software",
            "analise de dados",
            "inteligencia artificial",
        ],
        "related": [
            "suporte tecnico",
            "consultoria em ti",
            "seguranca da informacao",
        ],
    },
    "Engenharia Civil": {
        "core": [
            "projeto estrutural",
            "projeto executivo",
            "projeto basico",
            "fiscalizacao de obra",
            "pavimentacao",
        ],
        "related": [
            "levantamento topografico",
            "topografia",
            "orcamento de obra",
        ],
    },
    "Engenharia Elétrica": {
        "core": [
            "projeto eletrico",
            "instalacao eletrica",
            "iluminacao publica",
            "energia solar",
            "energia fotovoltaica",
        ],
        "related": [
            "manutencao eletrica",
            "eficiencia energetica",
            "subestacao",
        ],
    },
    "Arquitetura e Urbanismo": {
        "core": [
            "projeto arquitetonico",
            "projeto urbanistico",
            "plano diretor",
            "patrimonio historico",
            "design de interiores",
        ],
        "related": [
            "paisagismo",
            "planejamento urbano",
            "acessibilidade",
        ],
    },
    "Contabilidade e Finanças": {
        "core": [
            "auditoria",
            "servicos contabeis",
            "consultoria contabil",
            "pericia contabil",
            "controladoria",
        ],
        "related": [
            "assessoria contabil",
            "gestao financeira",
            "planejamento tributario",
        ],
    },
    "Consultoria e Gestão": {
        "core": [
            "consultoria empresarial",
            "planejamento estrategico",
            "gestao de processos",
            "gestao de projetos",
            "gestao da qualidade",
        ],
        "related": [
            "diagnostico organizacional",
            "treinamento",
            "capacitacao",
        ],
    },
    "Comunicação e Marketing": {
        "core": [
            "agencia de publicidade",
            "marketing digital",
            "comunicacao social",
            "assessoria de imprensa",
            "identidade visual",
        ],
        "related": [
            "design grafico",
            "producao audiovisual",
            "redes sociais",
        ],
    },
    "Jurídico": {
        "core": [
            "assessoria juridica",
            "consultoria juridica",
            "servicos advocaticios",
            "parecer juridico",
            "defesa judicial",
        ],
        "related": [
            "licitacoes e contratos",
            "direito administrativo",
            "contencioso",
        ],
    },
    "Saúde e Segurança do Trabalho": {
        "core": [
            "pcmso",
            "pgr",
            "ltcat",
            "medicina do trabalho",
            "seguranca do trabalho",
        ],
        "related": [
            "laudo ergonomico",
            "saude ocupacional",
            "exame admissional",
        ],
    },
    "Educação e Treinamento": {
        "core": [
            "curso de capacitacao",
            "treinamento corporativo",
            "educacao corporativa",
            "ensino a distancia",
            "formacao profissional",
        ],
        "related": [
            "plataforma de ensino",
            "workshop",
            "seminario",
        ],
    },
    "Engenharia de Produção": {
        "core": [
            "gestao da producao",
            "lean manufacturing",
            "six sigma",
            "logistica",
            "melhoria continua",
        ],
        "related": [
            "processos industriais",
            "automacao",
            "cadeia de suprimentos",
        ],
    },
    "Saneamento e Recursos Hídricos": {
        "core": [
            "projeto de saneamento",
            "tratamento de agua",
            "tratamento de esgoto",
            "recursos hidricos",
            "estudo hidrologico",
        ],
        "related": [
            "drenagem",
            "abastecimento",
            "outorga",
        ],
    },
    "Transporte e Mobilidade": {
        "core": [
            "estudo de trafego",
            "mobilidade urbana",
            "plano de mobilidade",
            "sinalizacao viaria",
            "projeto viario",
        ],
        "related": [
            "transporte publico",
            "gestao de frota",
            "ciclovias",
        ],
    },
    "Pesquisa e Desenvolvimento": {
        "core": [
            "pesquisa cientifica",
            "pesquisa e desenvolvimento",
            "inovacao tecnologica",
            "estudo de viabilidade",
            "prototipo",
        ],
        "related": [
            "estudo tecnico",
            "levantamento de dados",
            "diagnostico",
        ],
    },
}

# Lista de áreas disponíveis (ordenada)
AREAS_DISPONIVEIS: list[str] = sorted(DEFAULT_KEYWORD_PRESETS)

