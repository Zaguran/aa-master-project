# AAT - Automotive Assistance Tool

AI-driven Requirements Engineering Proof-of-Concept for automated requirements digitalization, matching, and traceability.

## Current Version: 1.6.0

**Status:** ✅ **All Agents Active** - Active Development

---

## 🚀 Quick Start - Deployment

### Architecture Overview

```
LINUX 1 (128.140.108.240)          LINUX 2 (168.119.122.36)
├─ TimescaleDB (5432)              ├─ Ollama LLM (11434)
├─ Docker Agents:                  ├─ Docker Containers:
│  └─ aat-monitor-db               │  ├─ aat-web-container (8501)
│                                  │  └─ aat-monitor-ollama
└─ Path: /root/master-project      └─ Path: /root/master-project
```

### Automated Deploy via GitHub Actions

**Triggers:**
- Push to `main` branch
- Changes in `web/**`, `agents/**`, or workflow files

**Workflows:**
- `.github/workflows/deploy-linux1.yaml` → Deploy agents to Linux 1
- `.github/workflows/deploy-linux2.yaml` → Deploy web + monitor to Linux 2

**Process:**
1. Push code: `git push origin main`
2. GitHub Actions automatically:
   - SSH to servers
   - Generate `.env` from secrets
   - Git pull latest code
   - Build Docker containers
   - Start services
3. Monitor in **Actions** tab (green ✅ = success)

### GitHub Secrets Required

```
LINUX_1_IP=128.140.108.240
LINUX_2_IP=168.119.122.36
SSH_KEY_L1=<private_key_linux1>
SSH_KEY_L2=<private_key_linux2>
DB_NAME=trading
DB_USER=trading_user
DB_PASSWORD=<secure_password>
DB_PORT=5432
```

### Manual Deploy (Emergency)

**Linux 1:**
```bash
ssh root@128.140.108.240
cd /root/master-project
git pull origin main
docker compose -f docker-compose.agents.yml up -d --build
docker logs aat-monitor-db
```

**Linux 2:**
```bash
ssh root@168.119.122.36
cd /root/master-project
git pull origin main
docker compose up -d --build
docker logs aat-web-container
```

### Access Web UI

- **URL:** http://168.119.122.36:8501
- **Login:** Use credentials from database
- **Status:** View agent heartbeats in "Status" page

---

## 📊 Current Implementation Status

### ✅ Completed (v1.6.0):
- [x] All 11 computation agents running in daemon loop mode
- [x] CPU/RAM resource monitoring in agent heartbeat
- [x] Visual resource bars in Status dashboard
- [x] Agent scaffolds ready for implementation
- [x] Multi-server Docker deployment (Linux 1 + Linux 2)
- [x] GitHub Actions automated deploy workflows
- [x] Web UI (Streamlit) with RBAC authentication
- [x] Session management (1 hour timeout)
- [x] Agent heartbeat monitoring system
- [x] Chat interface with Ollama LLM

### 🚧 In Progress (v1.7.0 - Next):
- [ ] Implement embedding_agent logic (Ollama integration)
- [ ] Implement matching_agent logic (vector similarity)
- [ ] Customer/Platform import pipeline
- [ ] Semantic embeddings generation

### 🎯 Roadmap:
- [ ] Matching engine
- [ ] Traceability visualization
- [ ] Git impact analysis
- [ ] Report generation
- [ ] DNG/Rhapsody integration

---

## 🐛 Troubleshooting

### Web returns 502:
```bash
ssh root@168.119.122.36
docker logs aat-web-container --tail 50
docker compose restart
```

### Agent not reporting:
```bash
ssh root@128.140.108.240
docker ps --filter "name=aat-"
docker logs aat-monitor-db
```

### Deploy fails:
1. Check GitHub Actions logs
2. Verify SSH keys in Secrets
3. Ensure `/root/master-project` exists on both servers
4. Verify Docker is running

---

## Change Log

- [x] **v1.64** (2026-01-17) - **E.3.1: Admin Panel Management**
  - [x] Implemented User Management (view, create, manage roles, activate/deactivate)
  - [x] Role definitions: Admin (full access) vs Visitor (read-only)
  - [x] Implemented Customer Management (view, create, delete)
  - [x] Implemented Platform Management (view, create, update, delete)
  - [x] Extended database.py with 13 new helper functions
  - [x] Admin panel with 4 tabs: Users, Customers, Platforms, Settings
  - [x] RBAC enforced: Admin-only access to Admin panel
  - [x] System info dashboard with metrics
  - [x] Next: E.3.2 - Enhanced Import Platform (platform + data type selection)

- [x] **v1.63** (2026-01-17) - **Fix: Import Module Path Resolution**
  - [x] Fixed ModuleNotFoundError in Docker for import_platform/import_customer
  - [x] Used importlib.util to load modules (avoids 'import' keyword conflict)
  - [x] Added Docker path (/app/agents/import) with local fallback
  - [x] Tested import functionality successfully

- [x] **v1.62** (2026-01-17) - **E.2: Import UI Pages**
  - [x] Created web/pages/10_Import_Platform.py (admin-only)
  - [x] Created web/pages/11_Import_Customer.py (admin-only)
  - [x] File upload UI for CSV/JSONL requirements import
  - [x] RBAC protection (admin role required)
  - [x] Integration with backend import pipeline (v1.61)
  - [x] Success/error handling with detailed feedback
  - [x] Complete import pipeline: Backend (E.1) + Frontend (E.2)
  - [x] Next: E.3 - Test import with sample CSV data

- [x] **v1.61** (2026-01-17) - **E.1: Backend Import Pipeline**
  - [x] ✅ Extended agents/db_bridge/database.py with 4 new helper functions
  - [x] ✅ insert_or_update_platform_requirement() - Platform req import
  - [x] ✅ insert_or_update_customer_requirement() - Customer req import
  - [x] ✅ create_customer_project() - Customer project creation
  - [x] ✅ list_projects() - List all projects
  - [x] ✅ Created agents/import/import_platform.py (CSV/JSONL loader)
  - [x] ✅ Created agents/import/import_customer.py (CSV/JSONL loader)
  - [x] ✅ Created web/components/importer.py (UI wrapper for imports)
  - [x] Backend ready for E.2 (Windsurf will create UI pages)
  - [x] Next: E.2 - Import UI pages (10_Import_Platform, 11_Import_Customer)
  
- [x] **v1.6.0** (2026-01-17) - **All Agents Active + Resource Monitoring**
  - [x] ✅ Created scaffolds for all 9 computation agents
  - [x] ✅ All agents running in daemon loop mode
  - [x] ✅ All agents reporting heartbeat to agent_status table
  - [x] ✅ Added CPU/RAM monitoring to agent heartbeat (psutil)
  - [x] ✅ Visual resource bars in Status dashboard UI
  - [x] ✅ Updated docker-compose.agents.yml with all 10 services
  - [x] ✅ Added psutil and plotly to requirements
  - [x] Agents created: embedding_agent, matching_agent, trace_agent, git_impact_agent, report_agent, pdf_chunker, pdf_extractor, strict_extractor, bridge_api
  - [x] Next: Implement actual logic in agents (v1.7)

- [x] **v1.5** (2026-01-17) - **Deploy Process Complete**
  - [x] ✅ GitHub Actions workflows functional (Linux 1 + Linux 2)
  - [x] ✅ Automated .env generation from secrets
  - [x] ✅ Git reset + pull to avoid conflicts
  - [x] ✅ Docker compose build + deploy working
  - [x] ✅ Monitor agents operational and reporting heartbeat
  - [x] Changed session timeout from 8 hours to 1 hour
  - [x] Restored Chat page with Ollama integration
  - [x] Updated README with deployment documentation

- [x] **v1.4.5.8** (2026-01-17) - **CRITICAL: Missing 'agents' Directory in Container**
  - [x] CRITICAL: Verified COPY agents/ /app/agents/ in Dockerfile
  - [x] Added emphasis comments to prevent agents directory from being missed
  - [x] Verified build context is set to root directory (.)
  - [x] Confirmed agents/ copied before web/ in Dockerfile
  - [x] Updated sidebar: v1.4.5.8 | Ollama Mod: v0.5
  - [x] Container structure: /app/agents/ and /app/app.py must coexist
  - [x] Added verification: ls /app should show agents directory
- [x] **v1.4.5.6** (2026-01-17) - **Final Fix for 'agents' Import**
  - [x] CRITICAL: Added dual sys.path.append for Docker compatibility
  - [x] Added sys.path.append(os.path.dirname(os.path.abspath(__file__)))
  - [x] Added sys.path.append("/app") for explicit Docker path
  - [x] Created __init__.py in agents/ folder to make it a proper Python module
  - [x] Created __init__.py in agents/db_bridge/ folder
  - [x] Verified Dockerfile COPY agents/ happens before CMD streamlit
  - [x] Updated sidebar: v1.4.5.6 | Ollama Mod v0.5 [cite: 2026-01-11]
  - [x] Final comprehensive fix for ModuleNotFoundError
- [x] **v1.4.5.5** (2026-01-16) - **Fix ModuleNotFoundError for 'agents'**
  - [x] CRITICAL: Fixed import path for agents module
  - [x] Updated sys.path.append to use os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  - [x] Verified ENV PYTHONPATH="/app" in Dockerfile (correct)
  - [x] Verified agents/ folder copied to /app/agents/ at same level as web/
  - [x] Updated sidebar: v1.4.5.5 | Ollama Mod v0.5 [cite: 2026-01-11]
  - [x] Final fix for web startup - no more ModuleNotFoundError
- [x] **v1.4.5.3** (2026-01-16) - **Environment Injection & Final Web Start**
  - [x] Fixed deployment workflow to generate .env file from GitHub Secrets
  - [x] Added DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS injection
  - [x] Ensured DB_HOST points to LINUX_1_IP (128.140.108.240)
  - [x] Updated sidebar display: v1.4.5.3 | Ollama Mod v0.5 [cite: 2026-01-11]
  - [x] Verified PYTHONPATH="/app" in Dockerfile (correct)
  - [x] Added error resilience to prevent 502 on DB connection failure
  - [x] Web container stays running even when DB is unavailable
- [x] **v1.4.5.2** (2026-01-16) - **Web Runtime & Docker Environment Fixes**
  - [x] Added ENV PYTHONPATH="/app" to web/Dockerfile for proper imports
  - [x] Added COPY agents/ to Dockerfile to make agent modules available
  - [x] Verified Streamlit entrypoint with --server.port=8501 --server.address=0.0.0.0
  - [x] Added startup logging to web/app.py showing DB connection target
  - [x] Enhanced Ollama Mod v0.5 display to read from work_aa.agent_status
  - [x] Kept sys.path hack in app.py as fallback for local development
  - [x] Added error logging for DB connection issues
- [x] **v1.4.5.1** (2026-01-16) - **Deployment Workflow Fixes**
  - [x] CRITICAL: Fixed secret names in all deployment workflows
  - [x] Updated to use LINUX_1_IP and LINUX_2_IP (not HOST)
  - [x] Updated to use SSH_KEY_L1 and SSH_KEY_L2 (not SSH_KEY)
  - [x] Added dual ssh-keyscan for both servers in all workflows
  - [x] Deprecated old workflows (deploy-bridge-ollama, deploy-db-bridge, deploy-monitor-ollama)
  - [x] Removed all remaining GCP references
  - [x] Verified Python path fix in web/app.py (already correct)
- [x] **v1.4.5** (2026-01-16) - **Emergency Path Fix & Infrastructure Alignment**
  - [x] CRITICAL: Fixed Python import paths for Docker/Linux compatibility
  - [x] Added os.path.abspath() in web/app.py and web/components/agents.py
  - [x] Added comprehensive error handling in 02_Status.py to prevent crashes
  - [x] Split infrastructure: Linux 1 (DB + monitor-db), Linux 2 (Web + monitor-ollama)
  - [x] Created deploy-linux1-monitor-db.yaml workflow with SSH_KEY_L1
  - [x] Created deploy-linux2-web-ollama.yaml workflow with SSH_KEY_L2
  - [x] Updated deploy_web.yaml to use LINUX_2_IP (removed GCP references)
  - [x] Created docker-compose.linux1.yml (monitor-db connects to localhost:5432)
  - [x] Created docker-compose.linux2.yml (monitor-ollama connects to LINUX_1_IP:5432)
  - [x] Updated app.py sidebar: v1.4.5 | Ollama Mod v0.5 [cite: 2026-01-11]
  - [x] All agents enforce search_path=work_aa for schema isolation
- [x] **v1.4.4** (2026-01-16) - **Final Agent Integration & Infrastructure**
  - [x] Added agent_status and system_health tables to schema work_aa
  - [x] Implemented agent heartbeat backend in agents/db_bridge/database.py
  - [x] Created web/components/agents.py helper for Status page
  - [x] Implemented Status dashboard (02_Status.py) with agent monitoring
  - [x] Created monitor_db_server.py agent with DB health checks
  - [x] Created monitor_ollama_server.py agent with Ollama Module v0.5 tracking
  - [x] Added docker-compose.agents.yml for monitor services
  - [x] Updated app.py sidebar to read Ollama status from DB
  - [x] All agents seed data initialized in manage_db_aa.py
  - [x] Version bumped to 1.4.4 in manage_db_aa.py
- [x] **v1.4.3** (2026-01-16) - **Database Dashboard & Table Browser**
  - [x] Implemented DB Status page (03_DB_Status.py) with read-only dashboard
  - [x] Shows table statistics from work_aa schema using get_aa_stats()
  - [x] Added placeholder buttons for future features (DB Extensions, Storage Size)
  - [x] Implemented Table View page (04_TableView.py) with pagination
  - [x] Browse all work_aa tables with 50 rows per page
  - [x] Pagination controls with Previous/Next buttons
  - [x] Admin-only access for both pages
- [x] **v1.4.2** (2026-01-16) - **Emergency Fix: Session Revocation & Timezone Sync**
  - [x] Emergency fix for session revocation and timezone sync
  - [x] Fixed timezone mismatch using datetime.now(timezone.utc)
  - [x] Simplified session validation to prevent auto-revocation
  - [x] Sessions now remain active for 8 hours with UTC timezone
  - [x] Changed app title to '🏠 App Home'
  - [x] Verified st.rerun() after login for immediate UI update
- [x] **v1.4.1** (2026-01-16) - **Bug Fix: Session Revocation Loop**
  - [x] Fixed session revocation loop preventing user login
  - [x] Explicitly set revoked=FALSE in session creation
  - [x] Prevented get_current_user from invalidating newly created sessions
  - [x] Added UI feedback for revoked sessions in sidebar
  - [x] Session validation now respects fresh login state
- [x] **v1.4.0** (2026-01-16) - **Auth State & DB Sync Fixes**
  - [x] Added detailed session creation error logging in auth.py
  - [x] Implemented st.rerun() after successful login for immediate UI update
  - [x] Enhanced sidebar status display: shows full_name and primary role
  - [x] Improved session synchronization across all tabs
  - [x] Created db_read.py inspection script for debugging DB state
  - [x] Active debugging of authentication flow and session management
- [x] **v1.3.9** (2026-01-16) - **Advanced Metadata & Auth Status**
  - [x] Dynamic build date using datetime.now()
  - [x] Session Info section in sidebar with auth status, email, and roles
  - [x] Last login result tracking (success/failure)
  - [x] Tab sync fix with auth.get_current_user() calls
  - [x] Clean logout with success message and state clearing
- [x] **v1.3.8** (2026-01-16) - **Simplified Static Navigation & Security**
  - [x] Removed dynamic navigation logic for simplicity
  - [x] Uniform protection with 'Goto Login Page' button on all pages
  - [x] Version info in sidebar: v1.3.8 | Ollama Mod: v0.5.
  - [x] Static navigation with proper icons for all pages
- [x] **v1.3.7** (2026-01-16) - **UI/UX Refinement & Secure Routing**
  - [x] Strict sidebar locking for unauthenticated users
  - [x] Dynamic role-based navigation for authenticated users
  - [x] Logout button in sidebar with redirect to Login
  - [x] Version info display in sidebar
  - [x] Global protection on all pages with redirect to Login
- [x] **v1.3.2** (2026-01-16) - **Hotfix: Docker Container Name Conflict**
  - [x] Added container cleanup step in deploy_web.yaml workflow
  - [x] Prevents deployment failures due to existing container names
  - [x] Added `docker rm -f aat-web-container` before docker compose up
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
 │   ├─ 00_Login.py           # Authentication login page
 │   ├─ 01_Dashboard.py       # System overview and key metrics
 │   ├─ 02_Status.py          # Agent and system status monitoring
 │   ├─ 03_DB_Status.py       # Database health and statistics
 │   ├─ 04_TableView.py       # Browse database tables
 │   ├─ 05_Matching.py        # Requirements matching interface
 │   ├─ 06_Trace.py           # Traceability analysis
 │   ├─ 07_Impact.py          # Git impact analysis
 │   ├─ 08_Reports.py         # Generate and view reports
 │   ├─ 09_Chat.py            # AI chat interface (Type A)
 │   ├─ 10_Import_Platform.py # Platform requirements import (E.2)
 │   ├─ 11_Import_Customer.py # Customer requirements import (E.2)
 │   └─ 99_Admin.py           # Admin panel
 ├─ components/
 │   ├─ layout.py             # Header rendering and layout utilities
 │   ├─ utils.py              # Chat and utility functions
 │   └─ importer.py           # Import wrapper functions (E.1)
 ├─ static/
 │   ├─ css/
 │   │   └─ app.css           # Minimal styling
 │   └─ img/
 └─ requirements.txt

agents/import/                 # Import modules (E.1)
 ├─ __init__.py
 ├─ import_platform.py        # Platform CSV/JSONL loader
 └─ import_customer.py        # Customer CSV/JSONL loader
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
| **v1.64   ** | 2026-01-17 | **E.3.1: Admin Panel Management** - User/Customer/Platform management with 4 tabs
| **v1.62   ** | 2026-01-17 | **E.2: Import UI Pages** - Frontend for platform/customer requirements import
| **v1.61   ** | 2026-01-17 | **E.1: Backend Import Pipeline** - E.1: steps done
| **v1.6.0  ** | 2026-01-17 | **All Agents Active + Resource Monitoring** - 9 computation agent scaffolds, CPU/RAM monitoring, visual resource bars in UI
| **v1.5    ** | 2026-01-17 | **Deploy Process Complete**
| **v1.4.5.8** | 2026-01-17 | **CRITICAL: Missing 'agents' Directory in Container**. Verified and emphasized COPY agents/ instruction in Dockerfile, confirmed build context, added critical comments to prevent directory from being missed. |
| **v1.4.5.6** | 2026-01-17 | **Final Fix for 'agents' Import**. Added dual sys.path.append, created __init__.py files in agents folders, comprehensive fix for ModuleNotFoundError in Docker. |
| **v1.4.5.5** | 2026-01-16 | **Fix ModuleNotFoundError for 'agents'**. Fixed critical import path issue preventing agents module from loading, updated sys.path resolution, final web startup fix. |
| **v1.4.5.3** | 2026-01-16 | **Environment Injection & Final Web Start**. Fixed deployment workflow to generate .env from GitHub Secrets, ensured DB connection to LINUX_1_IP, added error resilience to prevent 502 errors. |
| **v1.4.5.2** | 2026-01-16 | **Web Runtime & Docker Environment Fixes**. Added PYTHONPATH to Dockerfile, startup logging, verified Ollama status display from DB, fixed import issues in Docker container. |
| **v1.4.5.1** | 2026-01-16 | **Deployment Workflow Fixes**. Fixed secret names to match GitHub Secrets (LINUX_1_IP, LINUX_2_IP, SSH_KEY_L1, SSH_KEY_L2), added dual ssh-keyscan, deprecated old workflows. |
| **v1.4.5** | 2026-01-16 | **Emergency Path Fix & Infrastructure Alignment**. Fixed critical Python import paths for Docker/Linux, split infrastructure across two servers, removed GCP dependencies, added robust error handling. |
| **v1.4.4** | 2026-01-16 | **Final Agent Integration & Infrastructure**. Implemented agent heartbeat system, monitoring agents for DB and Ollama, Status dashboard, and docker-compose for agent services. |
| **v1.4.3** | 2026-01-16 | **Database Dashboard & Table Browser**. Added DB Status and Table View modules for read-only database browsing with pagination. |
| **v1.3.2** | 2026-01-16 | **Hotfix: Docker Container Conflict**. Fixed deployment failures by adding container cleanup step to prevent name conflicts. |
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
