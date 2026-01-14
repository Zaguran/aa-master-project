# PROJECT: aa-poc (Proof of Concept - Requirements Digitalization)

## Project Overview
**Purpose**: PoC for digitalization of customer requirements and automatic matching with system requirements. Demo for management decision-making.

**System Components:**
- **Customer Requirements** → Digitalization → System Requirements matching
- **V-Model simulation**: simplified subset with SRC (git)
- **DNG simulation** (DOORS Next Gen): Requirements detail from TimescaleDB
- **Rhapsody simulation**: Similar to DNG (possibly with static images)
- **Requirements ↔ Source Code traceability**: Bidirectional change detection

**Multi-VM Architecture:**
- **Linux VM #1**: TimescaleDB database, HW monitoring, digitalization agents (PDF processing)
- **Linux VM #2**: Ollama AI, Web interface (Docker container), HW monitoring
  - Web URL: http://168.119.122.36
  - Web for: task assignment, agent monitoring, visualization

**Tech Stack:**
- Database: TimescaleDB (PostgreSQL) - hosted on Linux VM #1
- Backend: Python agents (digitalization, matching, monitoring)
- Frontend: Web interface (Dockerized on Linux VM #2)
- AI: Ollama (Linux VM #2)
- Version Control: Git + GitHub

**Environment Setup:**
- Database credentials: configured on Linux VMs
- Web runs in Docker container on Linux VM #2
- PoC status: Demo system, can be shut down after management review

## Database Context (CRITICAL)
- **Primary schema**: `work_aa` (full access - can modify)
- **Shared schemas**: `schema_trading`, `schema_mt` exist in same DB but are INVISIBLE to this project
  - DO NOT query, modify, or reference these schemas
  - They belong to different projects
- Schema definition: `agents/db_basis/manage_db_aa.py`
- Current version: see version comment at top of manage_db_aa.py
- **WARNING**: Only `work_aa` can be modified. All other schemas are OFF-LIMITS.

## Tables Structure (work_aa schema)
- **customer**: Customer information
- **projects**: Project hierarchy (platforms, variants)
- **nodes**: Requirements nodes (type, scope, inheritance, ASIL, test_level, content)
- **links**: Traceability links between nodes (AI matching scores)
- **ai_analysis**: AI analysis results for nodes

## Versioning Rules (STRICT)
- **Every change** increments version by 0.01 (unless explicitly told otherwise)
- Version location: Top comment in `manage_db_aa.py`
  - Format: `Version: X.Y.Z - Description of change`
- **After every change**:
  1. Update version in manage_db_aa.py
  2. Update README.md with changelog entry
  3. Create git tag: `git tag vX.Y.Z`
  4. Push with tags: `git push && git push --tags`

## Task Execution Rules (STRICT)
- Modify ONLY files explicitly mentioned in the task
- If the task cannot be completed fully, DO NOT:
  - commit
  - deploy
  - modify additional files
  - continue working
- If interrupted or context is missing: STOP and report status
- NEVER make assumptions - always ask if unclear

## Git Workflow (CRITICAL)
### Standard Process:
```bash
# 1. Make changes
# 2. Update version in manage_db_aa.py (+0.01)
# 3. Update README.md changelog
# 4. Verify changes
git diff

# 5. Stage and commit
git add .
git commit -m "type: description (vX.Y.Z)"

# 6. Create version tag
git tag vX.Y.Z

# 7. Pull and push
git pull --rebase
git push
git push --tags

# If ANY step fails, STOP and report
```

### Commit Message Format:
- `feat: description (vX.Y.Z)` - new feature
- `fix: description (vX.Y.Z)` - bug fix
- `refactor: description (vX.Y.Z)` - code improvement
- `docs: description (vX.Y.Z)` - documentation only

### If Git Push Fails:
1. STOP immediately
2. Do NOT attempt fixes
3. Report the error
4. Wait for instructions

## Output Rules
- Prefer unified diff output for changes
- Do not reformat unrelated code
- Do not refactor unless explicitly asked
- Show file paths for all modifications
- Always show version numbers in responses

## Safety Checks (CRITICAL)
- **Before ANY database operation**: confirm target schema is `work_aa`
- If a change would affect `schema_trading` or `schema_mt` → respond with:
```
  FAIL: Cannot access schema - belongs to different project
```
- If unsure about impact → ask before proceeding
- Before commit: verify no unintended changes (`git diff`)

## Testing Before Commit
- Verify manage_db_aa.py syntax: `python3 -m py_compile manage_db_aa.py`
- Run existing tests if available: `pytest`
- Verify web application starts without errors (if applicable)
- Check Docker container status: `docker ps`

## Docker & Dependencies Management
- **Web application**: Runs in Docker container on Linux VM #2
- **Python dependencies**: Always update `requirements.txt` when adding new libraries
- **Dockerfile**: May need updates for system-level dependencies or configuration changes
  - Before modifying Dockerfile: STOP and ask for confirmation
  - Explain what change is needed and why
  - Wait for approval before proceeding
- Docker rebuild: May be manual or automated depending on deployment setup

### When Adding New Library:
1. Add to `requirements.txt`
2. Check if Dockerfile needs system packages
3. If Dockerfile change needed: ASK FIRST, then proceed if approved
4. Document in README.md changelog
5. Rebuild Docker container if web application affected

### Docker Commands Reference:
```bash
# Check running containers
docker ps

# View logs
docker logs <container_name>

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Documentation Requirements
- Every version change requires README.md update
- Changelog format in README.md:
```markdown
  ## vX.Y.Z - YYYY-MM-DD
  - Description of changes
  - Impact/notes if any
```

## Common Pitfalls to Avoid
- DO NOT continue working after failed git push
- DO NOT modify schema_trading or schema_mt under any circumstances
- DO NOT access schemas belonging to other projects
- DO NOT make "helpful" changes outside the task scope
- DO NOT assume context from previous sessions
- DO NOT forget to create git tag after version increment
- DO NOT skip README.md update
- DO NOT modify Dockerfile without asking first
- DO NOT shut down web without explicit instruction (PoC demo system)

## Project-Specific Context
- **PoC Status**: This is a demonstration system for management
- **Customer Requirements**: Digitalized from PDF documents
- **Matching Logic**: AI-powered (Ollama) partial matching between requirements
- **V-Model**: Simplified representation with git-based SRC
- **Traceability**: Bidirectional change detection (requirements ↔ code)
- **Web Interface**: Task assignment, monitoring, visualization at http://168.119.122.36

## File Locations Reference
- DB Schema: `agents/db_basis/manage_db_aa.py`
- README: `README.md` (root)
- Agents: `agents/` (digitalization, matching, monitoring)
- Dependencies: `requirements.txt`
- Docker: `Dockerfile`, `docker-compose.yml`
- Web deployment: http://168.119.122.36