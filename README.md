# AAT - Automotive Assistance Tool

AI-driven Requirements Engineering Proof-of-Concept for automated requirements digitalization, matching, and traceability.

## Current Version: 1.4.5

**Status:** Active development - session management stabilized

## Change Log
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
