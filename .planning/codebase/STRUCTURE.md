# Codebase Structure

**Analysis Date:** 2026-01-10

## Directory Layout

```
autocoder/
├── api/                    # Data layer (SQLAlchemy ORM)
├── mcp_server/             # MCP server implementations
├── server/                 # FastAPI backend
│   ├── routers/           # API route handlers
│   └── services/          # Business logic
├── ui/                     # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities and types
│   │   └── styles/        # CSS styles
│   └── dist/              # Built frontend (served by FastAPI)
├── .claude/               # Claude Code integration
│   ├── commands/          # Slash commands
│   ├── skills/            # Custom skills
│   └── templates/         # Prompt templates
├── .github/               # GitHub Actions
│   └── workflows/         # CI/CD workflows
├── .planning/             # GSD planning files
│   └── codebase/          # This codebase map
├── agent.py               # Agent session loop
├── client.py              # Claude SDK client factory
├── prompts.py             # Prompt loading
├── progress.py            # Progress tracking
├── registry.py            # Project registry
├── security.py            # Bash command allowlist
├── start.py               # CLI launcher
├── start_ui.py            # Web UI launcher
├── autonomous_agent_demo.py  # Agent entry point
└── requirements.txt       # Python dependencies
```

## Directory Purposes

**api/**
- Purpose: Data layer with SQLAlchemy ORM models
- Contains: `database.py` (Feature model), `migration.py`
- Key files: `database.py` - Feature table, database connection
- Subdirectories: None

**mcp_server/**
- Purpose: MCP server for agent tool access
- Contains: `feature_mcp.py` (FastMCP server)
- Key files: `feature_mcp.py` - Feature management tools
- Subdirectories: None

**server/**
- Purpose: FastAPI web backend
- Contains: Main app, routers, services, WebSocket
- Key files: `main.py` (app), `schemas.py` (Pydantic models), `websocket.py`
- Subdirectories: `routers/`, `services/`

**server/routers/**
- Purpose: REST API route handlers
- Contains: Route modules by feature
- Key files:
  - `projects.py` - Project CRUD
  - `agent.py` - Agent control (start/stop/pause)
  - `features.py` - Feature management
  - `filesystem.py` - Directory browser
  - `spec_creation.py` - Spec generation WebSocket
  - `assistant_chat.py` - Assistant chat endpoints
  - `settings.py` - Global settings

**server/services/**
- Purpose: Business logic and state management
- Contains: Process manager, chat sessions
- Key files:
  - `process_manager.py` - Agent subprocess lifecycle
  - `spec_chat_session.py` - Spec generation session
  - `assistant_chat_session.py` - Assistant conversation
  - `assistant_database.py` - Conversation persistence

**ui/src/**
- Purpose: React frontend source
- Contains: Components, hooks, utilities
- Subdirectories: `components/`, `hooks/`, `lib/`, `styles/`

**ui/src/components/**
- Purpose: React UI components (21 total)
- Contains: Modals, forms, cards, panels
- Key files:
  - `App.tsx` - Root component (in parent)
  - `ProjectSelector.tsx` - Project selection
  - `KanbanBoard.tsx` - Feature board
  - `AgentControl.tsx` - Start/stop/pause
  - `NewProjectModal.tsx` - Project creation wizard
  - `SpecCreationChat.tsx` - Spec generation chat
  - `AssistantPanel.tsx` - Assistant sidebar

**ui/src/hooks/**
- Purpose: Custom React hooks
- Contains: API hooks, WebSocket, utilities
- Key files:
  - `useProjects.ts` - Project CRUD, agent status
  - `useWebSocket.ts` - Real-time updates
  - `useAssistantChat.ts` - Assistant WebSocket
  - `useSpecChat.ts` - Spec creation WebSocket

**ui/src/lib/**
- Purpose: Utilities and types
- Contains: API client, TypeScript types
- Key files:
  - `api.ts` - REST API client
  - `types.ts` - TypeScript interfaces

**.claude/**
- Purpose: Claude Code integration
- Contains: Commands, skills, templates
- Subdirectories:
  - `commands/` - Slash command definitions
  - `skills/` - Custom skills (frontend-design)
  - `templates/` - Prompt templates

## Key File Locations

**Entry Points:**
- `start.py` - CLI menu launcher
- `start_ui.py` - Web UI launcher
- `autonomous_agent_demo.py` - Agent executor
- `ui/src/main.tsx` - React entry

**Configuration:**
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python tooling (Ruff, Mypy)
- `ui/package.json` - Node.js dependencies
- `ui/vite.config.ts` - Frontend build config
- `ui/tsconfig.json` - TypeScript config
- `.env.example` - Environment template

**Core Logic:**
- `agent.py` - Agent session loop
- `client.py` - Claude SDK client factory
- `security.py` - Bash command allowlist
- `prompts.py` - Prompt template loading
- `progress.py` - Progress tracking and DB queries
- `registry.py` - Project registry

**Testing:**
- `test_security.py` - Security hook tests

**Documentation:**
- `README.md` - Project documentation
- `CLAUDE.md` - Claude Code integration guide

## Naming Conventions

**Files:**
- Python: `snake_case.py` (e.g., `process_manager.py`, `spec_chat_session.py`)
- React: `PascalCase.tsx` for components (e.g., `AgentControl.tsx`, `KanbanBoard.tsx`)
- Hooks: `use{Feature}.ts` (e.g., `useProjects.ts`, `useWebSocket.ts`)
- Tests: `test_{module}.py` (e.g., `test_security.py`)

**Directories:**
- Lowercase with underscores for Python (`mcp_server/`, `api/`)
- Lowercase for frontend (`components/`, `hooks/`, `lib/`)
- Plural for collections (`routers/`, `services/`, `components/`)

**Special Patterns:**
- `__init__.py` for Python packages
- `index.ts` not used (direct imports)
- `*.template.md` for prompt templates in `.claude/templates/`

## Where to Add New Code

**New API Endpoint:**
- Primary code: `server/routers/{feature}.py`
- Schema: `server/schemas.py`
- Register: `server/routers/__init__.py`

**New React Component:**
- Implementation: `ui/src/components/{ComponentName}.tsx`
- Types: `ui/src/lib/types.ts`
- Use in: `ui/src/App.tsx` or parent component

**New React Hook:**
- Implementation: `ui/src/hooks/use{Feature}.ts`
- Types: `ui/src/lib/types.ts`

**New MCP Tool:**
- Implementation: `mcp_server/feature_mcp.py` (add tool function)
- Register: Add to MCP server in same file

**New Service:**
- Implementation: `server/services/{feature}.py`
- Import in: Relevant routers

**New Prompt Template:**
- Template: `.claude/templates/{name}.template.md`
- Loading: Via `prompts.py:load_prompt()`

## Special Directories

**ui/dist/**
- Purpose: Built React frontend
- Source: Generated by `npm run build`
- Committed: Yes (served by FastAPI in production)
- Note: Rebuild after UI changes

**venv/**
- Purpose: Python virtual environment
- Source: Created by `start_ui.py`
- Committed: No (in `.gitignore`)

**.planning/**
- Purpose: GSD planning and codebase documentation
- Source: Generated by `/gsd:map-codebase` and planning commands
- Committed: Yes (project documentation)

**~/.autocoder/**
- Purpose: Global user data
- Contains: `registry.db` (project name → path mapping)
- Location: User home directory

---

*Structure analysis: 2026-01-10*
*Update when directory structure changes*
