# CLAUDE.md - ubiquiti_dash

## Sobre o projeto
Dashboard de visualização de dispositivos Ubiquiti.
Projeto Python rodando na VPS Hostinger via Docker.

## Estrutura
- `main.py` - entrada principal
- `dashboard_vorp_oficial.py` - dashboard principal
- `dashboard_vorp_oficial2.py` - versão 2 do dashboard
- `dashboard_vorp_v1.py` - versão 1 do dashboard
- `procura_id_ubiquiti.py` - busca de IDs Ubiquiti
- `relatorio_sites.py` - relatório de sites
- `requirements.txt` - dependências Python
- `Dockerfile` - configuração do container
- `docker-compose.yml` - orquestração Docker

## Ambiente
- VPS Hostinger com Docker
- Container: claude-code (node:20-slim)
- Workspace: /workspace/ubiquiti_dash
- GitHub: git@github.com:vorptech/ubiquiti_dash.git

## Comandos importantes
```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o projeto
python main.py
```

## Regras para o Claude
- A cada alteração no projeto, executar o auto_sync.sh para subir ao GitHub
- Manter o requirements.txt sempre atualizado
- Commitar com mensagens descritivas
- Nunca commitar arquivos .env ou credenciais

## Auto-sync GitHub
O script auto_sync.sh roda via cron a cada 5 minutos e faz push automático.
Para sync manual: `./auto_sync.sh`
