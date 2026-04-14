import streamlit as st
import requests
import time

# --- CONFIGURAÇÃO ---
API_KEY = "gtk8nkEZ56lnttOtlBtpd2PuO1XGmbMX"
BASE_URL = "https://api.ui.com/v1"

st.set_page_config(page_title="Vorp SafeCore WIFI", layout="wide")

# --- ESTILO CSS MODERNO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0E1117; }
    
    .host-card {
        background-color: #161A23;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s;
        border: 1px solid #2D3342;
    }
    .host-card:hover { transform: translateY(-4px); }
    .offline-card { border: 2px solid #FF4B4B; box-shadow: 0 0 18px rgba(255, 75, 75, 0.25); }
    .online-card { border-top: 4px solid #00E676; }

    .host-name {
        color: #FFFFFF; font-size: 20px; font-weight: 600; margin-bottom: 12px;
    }
    .badge { padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
    .badge-offline { background-color: rgba(255, 75, 75, 0.15); color: #FF4B4B; border: 1px solid rgba(255, 75, 75, 0.4); }
    .badge-online { background-color: rgba(0, 230, 118, 0.15); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.4); }
    
    .host-info { color: #A0AEC0; font-size: 14px; margin-top: 18px; line-height: 1.7; }
    
    /* Estilo para os Links WAN */
    .wan-box {
        margin-top: 12px;
        padding: 8px;
        background-color: #1E2330;
        border-radius: 6px;
        font-size: 12px;
        color: #C5D0E6;
        border-left: 3px solid #3B82F6;
    }
    .wan-offline { border-left: 3px solid #EF4444; color: #EF4444; }
    
    .main-title {
        font-size: 42px; font-weight: 800;
        background: -webkit-linear-gradient(#4facfe, #00f2fe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px; margin-top: -30px;
    }
    </style>
""", unsafe_allow_html=True)

def buscar_hosts():
    headers = {"X-API-KEY": API_KEY, "Accept": "application/json"}
    try:
        response = requests.get(f"{BASE_URL}/hosts", headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except:
        return []

# --- CABEÇALHO ---
st.markdown("<h1 class='main-title'>🌐 Vorp SafeCore WIFI</h1>", unsafe_allow_html=True)
st.caption(f"NOC Monitor | Atualização em tempo real: {time.strftime('%H:%M:%S')}")
st.write("---")

hosts = buscar_hosts()

if hosts:
    hosts.sort(key=lambda h: str(h.get('reportedState', {}).get('state', '')).lower() == 'connected')

    cols = st.columns(4)
    for i, host in enumerate(hosts):
        estado = host.get('reportedState', {})
        nome = estado.get('name', f"Console {i+1}")
        status_raw = estado.get('state', 'offline')
        ip_publico = host.get('ipAddress', 'N/A')
        versao = estado.get('version', 'N/A')
        hardware = estado.get('hardware', {}).get('shortname', 'UniFi OS')
        
        # --- LÓGICA DE WANs ---
        wans = estado.get('wans', [])
        wan_html = ""
        
        if not wans and str(status_raw).lower() in ['connected', 'online']:
             wan_html = "<div class='wan-box'>🔌 Status WAN indisponível</div>"
        else:
            for idx, wan in enumerate(wans):
                # Checa se o cabo está conectado
                is_plugged = wan.get('plugged', False)
                wan_ip = wan.get('ipv4', 'N/A')
                tipo_wan = wan.get('type', f'WAN {idx+1}')
                
                if is_plugged:
                    wan_html += f"<div class='wan-box'>🟢 <b>{tipo_wan}</b>: {wan_ip}</div>"
                else:
                    wan_html += f"<div class='wan-box wan-offline'>🔴 <b>{tipo_wan}</b>: Cabo Desconectado</div>"

        is_online = str(status_raw).lower() in ['connected', 'online']
        card_class = "host-card online-card" if is_online else "host-card offline-card"
        badge_class = "badge badge-online" if is_online else "badge badge-offline"
        status_text = "CONNECTED" if is_online else "DISCONNECTED"
        icon = "🟢" if is_online else "🔴"

        card_html = f"""
        <div class="{card_class}">
            <div class="host-name">{nome}</div>
            <span class="{badge_class}">{icon} {status_text}</span>
            <div class="host-info">
                🌐 <b>IP Principal:</b> {ip_publico}<br>
                ⚙️ <b>{hardware}:</b> v{versao}
            </div>
            {wan_html}
        </div>
        """
        
        with cols[i % 4]:
            st.markdown(card_html, unsafe_allow_html=True)

else:
    st.error("Sem dados da API. Verifique sua chave.")

time.sleep(30)
st.rerun()