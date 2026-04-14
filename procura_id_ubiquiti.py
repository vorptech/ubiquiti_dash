import requests

# Substitua pela sua chave que você já tem
API_KEY = "gtk8nkEZ56lnttOtlBtpd2PuO1XGmbMX" 

headers = {
    "Accept": "application/json",
    "X-API-KEY": API_KEY
}

try:
    response = requests.get("https://api.ui.com/v1/organizations", headers=headers)
    if response.status_code == 200:
        orgs = response.json().get('data', [])
        print("\n--- ORGANIZAÇÕES ENCONTRADAS ---")
        for org in orgs:
            print(f"NOME: {org['name']}")
            print(f"ORG_ID: {org['id']}")
            print("-" * 30)
    else:
        print(f"Erro na API: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Erro de conexão: {e}")

input("\nAperte Enter para fechar...")