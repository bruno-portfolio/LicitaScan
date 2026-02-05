"""Schemas Pydantic para validação de dados."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class KeywordCategory(str, Enum):
    """Categoria de match de keyword."""

    CORE = "core"
    RELATED = "related"


class Licitacao(BaseModel):
    """Modelo de uma licitação do PNCP."""

    numero_pncp: str = Field(..., description="Número de controle PNCP")
    objeto: str = Field(..., description="Descrição do objeto")
    valor_estimado: float = Field(default=0.0, ge=0)
    modalidade: str = Field(default="")
    situacao: str = Field(default="")
    data_publicacao: datetime | None = None
    data_encerramento: datetime | None = None
    orgao: str = Field(default="")
    municipio: str = Field(default="")
    uf: str = Field(default="", max_length=2)
    link: str = Field(default="")

    # Campos calculados pelo scanner
    categoria: KeywordCategory | None = None
    keyword_match: str | None = None
    is_aberta: bool = False
    score: int = Field(default=0, ge=0)

    @field_validator("data_publicacao", "data_encerramento", mode="before")
    @classmethod
    def parse_datetime(cls, v: str | datetime | None) -> datetime | None:
        """Parse datetime de string ISO."""
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt.replace(tzinfo=None)
        except (ValueError, AttributeError):
            return None

    @field_validator("valor_estimado", mode="before")
    @classmethod
    def parse_valor(cls, v: float | str | None) -> float:
        """Parse valor para float."""
        if v is None:
            return 0.0
        if isinstance(v, int | float):
            return float(v)
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    @field_validator("link", "objeto", "modalidade", "situacao", "orgao", "municipio", "uf", "numero_pncp", mode="before")
    @classmethod
    def parse_string(cls, v: str | None) -> str:
        """Converte None para string vazia."""
        if v is None:
            return ""
        return str(v)

    def verificar_aberta(self) -> bool:
        """Verifica se a licitação ainda está aberta."""
        if not self.data_encerramento:
            return False
        return self.data_encerramento >= datetime.now()

    class Config:
        use_enum_values = True


class FilterConfig(BaseModel):
    """Configuração de filtros para o scanner."""

    estados: list[str] = Field(default_factory=list, description="UFs para buscar")
    modalidades: list[int] = Field(
        default_factory=lambda: [4, 6, 8, 9],
        description="Códigos das modalidades",
    )
    meses_historico: int = Field(
        default=1, ge=1, le=12, description="Meses para buscar"
    )
    keywords_core: list[str] = Field(
        default_factory=list, description="Regex keywords principais"
    )
    keywords_related: list[str] = Field(
        default_factory=list, description="Regex keywords relacionadas"
    )
    apenas_abertas: bool = Field(
        default=True, description="Filtrar apenas licitações abertas"
    )

    @field_validator("estados", mode="before")
    @classmethod
    def uppercase_estados(cls, v: list[str]) -> list[str]:
        """Garante UFs em maiúsculo."""
        if isinstance(v, list):
            return [s.upper() for s in v]
        return v


class ScanResult(BaseModel):
    """Resultado de uma varredura."""

    licitacoes: list[Licitacao] = Field(default_factory=list)
    total_varrido: int = Field(default=0, ge=0)
    total_encontrado: int = Field(default=0, ge=0)
    total_abertas: int = Field(default=0, ge=0)
    keywords_contagem: dict[str, int] = Field(default_factory=dict)
    tempo_execucao: float = Field(default=0.0, ge=0)
    erros: list[str] = Field(default_factory=list)

    @property
    def taxa_match(self) -> float:
        """Taxa de match sobre total varrido."""
        if self.total_varrido == 0:
            return 0.0
        return (self.total_encontrado / self.total_varrido) * 100


class ScanProgress(BaseModel):
    """Progresso atual do scan."""

    estado_atual: str = ""
    modalidade_atual: str = ""
    pagina_atual: int = 0
    total_processado: int = 0
    total_matches: int = 0
    percentual: float = 0.0
    status: str = "idle"  # idle, running, completed, error
