import os
import requests
import csv
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÕES ---
API_KEY = "gtk8nkEZ56lnttOtlBtpd2PuO1XGmbMX"
BASE_URL = "https://api.ui.com/ea" # URL da API oficial do Site Manager
DIRETORIO_BASE = "RELATORIO SITES"

headers = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}

class PDFRelatorio(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"Vorp SafeCore WIFI - Relatório de Auditoria", ln=True, align="C")
        self.set_font("Arial", "", 8)
        self.cell(0, 5, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
        self.ln(10)

def obter_sites():
    response = requests.get(f"{BASE_URL}/sites", headers=headers)
    return response.json().get('data', []) if response.status_code == 200 else []

def obter_dispositivos(site_id):
    response = requests.get(f"{BASE_URL}/sites/{site_id}/devices", headers=headers)
    return response.json().get('data', []) if response.status_code == 200 else []

def gerar_arquivos(site_name, dispositivos):
    nome_limpo = site_name.replace(" ", "_")
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # --- GERAR CSV ---
    arquivo_csv = os.path.join(DIRETORIO_BASE, f"{nome_limpo}_{timestamp}.csv")
    if dispositivos:
        colunas = dispositivos[0].keys()
        with open(arquivo_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colunas)
            writer.writeheader()
            writer.writerows(dispositivos)

    # --- GERAR PDF ---
    pdf = PDFRelatorio()
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, f"Site: {site_name}", ln=True)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 8, "Nome", 1, 0, "C", True)
    pdf.cell(40, 8, "Modelo", 1, 0, "C", True)
    pdf.cell(40, 8, "IP", 1, 0, "C", True)
    pdf.cell(30, 8, "Status", 1, 0, "C", True)
    pdf.cell(30, 8, "Versão", 1, 1, "C", True)

    pdf.set_font("Arial", "", 8)
    for d in dispositivos:
        pdf.cell(50, 7, str(d.get('name', 'S/N')), 1)
        pdf.cell(40, 7, str(d.get('model', 'N/A')), 1)
        pdf.cell(40, 7, str(d.get('ip', 'N/A')), 1)
        status = "Online" if d.get('state') == 1 else "Offline"
        pdf.cell(30, 7, status, 1)
        pdf.cell(30, 7, str(d.get('version', 'N/A')), 1, 1)

    arquivo_pdf = os.path.join(DIRETORIO_BASE, f"{nome_limpo}_{timestamp}.pdf")
    pdf.output(arquivo_pdf)

if __name__ == "__main__":
    if not os.path.exists(DIRETORIO_BASE):
        os.makedirs(DIRETORIO_BASE)

    print("🛰️ Conectando ao Site Manager da Ubiquiti...")
    sites = obter_sites()
    
    if not sites:
        print("❌ Nenhum site encontrado ou API Key inválida.")
    else:
        for site in sites:
            nome = site.get('name', 'Sem Nome')
            s_id = site.get('id')
            print(f"📊 Processando: {nome}...")
            
            dispositivos = obter_dispositivos(s_id)
            gerar_arquivos(nome, dispositivos)
        
        print(f"\n✅ Concluído! Arquivos salvos em: {DIRETORIO_BASE}")