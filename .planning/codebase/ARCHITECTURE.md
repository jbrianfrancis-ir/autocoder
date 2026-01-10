# Architecture

**Analysis Date:** 2026-01-10

## Pattern Overview

**Overall:** Hybrid Distributed Architecture - CLI Agent + Web UI Server

**Key Characteristics:**
- Two-agent pattern (Initializer + Coding Agent)
- Subprocess-based agent execution with WebSocket monitoring
- Cross-platform project registry
- MCP (Model Context Protocol) for agent-tool communication
- Real-time updates via WebSocket

## Layers

**Entry Point Layer:**
- Purpose: CLI and Web UI launching
- Contains: Menu systems, subprocess spawning, browser launch
- Location: `start.py`, `start_ui.py`, `autonomous_agent_demo.py`
- Depends on: Registry, agent execution
- Used by: End users

**Agent Execution Layer:**
- Purpose: Claude SDK agent session management
- Contains: Agent loop, client configuration, security hooks
- Location: `agent.py`, `client.py`, `security.py`
- Depends on: Claude SDK, MCP servers, prompts
- Used by: Entry points, process manager

**API/Server Layer:**
- Purpose: REST API and WebSocket for UI
- Contains: Route handlers, schemas, middleware
- Location: `server/main.py`, `server/routers/*.py`
- Depends on: Services, database, registry
- Used by: React frontend

**Service Layer:**
- Purpose: Business logic and state management
- Contains: Process manager, chat sessions, WebSocket manager
- Location: `server/services/*.py`, `server/websocket.py`
- Depends on: Data layer, subprocess management
- Used by: API routers

**MCP Integration Layer:**
- Purpose: Agent tools via Model Context Protocol
- Contains: Feature MCP server, Playwright integration
- Location: `mcp_server/feature_mcp.py`, spawned via `client.py`
- Depends on: Database, FastMCP
- Used by: Agent during execution

**Data Layer:**
- Purpose: Persistence for features, registry, conversations
- Contains: SQLAlchemy models, migrations
- Location: `api/database.py`, `registry.py`, `server/services/assistant_database.py`
- Depends on: SQLite
- Used by: All layers

**Frontend Layer:**
- Purpose: React UI for project management
- Contains: Components, hooks, API client
- Location: `ui/src/`
- Depends on: Server API, WebSocket
- Used by: End users via browser

## Data Flow

**Agent Execution Flow:**

1. User starts agent via CLI or Web UI
2. `autonomous_agent_demo.py` resolves project path from registry
3. `agent.py` checks if `features.db` has data:
   - NO features → Run initializer_prompt (creates features)
   - YES features → Run coding_prompt (implements features)
4. `create_client()` builds ClaudeSDKClient with:
   - Security hooks (bash allowlist)
   - MCP servers (feature_mcp, playwright)
   - Built-in tools (Read, Write, Glob, Grep)
5. Agent uses MCP tools to:
   - Get next feature (`feature_get_next`)
   - Mark feature in-progress
   - Write code, run tests
   - Mark feature passing
6. Process manager streams output to WebSocket clients

**Web UI Request Flow:**

1. User action in React component
2. REST API call to FastAPI router
3. Service layer executes business logic
4. Data layer query/update
5. Response + WebSocket broadcast to all clients

**State Management:**
- Feature state: SQLite per project (`features.db`)
- Agent state: Process manager singleton per project
- UI state: React Query + WebSocket subscription
- Registry: Global SQLite (`~/.autocoder/registry.db`)

## Key Abstractions

**Two-Agent Pattern:**
- Purpose: Separate feature creation from implementation
- Examples: Initializer creates features, Coder implements them
- Pattern: Session type determined by `has_features()` check

**Process Manager (`server/services/process_manager.py`):**
- Purpose: Agent subprocess lifecycle management
- Examples: `AgentProcessManager` class
- Pattern: Singleton per project via `get_manager()`
- Methods: `start()`, `stop()`, `pause()`, `resume()`, `healthcheck()`

**Project Registry (`registry.py`):**
- Purpose: Cross-platform project path mapping
- Examples: `get_project_path()`, `register_project()`
- Pattern: SQLite-backed name→path dictionary
- Location: `~/.autocoder/registry.db`

**Prompt Loading (`prompts.py`):**
- Purpose: Template loading with fallback chain
- Examples: `load_prompt("coding_prompt")`
- Pattern: Project-specific → Base template fallback
- Paths: `{project}/prompts/` → `.claude/templates/`

**MCP Servers:**
- Purpose: Agent tool access via standard protocol
- Examples: Feature MCP, Playwright MCP
- Pattern: FastMCP server spawned per agent
- Tools: `feature_get_next`, `feature_mark_passing`, etc.

**WebSocket Manager (`server/websocket.py`):**
- Purpose: Real-time updates to UI clients
- Examples: `ConnectionManager` class
- Pattern: Per-project connection sets
- Messages: progress, feature_update, log, agent_status

## Entry Points

**CLI Entry:**
- Location: `start.py`
- Triggers: User runs `python start.py`
- Responsibilities: Project menu, create/continue selection

**Web UI Entry:**
- Location: `start_ui.py`
- Triggers: User runs `./start_ui.sh` or `start_ui.bat`
- Responsibilities: Spawn venv, npm build, FastAPI server, open browser

**Agent Entry:**
- Location: `autonomous_agent_demo.py`
- Triggers: Process manager subprocess, CLI direct run
- Responsibilities: Parse args, resolve project, run agent loop

**FastAPI Entry:**
- Location: `server/main.py`
- Triggers: Uvicorn startup
- Responsibilities: Register routes, middleware, lifespan

## Error Handling

**Strategy:** Exceptions bubble up to boundary handlers

**Patterns:**
- API routes: HTTPException with status codes
- WebSocket: Silent reconnect with exponential backoff
- Agent: Print errors, continue to next feature
- Security: Block dangerous commands before execution

## Cross-Cutting Concerns

**Logging:**
- Console output via `print()` statements
- Agent output sanitized to remove API keys
- No structured logging framework

**Validation:**
- Pydantic schemas at API boundary (`server/schemas.py`)
- Project name regex: `^[a-zA-Z0-9_-]{1,50}$`
- Security hooks for bash commands

**Security:**
- Bash command allowlist (`security.py`)
- Filesystem sandbox to project directory
- Output redaction for secrets
- CORS middleware (currently over-permissive)

---

*Architecture analysis: 2026-01-10*
*Update when major patterns change*
