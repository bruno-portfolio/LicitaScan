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

# Keywords padrão para diferentes áreas
DEFAULT_KEYWORD_PRESETS: dict[str, dict[str, list[str]]] = {
    "Agronomia e Meio Ambiente": {
        "core": [
            r"prad",
            r"plano de manejo",
            r"plano de arboriza",
            r"reflorestamento",
            r"compensa..o ambiental",
            r"supress.o vegetal",
            r"cadastro ambiental",
            r"georreferencia",
            r"certifica..o incra",
            r"\bsigef\b",
            r"\bccir\b",
            r"\bcar\b",
            r"laudo.*agron",
            r"laudo.*vegeta",
            r"laudo.*arbor",
            r"laudo.*fitossanit",
            r"inventario.*florest",
            r"inventario.*arbor",
            r"eia.?rima",
            r"licenciamento ambiental",
            r"estudo de impacto",
            r"recupera..o de area",
            r"area degradada",
            r"monitoramento ambiental",
            r"outorga",
            r"meio ambiente",
        ],
        "related": [
            r"poda.*arvor",
            r"poda.*arbor",
            r"manejo.*arbor",
            r"fitossanit",
            r"viveiro.*muda",
            r"paisagismo",
            r"irriga..o",
            r"drenagem",
            r"consultoria ambiental",
            r"gestao ambiental",
            r"servico.*ambiental",
            r"projeto.*ambiental",
            r"relatorio ambiental",
            r"diagnostico ambiental",
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
            r"\bdesenvolvimento web\b",
            r"\bdesenvolvimento mobile\b",
            r"\baplicativo\b",
            r"\bsistema de gestao\b",
            r"\berp\b",
        ],
        "related": [
            r"\bsuporte tecnico\b",
            r"\binfra.?estrutura de ti\b",
            r"\bcloud computing\b",
            r"\bseguranca da informacao\b",
            r"\bconsultoria em ti\b",
            r"\bredes\b",
            r"\bdata center\b",
            r"\bbackup\b",
            r"\bvirtualizacao\b",
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
            r"\bprojeto arquitetonico\b",
            r"\bprojeto executivo\b",
            r"\bprojeto basico\b",
        ],
        "related": [
            r"\blevantamento topografico\b",
            r"\btopografia\b",
            r"\bsondagem\b",
            r"\bterraplanagem\b",
            r"\borcamento de obra\b",
            r"\bplanilha orcamentaria\b",
        ],
    },
    "Engenharia Elétrica": {
        "core": [
            r"\bprojeto eletrico\b",
            r"\binstalacao eletrica\b",
            r"\brede eletrica\b",
            r"\bsubestacao\b",
            r"\biluminacao publica\b",
            r"\beficiencia energetica\b",
            r"\benergia solar\b",
            r"\benergia fotovoltaica\b",
            r"\bspda\b",
            r"\bpara.?raio\b",
        ],
        "related": [
            r"\bmanutencao eletrica\b",
            r"\bquadro eletrico\b",
            r"\btransformador\b",
            r"\bgerador\b",
            r"\bnobreak\b",
        ],
    },
    "Arquitetura e Urbanismo": {
        "core": [
            r"\bprojeto arquitetonico\b",
            r"\bprojeto urbanistico\b",
            r"\bplano diretor\b",
            r"\bestudo urbanistico\b",
            r"\bprojeto de interiores\b",
            r"\brestauracao\b",
            r"\bpatrimonio historico\b",
            r"\bdesign de interiores\b",
        ],
        "related": [
            r"\bpaisagismo\b",
            r"\bplanejamento urbano\b",
            r"\bmobiliario urbano\b",
            r"\bacessibilidade\b",
        ],
    },
    "Contabilidade e Finanças": {
        "core": [
            r"\bauditoria\b",
            r"\bcontabilidade\b",
            r"\bservicos contabeis\b",
            r"\bconsultoria contabil\b",
            r"\bpericia contabil\b",
            r"\bgestao financeira\b",
            r"\bplanejamento tributario\b",
            r"\bcontroladoria\b",
        ],
        "related": [
            r"\bassessoria contabil\b",
            r"\bbalanco\b",
            r"\bdemonstracao financeira\b",
            r"\bfiscal\b",
        ],
    },
    "Consultoria e Gestão": {
        "core": [
            r"\bconsultoria empresarial\b",
            r"\bconsultoria em gestao\b",
            r"\bplanejamento estrategico\b",
            r"\bdiagnostico organizacional\b",
            r"\bgestao de processos\b",
            r"\bgestao de projetos\b",
            r"\bgestao da qualidade\b",
            r"\biso 9001\b",
        ],
        "related": [
            r"\btreinamento\b",
            r"\bcapacitacao\b",
            r"\bconsultoria\b",
            r"\bassessoria\b",
        ],
    },
    "Comunicação e Marketing": {
        "core": [
            r"\bagencia de publicidade\b",
            r"\bmarketing digital\b",
            r"\bcomunicacao social\b",
            r"\bassessoria de imprensa\b",
            r"\bproducao de conteudo\b",
            r"\bredes sociais\b",
            r"\bbranding\b",
            r"\bidentidade visual\b",
        ],
        "related": [
            r"\bdesign grafico\b",
            r"\bvideo institucional\b",
            r"\bfotografia\b",
            r"\bproducao audiovisual\b",
        ],
    },
    "Jurídico": {
        "core": [
            r"\bassessoria juridica\b",
            r"\bconsultoria juridica\b",
            r"\bservicos advocaticios\b",
            r"\badvocacia\b",
            r"\bparecer juridico\b",
            r"\bdefesa judicial\b",
            r"\bcontencioso\b",
        ],
        "related": [
            r"\blicitacoes e contratos\b",
            r"\bdireito administrativo\b",
            r"\bdireito trabalhista\b",
        ],
    },
    "Saúde e Segurança do Trabalho": {
        "core": [
            r"\bpcmso\b",
            r"\bppra\b",
            r"\bpgr\b",
            r"\bltcat\b",
            r"\blaudo ergonomico\b",
            r"\bmedicina do trabalho\b",
            r"\bseguranca do trabalho\b",
            r"\bsaude ocupacional\b",
            r"\bexame admissional\b",
            r"\bexame periodico\b",
        ],
        "related": [
            r"\bepi\b",
            r"\bcipa\b",
            r"\bbrigada de incendio\b",
            r"\bnr.?\d+\b",
        ],
    },
    "Educação e Treinamento": {
        "core": [
            r"\bcurso de capacitacao\b",
            r"\btreinamento corporativo\b",
            r"\beducacao corporativa\b",
            r"\bensino a distancia\b",
            r"\bead\b",
            r"\bplataforma de ensino\b",
            r"\bcurso tecnico\b",
            r"\bformacao profissional\b",
        ],
        "related": [
            r"\bpalestra\b",
            r"\bworkshop\b",
            r"\bseminario\b",
            r"\bcurso\b",
        ],
    },
    "Engenharia de Produção": {
        "core": [
            r"\bgestao da producao\b",
            r"\blean manufacturing\b",
            r"\bsix sigma\b",
            r"\bgestao da cadeia de suprimentos\b",
            r"\blogistica\b",
            r"\bplanejamento e controle\b",
            r"\bmelhoria continua\b",
        ],
        "related": [
            r"\bprocessos industriais\b",
            r"\bautomacao\b",
            r"\bindustria\b",
        ],
    },
    "Saneamento e Recursos Hídricos": {
        "core": [
            r"\bprojeto de saneamento\b",
            r"\btratamento de agua\b",
            r"\btratamento de esgoto\b",
            r"\brede de agua\b",
            r"\brede de esgoto\b",
            r"\bdrenagem\b",
            r"\brecursos hidricos\b",
            r"\boutorga\b",
            r"\bestudo hidrologico\b",
        ],
        "related": [
            r"\bpoco artesiano\b",
            r"\breservatorio\b",
            r"\babastecimento\b",
        ],
    },
    "Transporte e Mobilidade": {
        "core": [
            r"\bestudo de trafego\b",
            r"\bmobilidade urbana\b",
            r"\bplano de mobilidade\b",
            r"\bsinalizacao viaria\b",
            r"\bprojeto viario\b",
            r"\btransporte publico\b",
            r"\bgestao de frota\b",
        ],
        "related": [
            r"\bestacionamento\b",
            r"\bciclovias\b",
            r"\bpedestres\b",
        ],
    },
    "Pesquisa e Desenvolvimento": {
        "core": [
            r"\bpesquisa cientifica\b",
            r"\bpesquisa e desenvolvimento\b",
            r"\bp&d\b",
            r"\binovacao tecnologica\b",
            r"\bestudo de viabilidade\b",
            r"\bprototipo\b",
        ],
        "related": [
            r"\bestudo tecnico\b",
            r"\blevantamento de dados\b",
            r"\bdiagnostico\b",
        ],
    },
}

# Lista de áreas disponíveis (ordenada)
AREAS_DISPONIVEIS: list[str] = sorted(
    [k for k in DEFAULT_KEYWORD_PRESETS.keys()]
)

