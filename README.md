# AAT - Automotive Assistance Tool

AI-driven Requirements Engineering Proof-of-Concept for automated requirements digitalization, matching, and traceability.

## Current Version: 1.3.1

## Change Log
- [x] **v1.3.1** (2026-01-16) - **Hotfix: PostgreSQL Dependency**
  - [x] Added psycopg2-binary to requirements.txt
  - [x] Added libpq-dev to Dockerfile for PostgreSQL support
  - [x] Fixed Docker deployment crash due to missing database driver
- [x] **v1.3.0** (2026-01-16) - **Authentication & RBAC Implementation**
  - [x] Full authentication system with login/logout
  - [x] Role-Based Access Control (Admin / Visitor)
  - [x] Database tables: app_user, app_role, app_user_role, app_session
  - [x] SHA256 password hashing with session management
  - [x] Login page (00_Login.py) and Admin panel (99_Admin.py)
  - [x] Authentication components: auth.py, session.py, security.py
  - [x] Default admin user: admin@aat.local / admin123
  - [x] Database scripts: db_create_user.py, db_read_users.py
- [x] **v1.2.0** (2026-01-16) - **Automated Deployment Testing**
  - [x] Added tag trigger to deploy_web.yaml workflow (v* pattern)
  - [x] Testing automated deployment on tag creation
  - [x] CI/CD improvements for version releases
- [x] **v1.1.0** (2026-01-16) - **Web Skeleton Refactor**
  - [x] Complete removal of old PDF extraction UI logic
  - [x] New multi-tab Streamlit structure with 9 pages (Dashboard, Status, DB Status, TableView, Matching, Trace, Impact, Reports, Chat)
  - [x] Chat Type A implementation: simple input/output interface with no history or DB logging
  - [x] Integrated Ollama Module v1.3.0 status monitoring (2026-01-11)
  - [x] Database now running on schema `work_aa` in DB `trading`
  - [x] Clean component architecture: `components/layout.py` and `components/utils.py`
  - [x] Minimal CSS styling in `static/css/app.css`
- [x] **v1.0.2** (2026-01-14) - **Web Version Bump**
  - [x] Testing CLAUDE.md workflow
  - [x] No functional changes to application
- [x] **v1.0.1** (2026-01-13) - **Stable Demo Version**
  - [x] AI Requirements Extractor with llava vision model
  - [x] Generic Customer ID system for privacy compliance
  - [x] Low temperature (0.1) for stable, non-hallucinating output
  - [x] PDF to image conversion with pdf2image (DPI: 150)
  - [x] Strict extraction prompts - AI only reports visible text
  - [x] Clean sidebar with Ollama status and Reset Session
  - [x] Markdown table output for requirements
- [x] **v0.5.0** (2026-01-13) - **Ollama Module + Performance Statistics**
  - [x] AI Monitor: Run # column, Algo, Model, Type, Total Time columns
  - [x] Performance Statistics dashboard: Initial Run Avg, Incremental Run Avg (The Gauss), Efficiency Gain
  - [x] Header badge: Ollama module version (v1.3.0) and current mode display
  - [x] AI Agent v1.3.0: run_number tracking, task_type logic (initial/incremental)
- [x] **v0.4.0** (2026-01-09) - **Multi-Node Resource Monitoring**
- [x] **v0.3.0** - Ollama Chat online
- [x] **v0.2.0** - Docker Migration & CI/CD Setup
- [x] **v0.1.0** - Initial project setup

## Features

### Web Interface Structure
The application now features a clean multi-tab Streamlit interface:

```bash
web/
 ├─ app.py                    # Main entry point with layout loader
 ├─ pages/
 │   ├─ 01_Dashboard.py       # System overview and key metrics
 │   ├─ 02_Status.py          # Agent and system status monitoring
 │   ├─ 03_DB_Status.py       # Database health and statistics
 │   ├─ 04_TableView.py       # Browse database tables
 │   ├─ 05_Matching.py        # Requirements matching interface
 │   ├─ 06_Trace.py           # Traceability analysis
 │   ├─ 07_Impact.py          # Git impact analysis
 │   ├─ 08_Reports.py         # Generate and view reports
 │   └─ 09_Chat.py            # AI chat interface (Type A)
 ├─ components/
 │   ├─ layout.py             # Header rendering and layout utilities
 │   └─ utils.py              # Chat and utility functions
 ├─ static/
 │   ├─ css/
 │   │   └─ app.css           # Minimal styling
 │   └─ img/
 └─ requirements.txt
```

### Chat Type A
- Simple question/answer interface
- Single input box for user questions
- Single output box for responses
- No conversation history
- No database logging
- Placeholder implementation ready for future integration

### Database Configuration
- **Database**: `trading`
- **Schema**: `work_aa`
- **Extensions**: pgvector enabled for embeddings
- All database access uses environment variables (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)

### Ollama Module Integration
- Integrated Ollama Module v1.3.0 (2026-01-11)
- Status monitoring for AI services
- Ready for embedding and matching operations

## System Architecture

### Central Dashboard (`hetzner-vm-1`)
- **IP**: `128.140.108.240`
- **Port**: `5000` (Bridge API)
- **Role**: Data aggregation and visualization

### AI Node (`Hetzner-OL-02`)
- **IP**: `168.119.122.36`
- **Service**: `hetzner-monitor.service`
- **Role**: System metrics collection

## Docker Deployment

The application requires `poppler-utils` for PDF processing:

```bash
# Build and run
docker build -t ai-requirements-extractor .
docker run -p 8501:8501 ai-requirements-extractor
```

## Release History

| Tag | Date | Description |
|-----|------|-------------|
| **v1.3.1** | 2026-01-16 | **Hotfix: PostgreSQL Dependency**. Fixed Docker deployment crash by adding psycopg2-binary and libpq-dev dependencies. |
| **v1.3.0** | 2026-01-16 | **Authentication & RBAC**. Full authentication system with login/logout, role-based access control (Admin/Visitor), session management, and admin panel. |
| **v1.2.0** | 2026-01-16 | **Automated Deployment Testing**. Added tag trigger to CI/CD workflow for automated deployments on version releases. |
| **v1.1.0** | 2026-01-16 | **Web Skeleton Refactor**. Complete removal of PDF extraction code, new 9-page structure, Chat Type A, Ollama Module v1.3.0 integration, database on work_aa schema. |
| **v1.0.2** | 2026-01-14 | **Web Version Bump**. Testing CLAUDE.md workflow, no functional changes. |
| **v1.0.1** | 2026-01-13 | **Stable Demo**. AI Requirements Extractor with generic Customer IDs, low temperature mode, strict extraction prompts. |
| **v0.5.0** | 2026-01-13 | **Ollama Module + Performance Stats**. UI improvements and efficiency tracking. |
| **v0.4.0** | 2026-01-09 | **Resource Monitoring**. Multi-node monitoring integration. |
| **v0.3.0** | 2026-01-09 | **Ollama Chat**. First LLM integration. |
| **v0.2.0** | 2026-01-09 | **Docker Build & Deploy**. CI/CD automation. |
| **v0.1.0** | 2026-01-08 | **Initial Layout**. Basic application structure. |

## Administration

### Monitor Logs
```bash
sudo journalctl -u hetzner-monitor -f
```
