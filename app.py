# ======================================================================
# PROJETO: Vorp SafeCore & WIFI - NOC Monitor
# VERSÃO: 2.0 (Profissional)
# DESCRIÇÃO: Dashboard profissional de monitoramento Ubiquiti.
# API: Unifi Site Manager (https://api.ui.com)
# SEGURANÇA: API Key carregada via .env (nunca hardcoded)
# ======================================================================

import streamlit as st
import requests
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- Carrega variáveis de ambiente ---
load_dotenv()
API_KEY = os.getenv("UBIQUITI_API_KEY", "")
BASE_URL = "https://api.ui.com/v1"

# --- Configuração da página ---
st.set_page_config(
    page_title="Vorp NOC Monitor",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS: Tema escuro profissional ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background-color: #0B0F19;
}

/* Remove espaço em branco no topo */
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding-top: 1rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1F2937;
}

/* Animação offline recente (<48h) */
@keyframes pulso-vermelho {
    0%   { box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);  border-color: #EF4444; }
    50%  { box-shadow: 0 0 22px rgba(239, 68, 68, 0.85); border-color: #FF0000; }
    100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);  border-color: #EF4444; }
}

/* Cards — mesma estrutura de classes do v1 que o Streamlit renderiza corretamente */
.device-card {
    background-color: #161A23;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    transition: transform 0.2s;
    border: 1px solid #2D3342;
    display: flex;
    flex-direction: column;
    height: 315px;
    overflow: hidden;
}
.device-card:hover { transform: translateY(-2px); }

.card-online  { border-top: 4px solid #10B981; }

.card-offline-recente {
    border: 2px solid #EF4444;
    animation: pulso-vermelho 1.5s infinite;
}

.card-offline-antigo {
    border: 2px solid #7F1D1D;
    box-shadow: 0 0 8px rgba(239,68,68,0.1);
    opacity: 0.85;
}

.host-name {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    letter-spacing: 0.3px;
}

.badge { padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 700; }
.badge-online  { background: rgba(16,185,129,0.15); color: #10B981; border: 1px solid rgba(16,185,129,0.4); }
.badge-offline { background: rgba(239,68,68,0.15);  color: #EF4444; border: 1px solid rgba(239,68,68,0.4); }

.uptime-chip {
    display: inline-block;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    color: #10B981;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    margin-left: 6px;
}

.hw-name { font-size: 11px; color: #64748B; display: block; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.host-info { color: #A0AEC0; font-size: 12px; margin-top: 8px; line-height: 1.7; }

/* Tags */
.tags-container { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.mini-tag { background-color: #2D3342; padding: 3px 7px; border-radius: 5px; font-size: 10px; color: #C5D0E6; }
.tag-update { background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.4); color: #60A5FA; }
.tag-offline-time { background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.35); color: #F87171; }

/* WAN */
.wan-container { margin-top: auto; }
.wan-box {
    margin-top: 6px;
    padding: 5px 9px;
    background-color: #1E2330;
    border-radius: 5px;
    font-size: 11px;
    color: #C5D0E6;
    border-left: 3px solid #3B82F6;
}
.wan-offline { border-left-color: #EF4444; color: #F87171; }

/* Título principal */
.main-title {
    font-size: 34px;
    font-weight: 900;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
    margin: 0;
}
.subtitle {
    color: #475569;
    font-size: 13px;
    margin-top: 4px;
}

/* Métricas — botões clicáveis */
.metric-btn button {
    background: #111827 !important;
    border: 1px solid #1F2937 !important;
    border-radius: 10px !important;
    width: 100% !important;
    height: 110px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    color: inherit !important;
}
.metric-btn button:hover {
    background: #1F2937 !important;
    border-color: #4B5563 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
}
.metric-btn button p {
    margin: 0 !important;
    line-height: 1.2 !important;
    text-align: center !important;
}

/* Número grande no topo do botão */
.metric-btn button p:first-child {
    font-size: 48px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
}
/* Label pequeno embaixo */
.metric-btn button p:last-child {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.6px !important;
    text-transform: uppercase !important;
    color: #64748B !important;
    margin-top: 6px !important;
}

/* Cores por tipo */
.metric-total  button p:first-child { color: #60A5FA !important; }
.metric-online button p:first-child { color: #10B981 !important; }
.metric-offline button p:first-child { color: #EF4444 !important; }
.metric-alert  button p:first-child { color: #FBBF24 !important; }

/* Botão ativo (filtro selecionado) */
.metric-ativo button {
    border-color: #4B5563 !important;
    background: #1E2837 !important;
    box-shadow: inset 0 0 0 2px #374151 !important;
}

/* Barra de progresso */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #38BDF8, #818CF8);
}

/* Divisor */
hr { border-color: #1E293B !important; }

/* Alerta de API Key */
.api-warning {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 8px;
    padding: 16px;
    color: #FCA5A5;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Funções utilitárias
# ─────────────────────────────────────────────

def formatar_data_brt(data_iso: str, apenas_data: bool = False) -> str:
    if not data_iso:
        return ""
    try:
        data_limpa = data_iso.replace("Z", "").split(".")[0]
        dt_utc = datetime.strptime(data_limpa, "%Y-%m-%dT%H:%M:%S")
        dt_brt = dt_utc - timedelta(hours=3)
        if apenas_data:
            return dt_brt.strftime("%d/%m/%y")
        return dt_brt.strftime("%d/%m/%y %H:%M")
    except Exception:
        return ""


def calcular_horas_offline(data_iso: str) -> float:
    if not data_iso:
        return 9999.0
    try:
        data_limpa = data_iso.replace("Z", "").split(".")[0]
        dt_utc = datetime.strptime(data_limpa, "%Y-%m-%dT%H:%M:%S")
        return (datetime.utcnow() - dt_utc).total_seconds() / 3600
    except Exception:
        return 9999.0


def formatar_duracao(horas: float) -> str:
    if horas >= 9999:
        return "N/D"
    if horas < 1:
        mins = int(horas * 60)
        return f"{mins}m"
    if horas < 24:
        h = int(horas)
        m = int((horas - h) * 60)
        return f"{h}h {m}m"
    dias = int(horas // 24)
    h = int(horas % 24)
    return f"{dias}d {h}h"


def calcular_uptime(data_iso: str) -> str:
    if not data_iso:
        return "N/D"
    try:
        data_limpa = data_iso.replace("Z", "").split(".")[0]
        dt_utc = datetime.strptime(data_limpa, "%Y-%m-%dT%H:%M:%S")
        delta = datetime.utcnow() - dt_utc
        dias = delta.days
        horas = delta.seconds // 3600
        minutos = (delta.seconds % 3600) // 60
        if dias > 0:
            return f"{dias}d {horas}h"
        if horas > 0:
            return f"{horas}h {minutos}m"
        return f"{minutos}m"
    except Exception:
        return "N/D"


# ─────────────────────────────────────────────
# Chamadas à API
# ─────────────────────────────────────────────

@st.cache_data(ttl=55, show_spinner=False)
def buscar_hosts(api_key: str) -> list:
    if not api_key:
        return []
    headers = {"X-API-KEY": api_key, "Accept": "application/json"}
    try:
        resp = requests.get(f"{BASE_URL}/hosts", headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("data", [])
        return []
    except Exception:
        return []


# ─────────────────────────────────────────────
# Renderização de card de dispositivo
# ─────────────────────────────────────────────

def renderizar_card(host: dict, idx: int) -> str:
    estado = host.get("reportedState", {})
    nome = estado.get("name") or f"Dispositivo {idx + 1}"
    status_raw = str(estado.get("state", "")).lower()
    is_online = status_raw in ("connected", "online")

    ip_publico = host.get("ipAddress", "N/A") or "N/A"

    # IPs locais (VLANs)
    ips_reportados = estado.get("ipAddrs", [])
    locais = [
        ip for ip in ips_reportados
        if "." in ip
        and ip != ip_publico
        and not ip.startswith("169.254")
    ]
    redes_str = ", ".join(locais) if locais else (estado.get("ip") or "N/D")

    versao = estado.get("version", "N/D") or "N/D"
    hardware = (estado.get("hardware") or {}).get("name", "UniFi OS Console")

    # Backup
    backup_raw = host.get("latestBackupTime")
    backup_str = formatar_data_brt(backup_raw, apenas_data=True)
    texto_backup = f"💾 BKP: {backup_str}" if backup_str else "💾 Sem Backup"

    # Firmware update
    fw_update = (estado.get("firmwareUpdate") or {}).get("latestAvailableVersion")
    nova_versao = fw_update or ""

    # Tempo offline / uptime
    ultima_mudanca = host.get("lastConnectionStateChange")
    horas_offline = calcular_horas_offline(ultima_mudanca)
    data_queda = formatar_data_brt(ultima_mudanca)
    uptime_str = calcular_uptime(ultima_mudanca)

    # ── Classe do card ──
    if is_online:
        card_class = "device-card card-online"
    elif horas_offline <= 48:
        card_class = "device-card card-offline-recente"
    else:
        card_class = "device-card card-offline-antigo"

    # ── Badge + uptime ──
    if is_online:
        badge_html = f'<span class="badge badge-online">&#9679; ONLINE</span>'
        uptime_html = f'<span class="uptime-chip">&#9201; Up {uptime_str}</span>'
    else:
        badge_html = f'<span class="badge badge-offline">&#9679; OFFLINE</span>'
        uptime_html = ''

    # ── Tags ──
    tags_html = f'<span class="mini-tag">{texto_backup}</span>'
    if fw_update:
        tags_html += f'<span class="mini-tag tag-update">&#11014; FW {nova_versao}</span>'
    if not is_online and ultima_mudanca:
        tags_html += f'<span class="mini-tag tag-offline-time">&#128338; {formatar_duracao(horas_offline)} offline</span>'

    # ── WAN ──
    wans = estado.get("wans", [])
    if not is_online:
        wan_html = f'<div class="wan-box wan-offline">&#128308; <b>OFFLINE</b> &mdash; Caiu em {data_queda}</div>'
    elif not wans:
        wan_html = '<div class="wan-box">&#128268; WAN indispon&iacute;vel</div>'
    else:
        wan_html = ""
        for wan in wans:
            plugged = wan.get("plugged", False)
            wan_ip = wan.get("ipv4", "Sem IP") or "Sem IP"
            tipo = wan.get("type", "WAN") or "WAN"
            iface = wan.get("interface", "") or ""
            nome_link = f"{tipo} ({iface})" if iface else tipo
            if plugged:
                wan_html += f'<div class="wan-box">&#128994; <b>{nome_link}</b>: {wan_ip}</div>'
            else:
                wan_html += f'<div class="wan-box wan-offline">&#128308; <b>{nome_link}</b>: Desconectado</div>'

    card = (
        f'<div class="{card_class}">'
        f'<div class="host-name" title="{nome}">{nome}</div>'
        f'<div style="margin-bottom:6px;">{badge_html} {uptime_html}</div>'
        f'<span class="hw-name">&#9881; {hardware}</span>'
        f'<div class="host-info">'
        f'&#127760; <b>IP P&uacute;blico:</b> {ip_publico}<br>'
        f'<span title="{redes_str}" style="display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
        f'&#127968; <b>Redes/VLANs:</b> {redes_str}</span>'
        f'&#128260; <b>Firmware:</b> v{versao}'
        f'</div>'
        f'<div class="tags-container">{tags_html}</div>'
        f'<div class="wan-container">{wan_html}</div>'
        f'</div>'
    )
    return card


# ─────────────────────────────────────────────
# SIDEBAR — Filtros e configurações
# ─────────────────────────────────────────────

with st.sidebar:
    # Logo
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("### 🌐 Vorp NOC")

    st.markdown("---")
    st.markdown("### Filtros")

    filtro_busca = st.text_input(
        "Buscar por nome / cliente",
        placeholder="Ex: ClienteA, UDM-Pro...",
        help="Filtra por qualquer parte do nome do dispositivo",
    )

    filtro_offline = st.selectbox(
        "Tempo offline",
        options=[
            "Todos",
            "Última hora",
            "Últimas 24h",
            "Últimos 7 dias",
            "Mais de 7 dias",
        ],
        help="Filtra dispositivos offline pelo tempo fora do ar",
    )

    filtro_firmware = st.checkbox(
        "Somente com update de firmware pendente",
        value=False,
    )

    st.markdown("---")
    num_colunas = st.slider("Colunas na grade", min_value=1, max_value=6, value=5)
    st.markdown("---")
    st.caption("Vorp SafeCore & WIFI\nNOC Monitor v2.0")


# ─────────────────────────────────────────────
# Verificação da API Key
# ─────────────────────────────────────────────

if not API_KEY:
    st.markdown("""
    <div class="api-warning">
        <b>⚠️ API Key não configurada</b><br><br>
        Crie um arquivo <code>.env</code> na raiz do projeto com o conteúdo:<br>
        <code>UBIQUITI_API_KEY=sua_chave_aqui</code><br><br>
        A chave pode ser gerada em: <b>unifi.ui.com → Account → API</b>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────

col_titulo, col_sync = st.columns([8, 2])
with col_titulo:
    st.markdown("<h1 class='main-title'>Vorp SafeCore & WIFI</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='subtitle'>NOC Monitor &nbsp;|&nbsp; "
        f"Última sincronização: <b>{(datetime.utcnow() - timedelta(hours=3)).strftime('%H:%M:%S')}</b></p>",
        unsafe_allow_html=True,
    )
    placeholder_progresso = st.empty()

with col_sync:
    if st.button("🔄 Sincronizar agora", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Carrega dados
# ─────────────────────────────────────────────

with st.spinner("Consultando a API Ubiquiti..."):
    todos_hosts = buscar_hosts(API_KEY)


# ─────────────────────────────────────────────
# Aplica filtros
# ─────────────────────────────────────────────

def is_online_host(host: dict) -> bool:
    status = str(host.get("reportedState", {}).get("state", "")).lower()
    return status in ("connected", "online")


def tem_fw_update(host: dict) -> bool:
    fw = (host.get("reportedState") or {}).get("firmwareUpdate") or {}
    return bool(fw.get("latestAvailableVersion"))


# ─────────────────────────────────────────────
# Métricas clicáveis — filtro por botão
# ─────────────────────────────────────────────

total = len(todos_hosts)
online = sum(1 for h in todos_hosts if is_online_host(h))
offline = total - online
fw_alerts = sum(1 for h in todos_hosts if tem_fw_update(h))

if "filtro_btn" not in st.session_state:
    st.session_state.filtro_btn = "Todos"

filtro_btn_ativo = st.session_state.filtro_btn

m1, m2, m3, m4 = st.columns(4)

with m1:
    cls = "metric-btn metric-total" + (" metric-ativo" if filtro_btn_ativo == "Todos" else "")
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    if st.button(f"{total}\n\nTotal de Dispositivos", key="btn_total", use_container_width=True):
        st.session_state.filtro_btn = "Todos"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with m2:
    cls = "metric-btn metric-online" + (" metric-ativo" if filtro_btn_ativo == "Online" else "")
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    if st.button(f"{online}\n\nOnline", key="btn_online", use_container_width=True):
        st.session_state.filtro_btn = "Online"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with m3:
    cls = "metric-btn metric-offline" + (" metric-ativo" if filtro_btn_ativo == "Offline" else "")
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    if st.button(f"{offline}\n\nOffline", key="btn_offline", use_container_width=True):
        st.session_state.filtro_btn = "Offline"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with m4:
    cls = "metric-btn metric-alert" + (" metric-ativo" if filtro_btn_ativo == "Firmware" else "")
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    if st.button(f"{fw_alerts}\n\nUpdates Pendentes", key="btn_fw", use_container_width=True):
        st.session_state.filtro_btn = "Firmware"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Aplica filtros
# ─────────────────────────────────────────────

hosts_filtrados = list(todos_hosts)

# Filtro de busca por nome (sidebar)
if filtro_busca.strip():
    termo = filtro_busca.strip().lower()
    hosts_filtrados = [
        h for h in hosts_filtrados
        if termo in (h.get("reportedState", {}).get("name") or "").lower()
    ]

# Filtro de tempo offline (sidebar)
if filtro_offline != "Todos":
    def _horas(h):
        return calcular_horas_offline(h.get("lastConnectionStateChange"))

    if filtro_offline == "Última hora":
        hosts_filtrados = [h for h in hosts_filtrados if not is_online_host(h) and _horas(h) <= 1]
    elif filtro_offline == "Últimas 24h":
        hosts_filtrados = [h for h in hosts_filtrados if not is_online_host(h) and _horas(h) <= 24]
    elif filtro_offline == "Últimos 7 dias":
        hosts_filtrados = [h for h in hosts_filtrados if not is_online_host(h) and _horas(h) <= 168]
    elif filtro_offline == "Mais de 7 dias":
        hosts_filtrados = [h for h in hosts_filtrados if not is_online_host(h) and _horas(h) > 168]

# Filtro dos botões de métrica
if filtro_btn_ativo == "Online":
    hosts_filtrados = [h for h in hosts_filtrados if is_online_host(h)]
elif filtro_btn_ativo == "Offline":
    hosts_filtrados = [h for h in hosts_filtrados if not is_online_host(h)]
elif filtro_btn_ativo == "Firmware":
    hosts_filtrados = [h for h in hosts_filtrados if tem_fw_update(h)]

# Filtro de firmware do sidebar
if filtro_firmware:
    hosts_filtrados = [h for h in hosts_filtrados if tem_fw_update(h)]

# Ordenação: offline primeiro, depois por nome
hosts_filtrados.sort(
    key=lambda h: (
        is_online_host(h),
        (h.get("reportedState") or {}).get("name", "").lower(),
    )
)


# ─────────────────────────────────────────────
# Grade de cards
# ─────────────────────────────────────────────

if not todos_hosts:
    st.error(
        "Não foi possível obter dados da API. "
        "Verifique sua UBIQUITI_API_KEY no arquivo .env."
    )
elif not hosts_filtrados:
    st.info("Nenhum dispositivo corresponde aos filtros aplicados.")
else:
    colunas = st.columns(num_colunas)
    for i, host in enumerate(hosts_filtrados):
        with colunas[i % num_colunas]:
            st.markdown(renderizar_card(host, i), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Auto-refresh a cada 60 segundos
# ─────────────────────────────────────────────

TEMPO_REFRESH = 60
barra = placeholder_progresso.progress(0, text="Aguardando próxima atualização...")

for pct in range(100):
    time.sleep(TEMPO_REFRESH / 100.0)
    restante = TEMPO_REFRESH - int((pct / 100.0) * TEMPO_REFRESH)
    barra.progress(pct + 1, text=f"Próxima atualização em {restante}s...")

st.rerun()
