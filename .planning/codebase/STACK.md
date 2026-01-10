# Technology Stack

**Analysis Date:** 2026-01-10

## Languages

**Primary:**
- Python 3.11 - Backend server, agent logic, MCP servers (`pyproject.toml`)
- TypeScript 5.6.2 - React frontend (`ui/package.json`)

**Secondary:**
- JavaScript - Build scripts, config files (`ui/vite.config.ts`)

## Runtime

**Environment:**
- Python 3.11+ - Backend runtime (target-version in `pyproject.toml`)
- Node.js 20.x - Frontend build and development (`.github/workflows/ci.yml`)
- No browser runtime for Python (CLI + server only)

**Package Manager:**
- Python: pip with `requirements.txt`
- Node.js: npm 10.x with `package-lock.json` (lockfileVersion: 3)

## Frameworks

**Core:**
- FastAPI 0.115+ - REST API server (`requirements.txt`, `server/main.py`)
- React 18.3.1 - UI framework (`ui/package.json`)
- Claude Agent SDK 0.1+ - Agent execution (`requirements.txt`, `client.py`)

**Testing:**
- Pytest 8.0+ - Python testing (not extensively used)
- Custom test harness - Security validation (`test_security.py`)
- No frontend testing framework configured

**Build/Dev:**
- Vite 5.4.10 - Frontend bundling and dev server (`ui/vite.config.ts`)
- Uvicorn 0.32+ - ASGI server for FastAPI (`requirements.txt`)
- TypeScript 5.6.2 - Compilation (`ui/tsconfig.json`)

## Key Dependencies

**Critical:**
- SQLAlchemy 2.0+ - ORM for feature database (`api/database.py`)
- FastMCP - MCP server implementation (`mcp_server/feature_mcp.py`)
- psutil 6.0+ - Cross-platform process management (`server/services/process_manager.py`)
- websockets 13.0+ - Real-time updates (`server/websocket.py`)

**Infrastructure:**
- python-dotenv 1.0+ - Environment variable loading
- aiofiles 24.0+ - Async file operations
- python-multipart 0.0.17+ - Form data parsing

**Frontend:**
- TanStack React Query 5.60+ - Server state management (`ui/src/hooks/useProjects.ts`)
- Radix UI - Accessible components (dialog, dropdown, tooltip)
- Tailwind CSS 4.0.0-beta.4 - Utility styling (`ui/package.json`)
- Lucide React 0.460+ - Icon library

## Configuration

**Environment:**
- `.env` files for secrets (gitignored)
- `.env.example` - Template with `PROGRESS_N8N_WEBHOOK_URL`
- Environment variables: `VITE_API_PORT` for frontend proxy

**Build:**
- `pyproject.toml` - Python tooling (Ruff, Mypy)
- `ui/vite.config.ts` - Frontend build with API proxy
- `ui/tsconfig.json` - TypeScript strict mode

## Platform Requirements

**Development:**
- Windows/macOS/Linux (cross-platform)
- Python 3.11+ with venv
- Node.js 20+ for UI development
- No external services required (SQLite for storage)

**Production:**
- Runs as local server (not containerized)
- FastAPI on port 8888 (default)
- Static UI served from `ui/dist/`
- No external database required (SQLite files per project)

---

*Stack analysis: 2026-01-10*
*Update after major dependency changes*
