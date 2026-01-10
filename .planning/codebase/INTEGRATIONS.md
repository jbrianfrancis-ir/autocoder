# External Integrations

**Analysis Date:** 2026-01-10

## APIs & External Services

**Claude AI Integration:**
- Anthropic Claude SDK - Agent intelligence via `claude-agent-sdk`
  - SDK/Client: `claude_agent_sdk` package (`client.py`)
  - Auth: Credentials from `~/.claude/.credentials.json` (auto-detected)
  - Models: Configurable via `--model` flag, defaults in `registry.py`

**N8N Webhooks (Optional):**
- Progress notifications - Webhook for feature completions
  - Integration: HTTP POST requests (`progress.py:165-175`)
  - Auth: None (URL-based access)
  - Config: `PROGRESS_N8N_WEBHOOK_URL` environment variable
  - Payload: Feature ID, name, counts, timestamps

## Data Storage

**Databases:**
- SQLite - Feature storage (per project)
  - Connection: `sqlite:///{project_dir}/features.db` (`api/database.py`)
  - Client: SQLAlchemy 2.0+ ORM
  - Migrations: In-code via `_migrate_add_in_progress_column()` (`api/database.py`)

- SQLite - Project registry (global)
  - Connection: `~/.autocoder/registry.db` (`registry.py`)
  - Client: SQLAlchemy ORM
  - Purpose: Map project names to filesystem paths

- SQLite - Assistant conversations (per project)
  - Connection: `{project_dir}/assistant.db`
  - Client: SQLAlchemy (`server/services/assistant_database.py`)
  - Purpose: Persist assistant chat history

**File Storage:**
- Local filesystem only
  - Project files stored in user-specified directories
  - No cloud storage integration
  - Prompts stored in `{project_dir}/prompts/`

**Caching:**
- None (all database queries, no Redis/Memcached)

## Authentication & Identity

**Auth Provider:**
- Claude CLI authentication - Uses existing Claude credentials
  - Implementation: `~/.claude/.credentials.json` auto-discovery
  - Token storage: Local filesystem (managed by Claude CLI)
  - Session management: Per-agent execution

**OAuth Integrations:**
- None (local application only)

## Monitoring & Observability

**Error Tracking:**
- None (stdout/stderr logging only)
  - Errors logged to console via `print()` statements
  - No Sentry, Datadog, or similar integration

**Analytics:**
- None

**Logs:**
- Console output only
  - Agent output streamed to WebSocket clients
  - Sanitization removes API keys before display (`server/services/process_manager.py`)

## CI/CD & Deployment

**Hosting:**
- Local execution (not a hosted service)
  - Development: `python start_ui.py` or `./start_ui.sh`
  - No cloud deployment configuration

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
  - Workflows: Python linting (Ruff), type checking (Mypy), security tests
  - UI: Build verification, TypeScript type checking
  - Secrets: None required (public tests only)

## Environment Configuration

**Development:**
- Required env vars: None (all optional)
- Optional: `PROGRESS_N8N_WEBHOOK_URL` for notifications
- Optional: `VITE_API_PORT` for custom API port (default 8888)
- Secrets location: `.env.local` (gitignored)

**Staging:**
- Not applicable (local development tool)

**Production:**
- Runs locally on user machine
- No separate production environment

## Webhooks & Callbacks

**Incoming:**
- None (no external webhooks received)

**Outgoing:**
- N8N Progress Webhook - `progress.py:177-185`
  - Endpoint: User-configured `PROGRESS_N8N_WEBHOOK_URL`
  - Trigger: Feature marked as passing
  - Payload: `{ feature_id, feature_name, passing_count, total_count, percentage, timestamp }`
  - Retry logic: None (single attempt with 5s timeout)

## MCP Servers

**Feature MCP Server:**
- Command: `python -m mcp_server.feature_mcp` (`client.py:165`)
- Tools: Feature management for agent
  - `feature_get_stats` - Progress statistics
  - `feature_get_next` - Next pending feature
  - `feature_get_for_regression` - Random passing features
  - `feature_mark_passing` - Mark feature complete
  - `feature_skip` - Move feature to end of queue
  - `feature_create_bulk` - Bulk feature creation

**Playwright MCP Server:**
- Command: `npx @playwright/mcp@latest --viewport-size 1280x720` (`client.py:31-61`)
- Purpose: Browser automation for agent testing
- Tools: Snapshots, clicks, navigation, screenshots, etc.
- Status: Optional (disabled in YOLO mode)

## Real-time Communication

**WebSocket:**
- Protocol: WebSocket over HTTP/HTTPS
- Path: `/ws/projects/{project_name}` (`server/websocket.py`)
- Message Types:
  - `progress` - Feature pass counts
  - `agent_status` - Running/paused/stopped/crashed
  - `log` - Agent output lines
  - `feature_update` - Feature status changes
  - `pong` - Heartbeat response
- Auto-reconnect: Exponential backoff in UI (`ui/src/hooks/useWebSocket.ts`)

---

*Integration audit: 2026-01-10*
*Update when adding/removing external services*
