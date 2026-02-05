"""Lógica de matching de keywords e filtragem."""

import re
import unicodedata
from dataclasses import dataclass
from re import Pattern

from src.models.schemas import KeywordCategory, Licitacao


@dataclass
class MatchResult:
    """Resultado de um match."""

    matched: bool
    category: KeywordCategory | None = None
    keyword: str | None = None
    pattern: str | None = None


class KeywordMatcher:
    """Matcher de keywords com suporte a regex."""

    def __init__(
        self,
        keywords_core: list[str] | None = None,
        keywords_related: list[str] | None = None,
    ) -> None:
        self._core_patterns: list[tuple[Pattern, str]] = []
        self._related_patterns: list[tuple[Pattern, str]] = []

        if keywords_core:
            self._compile_keywords(keywords_core, KeywordCategory.CORE)
        if keywords_related:
            self._compile_keywords(keywords_related, KeywordCategory.RELATED)

    def _compile_keywords(self, patterns: list[str], category: KeywordCategory) -> None:
        """Compila patterns de keywords."""
        target = (
            self._core_patterns
            if category == KeywordCategory.CORE
            else self._related_patterns
        )

        for pattern in patterns:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                label = self._pattern_to_label(pattern)
                target.append((compiled, label))
            except re.error:
                continue

    @staticmethod
    def _pattern_to_label(pattern: str) -> str:
        """Converte pattern regex em label legível."""
        label = pattern.replace(r"\b", "").replace(r"\s+", " ")
        label = re.sub(r"[\\.*+?^${}()|[\]]", "", label)
        return label.strip().title()

    @staticmethod
    def normalizar_texto(texto: str | None) -> str:
        """Remove acentos e converte para minúsculas."""
        if not texto:
            return ""
        normalized = unicodedata.normalize("NFD", texto)
        return normalized.encode("ascii", "ignore").decode("utf-8").lower()

    def match(self, texto: str) -> MatchResult:
        """Tenta match de keywords no texto."""
        texto_norm = self.normalizar_texto(texto)

        # Tenta core primeiro (prioridade)
        for pattern, label in self._core_patterns:
            if pattern.search(texto_norm):
                return MatchResult(
                    matched=True,
                    category=KeywordCategory.CORE,
                    keyword=label,
                    pattern=pattern.pattern,
                )

        # Depois tenta related
        for pattern, label in self._related_patterns:
            if pattern.search(texto_norm):
                return MatchResult(
                    matched=True,
                    category=KeywordCategory.RELATED,
                    keyword=label,
                    pattern=pattern.pattern,
                )

        return MatchResult(matched=False)

    def processar_licitacao(self, licitacao: Licitacao) -> Licitacao | None:
        """Processa licitação aplicando filtros."""
        result = self.match(licitacao.objeto)

        if not result.matched:
            return None

        # Atualiza campos da licitação
        licitacao.categoria = result.category
        licitacao.keyword_match = result.keyword
        licitacao.is_aberta = licitacao.verificar_aberta()

        return licitacao

    def adicionar_keyword(self, pattern: str, category: KeywordCategory) -> bool:
        """Adiciona keyword dinamicamente."""
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            label = self._pattern_to_label(pattern)

            if category == KeywordCategory.CORE:
                self._core_patterns.append((compiled, label))
            else:
                self._related_patterns.append((compiled, label))

            return True
        except re.error:
            return False

    @property
    def total_patterns(self) -> dict[str, int]:
        """Retorna contagem de patterns."""
        return {
            "core": len(self._core_patterns),
            "related": len(self._related_patterns),
        }
