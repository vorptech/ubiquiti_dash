# ======================================================================
# PROJETO: Vorp SafeCore & WIFI - NOC Monitor
# VERSÃO: 1.0 (Baseline Oficial)
# DATA: Março/2026
# DESCRIÇÃO: Dashboard em tempo real para API UniFi.
# FUNCIONALIDADES: Ordenação inteligente (Offline no topo), Animação de 
# alerta (Pisca até 48h), Uptime, IP Público, Múltiplas VLANs (IP Local), 
# Status de Backup, Alerta de Atualização e Monitoramento Multi-WAN.
# ======================================================================

import streamlit as st
import requests
import time
import os
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO ---
API_KEY = "gtk8nkEZ56lnttOtlBtpd2PuO1XGmbMX"
BASE_URL = "https://api.ui.com/v1"

st.set_page_config(page_title="Vorp SafeCore & WIFI", layout="wide")

# --- ESTILO CSS MODERNO E ANIMAÇÕES ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0E1117; }
    
    @keyframes pulso-vermelho {
        0% { box-shadow: 0 0 10px rgba(255, 75, 75, 0.3); border-color: #FF4B4B; }
        50% { box-shadow: 0 0 25px rgba(255, 0, 0, 0.8); border-color: #FF0000; }
        100% { box-shadow: 0 0 10px rgba(255, 75, 75, 0.3); border-color: #FF4B4B; }
    }

    .host-card {
        background-color: #161A23;
        border-radius: 10px;
        padding: 16px; 
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s;
        border: 1px solid #2D3342;
        display: flex;
        flex-direction: column;
        height: 290px; 
        overflow: hidden; 
    }
    .host-card:hover { transform: translateY(-2px); }
    
    .online-card { border-top: 4px solid #00E676; }
    
    .offline-card-pisca { 
        border: 2px solid #FF4B4B; 
        animation: pulso-vermelho 1.5s infinite; 
    }
    
    .offline-card-estatico {
        border: 2px solid #FF4B4B;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.1);
        opacity: 0.85; 
    }

    .host-name {
        color: #FFFFFF; font-size: 17px; font-weight: 600; margin-bottom: 8px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
    }
    .badge { padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: bold; }
    .badge-offline { background-color: rgba(255, 75, 75, 0.15); color: #FF4B4B; border: 1px solid rgba(255, 75, 75, 0.4); }
    .badge-online { background-color: rgba(0, 230, 118, 0.15); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.4); }
    
    .host-info { color: #A0AEC0; font-size: 12px; margin-top: 12px; line-height: 1.5; }
    .hw-name { font-size: 11px; color: #8A9BB2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
    
    .tags-container { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; }
    .mini-tag { background-color: #2D3342; padding: 3px 6px; border-radius: 4px; font-size: 10px; color: #C5D0E6; }
    .tag-update { background-color: rgba(59, 130, 246, 0.2); border: 1px solid #3B82F6; color: #3B82F6; }

    .wan-container { margin-top: auto; }
    
    .wan-box {
        margin-top: 6px;
        padding: 4px 8px; 
        background-color: #1E2330;
        border-radius: 4px;
        font-size: 11px; 
        color: #C5D0E6;
        border-left: 3px solid #3B82F6;
    }
    .wan-offline { border-left: 3px solid #EF4444; color: #EF4444; }
    
    .main-title {
        font-size: 38px; font-weight: 800;
        background: -webkit-linear-gradient(#4facfe, #00f2fe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0px; margin-top: -10px;
    }
    
    .logo-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 100%;
    }
    
    .stProgress > div > div > div > div {
        background-color: #00E676;
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

def formatar_data(data_iso, apenas_data=False):
    if not data_iso:
        return ""
    try:
        data_limpa = data_iso.replace('Z', '').split('.')[0]
        dt_utc = datetime.strptime(data_limpa, "%Y-%m-%dT%H:%M:%S")
        dt_brt = dt_utc - timedelta(hours=3)
        if apenas_data:
            return dt_brt.strftime("%d/%m/%y")
        return dt_brt.strftime("%d/%m/%y às %H:%M")
    except:
        return ""

def calcular_horas_offline(data_iso):
    if not data_iso:
        return 999 
    try:
        data_limpa = data_iso.replace('Z', '').split('.')[0]
        dt_utc = datetime.strptime(data_limpa, "%Y-%m-%dT%H:%M:%S")
        tempo_offline = datetime.utcnow() - dt_utc
        return tempo_offline.total_seconds() / 3600 
    except:
        return 999

def calcular_uptime(data_iso):
    if not data_iso:
        return "N/D"
    try:
        data_limpa = data_iso.replace('Z', '').split('.')[0]
        dt_utc = datetime.strptime(data_limpa, "%Y-%m-%dT%H:%M:%S")
        tempo_online = datetime.utcnow() - dt_utc
        
        dias = tempo_online.days
        horas = tempo_online.seconds // 3600
        minutos = (tempo_online.seconds % 3600) // 60
        
        if dias > 0:
            return f"{dias}d {horas}h"
        elif horas > 0:
            return f"{horas}h {minutos}m"
        else:
            return f"{minutos}m"
    except:
        return "N/D"

# --- CABEÇALHO ---
col_titulo, col_logo = st.columns([10, 1.5]) 

with col_titulo:
    st.markdown("<h1 class='main-title'>Vorp SafeCore & WIFI</h1>", unsafe_allow_html=True)
    st.caption(f"NOC Monitor | Última sincronização: {time.strftime('%H:%M:%S')}")
    placeholder_progresso = st.empty()

with col_logo:
    caminho_logo = "c:/PROJETO_VORP/logo.png"
    if os.path.exists(caminho_logo):
        st.image(caminho_logo, use_container_width=True)
    else:
        st.markdown("<div class='logo-container'><h1 style='margin: 0;'>🌐</h1></div>", unsafe_allow_html=True)

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
        
        ips_reportados = estado.get('ipAddrs', [])
        redes_locais = []
        for ip in ips_reportados:
            if "." in ip and ip != ip_publico and not ip.startswith("169.254") and ip not in redes_locais:
                redes_locais.append(ip)
        
        if redes_locais:
            vlans_str = ", ".join(redes_locais)
        else:
            vlans_str = estado.get('ip', 'N/D')
        
        versao = estado.get('version', 'Desconhecida')
        hardware = estado.get('hardware', {}).get('name', 'UniFi OS Console')
        
        backup_raw = host.get('latestBackupTime')
        backup_str = formatar_data(backup_raw, apenas_data=True)
        texto_backup = f"💾 BKP: {backup_str}" if backup_str else "💾 Sem Backup"
        
        fw_update = estado.get('firmwareUpdate', {}).get('latestAvailableVersion')
        tem_update = fw_update is not None
        
        ultima_mudanca_raw = host.get('lastConnectionStateChange')
        data_queda = formatar_data(ultima_mudanca_raw)
        horas_offline = calcular_horas_offline(ultima_mudanca_raw)
        
        is_online = str(status_raw).lower() in ['connected', 'online']
        
        tags_html = f"<div class='tags-container'>"
        tags_html += f"<span class='mini-tag'>{texto_backup}</span>"
        if tem_update:
            tags_html += "<span class='mini-tag tag-update' title='Firmware desatualizado'>⬆️ Update Pendente</span>"
        tags_html += "</div>"
        
        wans = estado.get('wans', [])
        wan_html = ""
        
        if not is_online:
             wan_html = f"<div class='wan-box wan-offline'>🔴 <b>OFFLINE</b><br>🕒 Caiu em: {data_queda}</div>"
        elif not wans:
             wan_html = "<div class='wan-box'>🔌 Informação WAN Indisponível</div>"
        else:
            for wan in wans:
                is_plugged = wan.get('plugged', False)
                wan_ip = wan.get('ipv4', 'Sem IP')
                tipo_wan = wan.get('type', 'WAN')
                interface = wan.get('interface', '')
                
                nome_link = f"{tipo_wan} ({interface})" if interface else tipo_wan

                if is_plugged:
                    wan_html += f"<div class='wan-box'>🟢 <b>{nome_link}</b>: {wan_ip}</div>"
                else:
                    wan_html += f"<div class='wan-box wan-offline'>🔴 <b>{nome_link}</b>: Desconectado</div>"

        if is_online:
            card_class = "host-card online-card"
            badge_class = "badge badge-online"
            status_text = "CONNECTED"
            icon = "🟢"
            uptime_str = calcular_uptime(ultima_mudanca_raw)
            html_do_status = f'<span class="{badge_class}">{icon} {status_text}</span><span style="font-size: 11px; color: #10B981; font-weight: bold; margin-left: 8px;" title="Tempo em atividade (Uptime)">⏱️ Up: {uptime_str}</span>'
        else:
            badge_class = "badge badge-offline"
            status_text = "DISCONNECTED"
            icon = "🔴"
            html_do_status = f'<span class="{badge_class}">{icon} {status_text}</span>'
            
            if horas_offline <= 48:
                card_class = "host-card offline-card-pisca"
            else:
                card_class = "host-card offline-card-estatico"

        card_html = f"""
        <div class="{card_class}">
            <div>
                <div class="host-name" title="{nome}">{nome}</div>
                {html_do_status}
                <div class="host-info">
                    🌐 <b>IP Público:</b> {ip_publico}<br>
                    <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{vlans_str}">
                        🏠 <b>Redes (VLANs):</b> {vlans_str}
                    </div>
                    <span class="hw-name" title="{hardware}">⚙️ <b>{hardware}</b></span>
                    <span>🔄 <b>Versão:</b> v{versao}</span>
                </div>
                {tags_html}
            </div>
            <div class="wan-container">
                {wan_html}
            </div>
        </div>
        """
        
        with cols[i % 4]:
            st.markdown(card_html, unsafe_allow_html=True)

else:
    st.error("Sem dados da API. Verifique a sua chave ou ligação.")

TEMPO_REFRESH = 60
barra_animada = placeholder_progresso.progress(0, text="A aguardar próxima atualização...")

for percentual in range(100):
    time.sleep(TEMPO_REFRESH / 100.0)
    segundos_restantes = TEMPO_REFRESH - int((percentual / 100.0) * TEMPO_REFRESH)
    texto_barra = f"Próxima atualização em {segundos_restantes} segundos..."
    barra_animada.progress(percentual + 1, text=texto_barra)

st.rerun()