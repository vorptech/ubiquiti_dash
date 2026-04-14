# CLAUDE.md - Vorp NOC Monitor (ubiquiti_dash)

## Sobre o projeto
Dashboard profissional de monitoramento de dispositivos Ubiquiti em tempo real.
Consome a API do **Unifi Site Manager** (`https://api.ui.com`).
Desenvolvido com Python + Streamlit, rodando na VPS Hostinger via Docker.

## Arquivos principais
| Arquivo | Descrição |
|---|---|
| `app.py` | Entrada principal — dashboard profissional v2.0 |
| `.env` | Credenciais (NUNCA commitar — ver .gitignore) |
| `.env.example` | Template de variáveis de ambiente (comittável) |
| `requirements.txt` | Dependências Python |
| `Dockerfile` | Imagem Docker (python:3.11-slim) |
| `docker-compose.yml` | Orquestração Docker com healthcheck |
| `.gitignore` | Proteção de arquivos sensíveis |
| `logo.png` | Logo da Vorp (exibida no sidebar) |
| `auto_sync.sh` | Script de sincronização automática com GitHub |

## Arquivos legados (não usar em produção)
- `dashboard_vorp_v1.py` — versão 1 (API key hardcoded)
- `dashboard_vorp_oficial.py` — versão oficial anterior
- `dashboard_vorp_oficial2.py` — segunda versão anterior
- `relatorio_sites.py` — geração de relatórios em PDF/CSV
- `procura_id_ubiquiti.py` — busca de IDs de organizações

## Ambiente
- VPS Hostinger com Docker
- GitHub: git@github.com:vorptech/ubiquiti_dash.git
- Porta da aplicação: **8501**

## Variáveis de ambiente (.env)
```env
UBIQUITI_API_KEY=sua_chave_aqui
```
Gere a chave em: **unifi.ui.com → Account → API Keys**

## Comandos importantes
```bash
# Desenvolvimento local
pip install -r requirements.txt
streamlit run app.py

# Docker (produção)
docker-compose up -d --build

# Ver logs
docker-compose logs -f dashboard

# Parar
docker-compose down

# Sync manual com GitHub
./auto_sync.sh
```

## API Ubiquiti Site Manager
| Endpoint | Descrição |
|---|---|
| `GET /v1/hosts` | Lista todos os consoles/hosts |
| `GET /v1/organizations` | Lista organizações |
| `GET /ea/sites` | Lista sites |
| `GET /ea/sites/{id}/devices` | Dispositivos de um site |

**Auth:** Header `X-API-KEY: <sua_chave>`

## Funcionalidades do app.py (v2.0)
- Status online/offline com indicador visual por cor
- IP público e IPs locais (VLANs)
- Status de cada link WAN (plugado/desconectado + IP)
- Versão de firmware + alerta de update pendente
- Uptime (online) ou tempo offline com formatação humana
- Borda vermelha pulsante para dispositivos offline < 48h
- Auto-refresh a cada 60 segundos com barra de progresso
- Sidebar com filtros: busca por nome, status, tempo offline, firmware
- Métricas de resumo: total, online, offline, updates pendentes
- Botão de sincronização manual
- Suporte a logo.png no sidebar

## Regras para o Claude
- **Nunca** commitar `.env` ou qualquer arquivo com credenciais
- A cada alteração, executar `./auto_sync.sh` para subir ao GitHub
- Manter `requirements.txt` atualizado
- Usar `app.py` como ponto de entrada (não os arquivos legados)
- Commitar com mensagens descritivas em português

## Auto-sync GitHub
O script `auto_sync.sh` roda via cron a cada 5 minutos e faz push automático.
Para sync manual: `./auto_sync.sh`
