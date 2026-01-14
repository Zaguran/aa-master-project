# AI Requirements Extractor

An AI-powered tool for extracting requirements from PDF documents using vision-based analysis.

## Current Version: 1.0.2

## Change Log
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

### AI Requirements Extraction
- Upload PDF documents for automated requirements extraction
- Uses **llava** vision model to analyze document images
- Outputs structured Markdown tables with requirement IDs and text
- Strict prompts ensure AI only extracts visible text (no hallucinations)

### Privacy & Generic Customer IDs
The system uses generic Customer IDs (e.g., `CUST-001`) instead of customer-specific identifiers. This ensures:
- **Privacy compliance**: No customer names stored in extraction logs
- **Data portability**: Results can be shared without exposing client identities
- **Demo-safe**: Safe for presentations and demos

### Technical Configuration
| Parameter | Value | Purpose |
|-----------|-------|---------|
| Temperature | 0.1 | Low creativity for stable output |
| Context Window | 4096 | Token context size |
| Threads | 8 | Parallel processing threads |
| PDF DPI | 150 | Image conversion quality |
| Model | llava | Vision-capable LLM |

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
