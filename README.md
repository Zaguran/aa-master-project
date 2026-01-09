# Automotive Assistance Tool (AAT)

Projekt pro správu kvality a monitorování automotive projektů.

## 🚀 Aktuální stav (Change Log)
- [x] **v0.1.0** - Inicializace projektu, základní Streamlit layout
- [x] **v0.2.0** (2026-01-09) - **Docker Migration & CI/CD Setup**
  - [x] Migrace z lokálního spouštění na Docker kontejnerizaci
  - [x] Nastavení `docker-compose.yml` s automatickým restartem
  - [x] Oprava Docker kontextu pro přístup k `requirements.txt`
  - [x] Implementace GitHub Actions pro automatický deploy na Hetzner VPS
  - [x] Vyřešení konfliktů portu 8501 (automatické ukončení visících Python procesů)
  - [x] Funkční verze dostupná na iPhonu, notebooku i VM
## Aktuální stav (v0.3.2)
- **Framework:** Streamlit (běžící v Dockeru)
- **AI Engine:** Ollama (Llama 3.1 8B)
- **Síťování:** Režim `host` (přímý přístup ke službám serveru)  

## 🏗️ Architektura Nasazení (v0.2.0)
1. **Frontend/Backend**: Streamlit aplikace běžící v Dockeru.
2. **Kontejner**: Python 3.11-slim (minimalizovaná velikost obrazu).
3. **Port**: `8501` mapovaný 1:1 na hostitelský systém.
4. **CI/CD**: GitHub Actions komunikující přes SSH s Hetzner VPS.

## 🏷️ Release History & Tags

| Tag | Datum | Popis změn |
| :--- | :--- | :--- |
| **v0.3.0** | 2026-01-09 | **Ollama Chat online**. První chat s Ollamou. |
| **v0.2.0** | 2026-01-09 | **Docker Build & Deploy**. První stabilní verze běžící v izolovaném kontejneru s automatickým deployem. |
| **v0.1.0** | 2026-01-08 | **Initial Layout**. Základní struktura aplikace a dashboardu. |

## 🛠️ Administrace (Build Process)

### Jak vytvořit nový release tag:
1. `git add .`
2. `git commit -m "popis tvé změny"`
3. `git tag -a v0.2.1 -m "Krátký popis verze"`
4. `git push origin v0.2.1`



# Restart celého stacku
cd ~/master-project
docker compose down
docker compose up -d --build

## Instalace a spuštění
1. Ujistěte se, že na hostitelském serveru běží Ollama:
   ```bash
   ollama serve
   ollama pull llama3.1:8b