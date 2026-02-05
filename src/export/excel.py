"""Exportação de dados para Excel."""

import io
import re
from datetime import datetime

import pandas as pd

from src.models.schemas import ScanResult


class ExcelExporter:
    """Exportador de resultados para Excel."""

    COLUMNS_ORDER = [
        "score",
        "categoria",
        "keyword_match",
        "municipio",
        "uf",
        "valor_estimado",
        "objeto",
        "orgao",
        "modalidade",
        "data_encerramento",
        "link",
        "numero_pncp",
    ]

    COLUMN_LABELS = {
        "score": "Score",
        "categoria": "Categoria",
        "keyword_match": "Keyword",
        "municipio": "Município",
        "uf": "UF",
        "valor_estimado": "Valor Estimado",
        "objeto": "Objeto",
        "orgao": "Órgão",
        "modalidade": "Modalidade",
        "data_encerramento": "Encerramento",
        "link": "Link",
        "numero_pncp": "Nº PNCP",
    }

    def __init__(self, result: ScanResult) -> None:
        self.result = result
        self._df: pd.DataFrame | None = None

    @staticmethod
    def _limpar_texto(texto: str | None) -> str:
        """Remove caracteres inválidos para Excel."""
        if not isinstance(texto, str):
            return texto if texto is not None else ""
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", texto)

    def _to_dataframe(self) -> pd.DataFrame:
        """Converte licitações para DataFrame."""
        if self._df is not None:
            return self._df

        data = []
        for lic in self.result.licitacoes:
            # Fallback para link do PNCP se não tiver link original
            link = lic.link.strip() if lic.link else ""
            if not link and lic.numero_pncp:
                link = f"https://pncp.gov.br/app/editais/{lic.numero_pncp}"

            row = {
                "score": lic.score,
                "categoria": "Core" if lic.categoria == "core" else "Relacionado",
                "keyword_match": lic.keyword_match,
                "municipio": lic.municipio,
                "uf": lic.uf,
                "valor_estimado": lic.valor_estimado,
                "objeto": self._limpar_texto(lic.objeto),
                "orgao": self._limpar_texto(lic.orgao),
                "modalidade": lic.modalidade,
                "data_encerramento": lic.data_encerramento,
                "link": link,
                "numero_pncp": lic.numero_pncp,
            }
            data.append(row)

        df = pd.DataFrame(data)

        # Reordenar colunas
        cols_exist = [c for c in self.COLUMNS_ORDER if c in df.columns]
        self._df = df[cols_exist]

        return self._df

    def to_excel_bytes(self) -> bytes:
        """Gera Excel em bytes (para download)."""
        df = self._to_dataframe()

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book

            # Formatos
            fmt_header = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#1F4E79",
                    "font_color": "white",
                    "border": 1,
                    "align": "center",
                }
            )
            fmt_money = workbook.add_format(
                {
                    "num_format": "R$ #,##0.00",
                    "border": 1,
                }
            )
            fmt_date = workbook.add_format(
                {
                    "num_format": "dd/mm/yyyy hh:mm",
                    "border": 1,
                }
            )
            fmt_link = workbook.add_format(
                {
                    "font_color": "blue",
                    "underline": True,
                }
            )

            # Escrever dados
            df.to_excel(
                writer,
                sheet_name="Licitações",
                index=False,
                startrow=1,
                header=False,
            )

            ws = writer.sheets["Licitações"]

            # Headers
            for col_num, col_name in enumerate(df.columns):
                label = self.COLUMN_LABELS.get(col_name, col_name)
                ws.write(0, col_num, label, fmt_header)

            # Configurar colunas
            for col_num, col_name in enumerate(df.columns):
                if col_name == "valor_estimado":
                    ws.set_column(col_num, col_num, 15, fmt_money)
                elif col_name == "data_encerramento":
                    ws.set_column(col_num, col_num, 18, fmt_date)
                elif col_name == "objeto":
                    ws.set_column(col_num, col_num, 60)
                elif col_name == "orgao":
                    ws.set_column(col_num, col_num, 40)
                elif col_name == "link":
                    ws.set_column(col_num, col_num, 30, fmt_link)
                else:
                    ws.set_column(col_num, col_num, 12)

            # Autofilter
            ws.autofilter(0, 0, len(df), len(df.columns) - 1)

            # Freeze panes
            ws.freeze_panes(1, 0)

        output.seek(0)
        return output.getvalue()

    def to_csv_bytes(self) -> bytes:
        """Gera CSV em bytes."""
        df = self._to_dataframe()
        return df.to_csv(index=False).encode("utf-8-sig")

    def gerar_nome_arquivo(self, extensao: str = "xlsx") -> str:
        """Gera nome de arquivo com timestamp."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"pncp_licitacoes_{ts}.{extensao}"
