"""PNCP Scanner - Interface Streamlit."""

import asyncio
from datetime import datetime

import streamlit as st

from src.config import (
    AREAS_DISPONIVEIS,
    DEFAULT_KEYWORD_PRESETS,
    ESTADOS_BRASIL,
    MODALIDADES,
)
from src.export.excel import ExcelExporter
from src.models.schemas import FilterConfig, ScanProgress, ScanResult
from src.services.scanner import Scanner

# =============================================================================
# Page Config
# =============================================================================
st.set_page_config(
    page_title="LicitaScan",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CSS Customizado
# =============================================================================
st.markdown("""
<style>
    /* Remove padding extra */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* Cards de métricas */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #eee;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }

    /* Cards de licitação */
    .lic-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #1e3a5f;
        transition: all 0.2s;
    }
    .lic-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateX(4px);
    }
    .lic-card.core {
        border-left-color: #28a745;
    }
    .lic-card.related {
        border-left-color: #17a2b8;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-core {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
    }
    .badge-related {
        background: linear-gradient(135deg, #17a2b8, #6f42c1);
        color: white;
    }

    /* Info boxes */
    .info-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #e9ecef;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Botão principal */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(30, 58, 95, 0.4);
    }

    /* Download buttons */
    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 500;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1e3a5f, #2d5a87);
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1e3a5f;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #888;
        font-size: 0.85rem;
        border-top: 1px solid #eee;
        margin-top: 3rem;
    }
    .footer a {
        color: #1e3a5f;
        text-decoration: none;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Session State
# =============================================================================
def init_session_state() -> None:
    """Inicializa session state."""
    # Keywords padrão (Agronomia e Meio Ambiente - simplificadas)
    default_core = """georreferenciamento
licenciamento ambiental
estudo de impacto
prad
plano de manejo
laudo ambiental
inventario florestal
outorga
meio ambiente"""

    default_related = """paisagismo
consultoria ambiental
gestao ambiental
projeto ambiental"""

    defaults = {
        "scan_result": None,
        "is_scanning": False,
        "stop_requested": False,
        "progress": ScanProgress(),
        "keywords_core_text": default_core,
        "keywords_related_text": default_related,
        "area_loaded": "Agronomia e Meio Ambiente",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# =============================================================================
# Components
# =============================================================================
def render_header() -> None:
    """Renderiza header principal."""
    st.markdown("""
        <div class="main-header">
            <h1>🔍 LicitaScan</h1>
            <p>Encontre licitações abertas no Portal Nacional de Contratações Públicas</p>
        </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str, icon: str = "") -> None:
    """Renderiza card de métrica."""
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{icon} {value}</div>
            <div class="metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)


def render_licitacao_card(lic) -> None:
    """Renderiza card de licitação."""
    badge_class = "badge-core" if lic.categoria == "core" else "badge-related"
    badge_text = "CORE" if lic.categoria == "core" else "RELACIONADO"
    card_class = "core" if lic.categoria == "core" else "related"

    valor_fmt = f"R$ {lic.valor_estimado:,.0f}".replace(",", ".")
    data_enc = lic.data_encerramento.strftime("%d/%m/%Y às %H:%M") if lic.data_encerramento else "Não informado"

    # Gerar link - usa link do sistema origem ou fallback para PNCP
    if lic.link and lic.link.strip():
        link_url = lic.link
        link_text = "Acessar edital →"
    else:
        # Fallback: link direto para o PNCP
        link_url = f"https://pncp.gov.br/app/editais/{lic.numero_pncp}"
        link_text = "Ver no PNCP →"

    st.markdown(f"""
        <div class="lic-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                <div>
                    <span class="badge {badge_class}">{badge_text}</span>
                    <span style="margin-left: 8px; color: #666; font-size: 0.85rem;">{lic.keyword_match}</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #1e3a5f;">{valor_fmt}</div>
                </div>
            </div>
            <div style="font-weight: 600; color: #333; margin-bottom: 0.5rem;">
                📍 {lic.municipio}/{lic.uf} — {lic.orgao}
            </div>
            <div style="color: #555; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0.75rem;">
                {lic.objeto[:250]}{"..." if len(lic.objeto) > 250 else ""}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; color: #888; font-size: 0.85rem;">
                <span>⏰ Encerra: {data_enc}</span>
                <a href="{link_url}" target="_blank" rel="noopener noreferrer" style="color: #1e3a5f; text-decoration: none; font-weight: 500;">
                    {link_text}
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Sidebar
# =============================================================================
def render_sidebar() -> FilterConfig | None:
    """Renderiza sidebar com configurações."""
    with st.sidebar:
        st.markdown("## ⚙️ Configurações")
        st.markdown("---")

        # Áreas de Atuação (preset para carregar keywords)
        st.markdown("### 📋 Carregar Preset")

        def carregar_preset():
            area = st.session_state.preset_selector
            preset = DEFAULT_KEYWORD_PRESETS[area]
            st.session_state.keywords_core_text = "\n".join(preset["core"])
            st.session_state.keywords_related_text = "\n".join(preset["related"])
            st.session_state.area_loaded = area

        st.selectbox(
            "Área",
            options=AREAS_DISPONIVEIS,
            index=AREAS_DISPONIVEIS.index(st.session_state.area_loaded) if st.session_state.area_loaded in AREAS_DISPONIVEIS else 0,
            label_visibility="collapsed",
            key="preset_selector",
            on_change=carregar_preset,
        )

        # Keywords editáveis
        st.markdown("### 🔑 Keywords Core")
        st.caption("Uma por linha (principais, alta prioridade)")
        st.text_area(
            "Core",
            height=200,
            placeholder="Digite suas keywords aqui\nUma por linha",
            label_visibility="collapsed",
            key="keywords_core_text",
        )

        st.markdown("### 🔗 Keywords Relacionadas")
        st.caption("Uma por linha (secundárias)")
        st.text_area(
            "Related",
            height=120,
            placeholder="Keywords relacionadas\nUma por linha",
            label_visibility="collapsed",
            key="keywords_related_text",
        )

        # Processar keywords
        keywords_core = [k.strip() for k in st.session_state.keywords_core_text.split("\n") if k.strip()]
        keywords_related = [k.strip() for k in st.session_state.keywords_related_text.split("\n") if k.strip()]

        if not keywords_core and not keywords_related:
            st.error("Adicione pelo menos uma keyword")
            return None

        st.caption(f"✅ {len(keywords_core)} core, {len(keywords_related)} relacionadas")

        # Estados
        st.markdown("### 🗺️ Estados")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Sudeste", use_container_width=True, type="secondary"):
                st.session_state["estados_sel"] = ["SP", "RJ", "MG", "ES"]
        with col2:
            if st.button("Sul", use_container_width=True, type="secondary"):
                st.session_state["estados_sel"] = ["PR", "SC", "RS"]
        with col3:
            if st.button("Todos", use_container_width=True, type="secondary"):
                st.session_state["estados_sel"] = list(ESTADOS_BRASIL.keys())

        estados_default = st.session_state.get("estados_sel", ["SP", "MG", "PR", "SC", "RS"])

        estados_selecionados = st.multiselect(
            "Selecione os estados",
            options=list(ESTADOS_BRASIL.keys()),
            default=estados_default,
            format_func=lambda x: f"{x} - {ESTADOS_BRASIL[x]}",
            label_visibility="collapsed",
        )

        if not estados_selecionados:
            st.error("Selecione pelo menos um estado")
            return None

        # Modalidades
        st.markdown("### 📑 Modalidades")
        modalidades_selecionadas = st.multiselect(
            "Modalidades",
            options=list(MODALIDADES.keys()),
            default=[4, 6, 8, 9],
            format_func=lambda x: MODALIDADES[x],
            label_visibility="collapsed",
        )

        if not modalidades_selecionadas:
            st.error("Selecione pelo menos uma modalidade")
            return None

        # Período
        st.markdown("### 📅 Período de Busca")
        meses = st.select_slider(
            "Meses",
            options=[1, 2, 3, 4, 5, 6],
            value=2,
            format_func=lambda x: f"{x} {'mês' if x == 1 else 'meses'}",
            label_visibility="collapsed",
        )

        # Filtros adicionais
        st.markdown("### 🔧 Filtros")
        apenas_abertas = st.toggle("Apenas licitações abertas", value=True, help="Mostra apenas licitações com prazo ainda não encerrado")

        # Resumo
        st.markdown("---")
        st.markdown("### 📊 Resumo da Busca")

        st.markdown(f"""
            <div class="info-box">
                <div>📍 <strong>{len(estados_selecionados)}</strong> estados</div>
                <div>📑 <strong>{len(modalidades_selecionadas)}</strong> modalidades</div>
                <div>📅 <strong>{meses}</strong> {'mês' if meses == 1 else 'meses'}</div>
                <div>🔑 <strong>{len(keywords_core)}</strong> keywords core</div>
                <div>🔗 <strong>{len(keywords_related)}</strong> keywords relacionadas</div>
            </div>
        """, unsafe_allow_html=True)

        return FilterConfig(
            estados=estados_selecionados,
            modalidades=modalidades_selecionadas,
            meses_historico=meses,
            keywords_core=keywords_core,
            keywords_related=keywords_related,
            apenas_abertas=apenas_abertas,
        )


# =============================================================================
# Main Content
# =============================================================================
def run_scan(config: FilterConfig) -> None:
    """Executa o scan com possibilidade de parar - atualiza a cada página."""
    import time as time_module
    from src.api.pncp_client import PNCPClient
    from src.filters.matcher import KeywordMatcher
    from src.config import get_settings
    from collections import Counter
    import httpx

    st.session_state.is_scanning = True
    st.session_state.stop_requested = False

    # Inicializar resultado parcial se não existir
    if "partial_result" not in st.session_state:
        st.session_state.partial_result = {
            "licitacoes": [],
            "total_varrido": 0,
            "keywords_count": Counter(),
            "erros": [],
            "inicio": time_module.time(),
            "estado_idx": 0,
            "modalidade_idx": 0,
            "intervalo_idx": 0,
            "pagina": 1,
        }

    partial = st.session_state.partial_result

    # UI de progresso
    st.markdown("### 🔄 Varredura em Andamento")

    # Info atual
    if partial["estado_idx"] < len(config.estados):
        uf_atual = config.estados[partial["estado_idx"]]
        mod_atual = config.modalidades[partial["modalidade_idx"]] if partial["modalidade_idx"] < len(config.modalidades) else "-"
        st.info(f"🔍 **{uf_atual}** | Modalidade **{mod_atual}** | Página **{partial['pagina']}**")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Processados", f"{partial['total_varrido']:,}")
    with col2:
        st.metric("Encontrados", len(partial['licitacoes']))
    with col3:
        tempo_decorrido = time_module.time() - partial["inicio"]
        st.metric("Tempo", f"{tempo_decorrido:.0f}s")
    with col4:
        if st.button("⏹️ PARAR", type="primary", use_container_width=True):
            st.session_state.stop_requested = True

    if st.session_state.stop_requested:
        # Parou - mostrar resultados parciais
        tempo_total = time_module.time() - partial["inicio"]
        licitacoes = partial["licitacoes"]
        licitacoes.sort(key=lambda x: x.score, reverse=True)

        st.session_state.scan_result = ScanResult(
            licitacoes=licitacoes,
            total_varrido=partial["total_varrido"],
            total_encontrado=len(licitacoes),
            total_abertas=sum(1 for lic in licitacoes if lic.is_aberta),
            keywords_contagem=dict(partial["keywords_count"]),
            tempo_execucao=round(tempo_total, 2),
            erros=partial["erros"],
        )
        st.session_state.is_scanning = False
        del st.session_state.partial_result
        st.rerun()
        return

    # Barra de progresso
    intervalos = PNCPClient.gerar_intervalos_mensais(config.meses_historico)
    total_combos = len(config.estados) * len(config.modalidades) * len(intervalos)
    current_combo = (
        partial["estado_idx"] * len(config.modalidades) * len(intervalos) +
        partial["modalidade_idx"] * len(intervalos) +
        partial["intervalo_idx"]
    )
    st.progress(min(current_combo / max(total_combos, 1), 1.0))

    # Verificar se terminou
    if partial["estado_idx"] >= len(config.estados):
        tempo_total = time_module.time() - partial["inicio"]
        licitacoes = partial["licitacoes"]
        licitacoes.sort(key=lambda x: x.score, reverse=True)

        st.session_state.scan_result = ScanResult(
            licitacoes=licitacoes,
            total_varrido=partial["total_varrido"],
            total_encontrado=len(licitacoes),
            total_abertas=sum(1 for lic in licitacoes if lic.is_aberta),
            keywords_contagem=dict(partial["keywords_count"]),
            tempo_execucao=round(tempo_total, 2),
            erros=partial["erros"],
        )
        st.session_state.is_scanning = False
        del st.session_state.partial_result
        st.rerun()
        return

    # Configuração
    matcher = KeywordMatcher(
        keywords_core=config.keywords_core,
        keywords_related=config.keywords_related,
    )
    settings = get_settings()

    # Dados atuais
    uf = config.estados[partial["estado_idx"]]
    cod_mod = config.modalidades[partial["modalidade_idx"]]
    data_ini, data_fim = intervalos[partial["intervalo_idx"]]
    pagina = partial["pagina"]

    # Buscar UMA página
    try:
        with httpx.Client(timeout=settings.api_timeout) as client:
            params = {
                "dataInicial": data_ini,
                "dataFinal": data_fim,
                "codigoModalidadeContratacao": cod_mod,
                "uf": uf,
                "tamanhoPagina": settings.page_size,
                "pagina": pagina,
            }
            response = client.get(settings.pncp_base_url, params=params)
            response.raise_for_status()
            resultado = response.json()

            itens = resultado.get("data", [])

            for item in itens:
                partial["total_varrido"] += 1

                # Parse manual do item
                unidade = item.get("unidadeOrgao", {})
                from src.models.schemas import Licitacao
                licitacao = Licitacao(
                    numero_pncp=item.get("numeroControlePNCP", ""),
                    objeto=item.get("objetoCompra", ""),
                    valor_estimado=item.get("valorTotalEstimado"),
                    modalidade=item.get("modalidadeNome", ""),
                    situacao=item.get("situacaoCompraLicitacaoNome", ""),
                    data_publicacao=item.get("dataPublicacaoPncp"),
                    data_encerramento=item.get("dataEncerramentoProposta"),
                    orgao=unidade.get("nomeUnidade", ""),
                    municipio=unidade.get("municipioNome", ""),
                    uf=unidade.get("ufSigla", ""),
                    link=item.get("linkSistemaOrigem", ""),
                )

                resultado_match = matcher.processar_licitacao(licitacao)
                if resultado_match is None:
                    continue
                if config.apenas_abertas and not resultado_match.is_aberta:
                    continue

                # Score
                score = 0
                if resultado_match.categoria == "core":
                    score += 30
                elif resultado_match.categoria == "related":
                    score += 15
                if resultado_match.is_aberta:
                    score += 40
                if resultado_match.valor_estimado > 100_000:
                    score += 20
                elif resultado_match.valor_estimado > 50_000:
                    score += 10
                resultado_match.score = score

                partial["licitacoes"].append(resultado_match)
                partial["keywords_count"][resultado_match.keyword_match] += 1

            # Avançar
            if len(itens) < settings.page_size:
                # Acabou essa combinação, vai para próxima
                partial["pagina"] = 1
                partial["intervalo_idx"] += 1
                if partial["intervalo_idx"] >= len(intervalos):
                    partial["intervalo_idx"] = 0
                    partial["modalidade_idx"] += 1
                    if partial["modalidade_idx"] >= len(config.modalidades):
                        partial["modalidade_idx"] = 0
                        partial["estado_idx"] += 1
            else:
                # Mais páginas
                partial["pagina"] += 1

    except Exception as e:
        partial["erros"].append(f"{uf}/{cod_mod}/pag{pagina}: {str(e)}")
        # Pula para próxima combinação em caso de erro
        partial["pagina"] = 1
        partial["intervalo_idx"] += 1
        if partial["intervalo_idx"] >= len(intervalos):
            partial["intervalo_idx"] = 0
            partial["modalidade_idx"] += 1
            if partial["modalidade_idx"] >= len(config.modalidades):
                partial["modalidade_idx"] = 0
                partial["estado_idx"] += 1

    # Continuar
    st.rerun()


def render_results() -> None:
    """Renderiza resultados."""
    result: ScanResult | None = st.session_state.scan_result

    if result is None:
        # Estado inicial - instruções
        st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 16px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🎯</div>
                <h3 style="color: #1e3a5f; margin-bottom: 1rem;">Pronto para encontrar oportunidades?</h3>
                <p style="color: #666; max-width: 500px; margin: 0 auto;">
                    Configure os filtros na barra lateral e clique em <strong>"Iniciar Varredura"</strong>
                    para buscar licitações abertas no PNCP.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Features
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="metric-container">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                    <div style="font-weight: 600; color: #1e3a5f;">Rápido</div>
                    <div style="font-size: 0.85rem; color: #666;">Busca assíncrona otimizada</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="metric-container">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                    <div style="font-weight: 600; color: #1e3a5f;">Preciso</div>
                    <div style="font-size: 0.85rem; color: #666;">Filtros inteligentes com regex</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div class="metric-container">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-weight: 600; color: #1e3a5f;">Exportável</div>
                    <div style="font-size: 0.85rem; color: #666;">Download em Excel e CSV</div>
                </div>
            """, unsafe_allow_html=True)
        return

    if result.total_encontrado == 0:
        st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #fff3cd; border-radius: 16px; margin: 2rem 0;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">😕</div>
                <h3 style="color: #856404;">Nenhuma licitação encontrada</h3>
                <p style="color: #856404;">Tente ajustar os filtros ou ampliar o período de busca.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    # Sucesso - Métricas
    st.markdown("### 📊 Resultados da Varredura")

    # Calcular core vs related
    total_core = sum(1 for l in result.licitacoes if l.categoria == "core")
    total_related = sum(1 for l in result.licitacoes if l.categoria == "related")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card(f"{result.total_varrido:,}", "Total Analisado", "📄")
    with col2:
        render_metric_card(f"{result.total_encontrado}", "Encontradas", "✅")
    with col3:
        render_metric_card(f"{total_core}", "Core", "🎯")
    with col4:
        render_metric_card(f"{total_related}", "Relacionadas", "🔗")
    with col5:
        render_metric_card(f"{result.tempo_execucao:.1f}s", "Tempo", "⏱️")

    st.markdown("<br>", unsafe_allow_html=True)

    # Downloads
    col1, col2, col3 = st.columns([1, 1, 2])

    exporter = ExcelExporter(result)

    with col1:
        excel_bytes = exporter.to_excel_bytes()
        st.download_button(
            label="📥 Download Excel",
            data=excel_bytes,
            file_name=exporter.gerar_nome_arquivo("xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )

    with col2:
        csv_bytes = exporter.to_csv_bytes()
        st.download_button(
            label="📥 Download CSV",
            data=csv_bytes,
            file_name=exporter.gerar_nome_arquivo("csv"),
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")

    # Tabs para organizar conteúdo
    tab1, tab2 = st.tabs(["📋 Licitações", "📈 Estatísticas"])

    with tab1:
        # Filtros inline
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_categoria = st.selectbox(
                "Categoria",
                ["Todas", "Core", "Relacionado"],
                key="filter_cat"
            )

        with col2:
            ufs_disponiveis = sorted(set(l.uf for l in result.licitacoes))
            filter_uf = st.selectbox("UF", ["Todas"] + ufs_disponiveis, key="filter_uf")

        with col3:
            filter_valor_min = st.number_input(
                "Valor mínimo (R$)",
                min_value=0,
                value=0,
                step=10000,
                format="%d",
                key="filter_valor"
            )

        # Aplicar filtros
        licitacoes_filtradas = result.licitacoes

        if filter_categoria != "Todas":
            cat = "core" if filter_categoria == "Core" else "related"
            licitacoes_filtradas = [l for l in licitacoes_filtradas if l.categoria == cat]

        if filter_uf != "Todas":
            licitacoes_filtradas = [l for l in licitacoes_filtradas if l.uf == filter_uf]

        if filter_valor_min > 0:
            licitacoes_filtradas = [l for l in licitacoes_filtradas if l.valor_estimado >= filter_valor_min]

        # Paginação
        items_per_page = 30
        total_items = len(licitacoes_filtradas)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        if "results_page" not in st.session_state:
            st.session_state.results_page = 1

        # Garantir página válida
        if st.session_state.results_page > total_pages:
            st.session_state.results_page = 1

        current_page = st.session_state.results_page
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)

        # Navegação
        if total_pages > 1:
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col1:
                if st.button("⬅️ Anterior", disabled=(current_page <= 1), use_container_width=True):
                    st.session_state.results_page -= 1
                    st.rerun()
            with nav_col2:
                st.markdown(f"<div style='text-align: center; padding: 8px;'>Página **{current_page}** de **{total_pages}** ({total_items} resultados)</div>", unsafe_allow_html=True)
            with nav_col3:
                if st.button("Próximo ➡️", disabled=(current_page >= total_pages), use_container_width=True):
                    st.session_state.results_page += 1
                    st.rerun()
        else:
            st.caption(f"{total_items} resultados")

        # Cards da página atual
        for lic in licitacoes_filtradas[start_idx:end_idx]:
            render_licitacao_card(lic)

    with tab2:
        # Estatísticas
        if result.keywords_contagem:
            st.markdown("#### 🏷️ Keywords Mais Frequentes")

            keywords_sorted = sorted(
                result.keywords_contagem.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            # Criar gráfico simples
            for kw, count in keywords_sorted:
                pct = (count / result.total_encontrado) * 100
                st.markdown(f"""
                    <div style="margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-weight: 500;">{kw}</span>
                            <span style="color: #666;">{count} ({pct:.0f}%)</span>
                        </div>
                        <div style="background: #e9ecef; border-radius: 4px; height: 8px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #1e3a5f, #2d5a87); width: {pct}%; height: 100%;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Por UF
        st.markdown("#### 🗺️ Distribuição por Estado")
        uf_count = {}
        for lic in result.licitacoes:
            uf_count[lic.uf] = uf_count.get(lic.uf, 0) + 1

        uf_sorted = sorted(uf_count.items(), key=lambda x: x[1], reverse=True)

        cols = st.columns(min(len(uf_sorted), 6))
        for idx, (uf, count) in enumerate(uf_sorted[:6]):
            with cols[idx]:
                st.metric(uf, count)


def render_footer() -> None:
    """Renderiza footer."""
    st.markdown("""
        <div class="footer">
            <p>
                <strong>LicitaScan v1.0.0</strong><br>
                Dados obtidos do <a href="https://pncp.gov.br" target="_blank">Portal Nacional de Contratações Públicas</a>
            </p>
        </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Main
# =============================================================================
def main() -> None:
    """Entry point."""
    render_header()

    config = render_sidebar()

    if config:
        if st.session_state.is_scanning:
            # Continuar scan em andamento
            run_scan(config)
        else:
            # Botão para iniciar
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🚀 Iniciar Varredura",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.scan_result = None  # Limpar resultado anterior
                    run_scan(config)

    if not st.session_state.is_scanning:
        render_results()
        render_footer()


if __name__ == "__main__":
    main()
