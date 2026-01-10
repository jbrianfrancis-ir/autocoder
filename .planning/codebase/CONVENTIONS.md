# Coding Conventions

**Analysis Date:** 2026-01-10

## Naming Patterns

**Files:**
- Python: `snake_case.py` (e.g., `process_manager.py`, `spec_chat_session.py`)
- React components: `PascalCase.tsx` (e.g., `AgentControl.tsx`, `KanbanBoard.tsx`)
- Hooks: `use{Feature}.ts` (e.g., `useProjects.ts`, `useWebSocket.ts`)
- Test files: `test_{module}.py` (e.g., `test_security.py`)

**Functions:**
- Python: `snake_case()` (e.g., `get_project_path()`, `load_prompt()`)
- TypeScript: `camelCase()` (e.g., `listProjects()`, `handleSelectProject()`)
- Event handlers: `handle{Event}` (e.g., `handleClick`, `handleKeyDown`)
- Async: No special prefix (use type hints instead)

**Variables:**
- Python: `snake_case` for variables
- TypeScript: `camelCase` for variables
- Constants: `UPPER_SNAKE_CASE` (e.g., `ALLOWED_COMMANDS`, `DEFAULT_MODEL`, `MAX_LOGS`)
- Private: Underscore prefix in Python (`_session_maker`, `_init_imports()`)

**Types:**
- Python classes: `PascalCase` (e.g., `Feature`, `RegistryError`)
- TypeScript interfaces: `PascalCase`, no I prefix (e.g., `Feature`, `ProjectSummary`)
- TypeScript types: `PascalCase` (e.g., `AgentStatus`, `WSMessage`)

## Code Style

**Formatting:**
- Python: 4 spaces indentation, 120 char line length (Ruff)
- TypeScript: 2 spaces indentation, no explicit line limit
- Python quotes: Double quotes `"` for strings
- TypeScript quotes: Single quotes `'` for imports, double for JSX

**Semicolons:**
- Python: Not used
- TypeScript: Used consistently

**Linting:**
- Python: Ruff for linting, Mypy for type checking (`pyproject.toml`)
- TypeScript: ESLint with TypeScript support (`ui/package.json`)
- Run: `ruff check .` (Python), `npm run lint` (TypeScript)

## Import Organization

**Python Order:**
1. Standard library (`import os`, `from pathlib import Path`)
2. Third-party packages (`from fastapi import ...`)
3. Local modules (`from registry import ...`)

**TypeScript Order:**
1. External packages (`import { useState } from 'react'`)
2. Internal modules (`import { api } from '../lib/api'`)
3. Types (`import type { Feature } from '../lib/types'`)

**Grouping:**
- Blank line between groups
- Alphabetical within each group (enforced by Ruff for Python)

**Path Aliases:**
- TypeScript: No path aliases configured (relative imports only)

## Error Handling

**Patterns:**
- Python: Raise exceptions, catch at API boundaries
- TypeScript: Try/catch for async operations, error boundaries for React
- FastAPI: `HTTPException` with appropriate status codes

**Error Types:**
- Python: Custom exceptions extend `Exception` (e.g., `RegistryError`, `RegistryNotFound`)
- Logging: `print()` to stdout/stderr (no structured logging)

**Async:**
- Python: `async/await` with `try/except`
- TypeScript: `async/await` with `try/catch`

## Logging

**Framework:**
- Python: Console via `print()` statements
- TypeScript: `console.log()`, `console.error()`

**Patterns:**
- Agent output streamed to WebSocket clients
- Secrets redacted before display (`server/services/process_manager.py`)
- No structured logging framework

**Where:**
- Log at API boundaries and error conditions
- Agent output captured and broadcast

## Comments

**When to Comment:**
- Explain "why", not "what"
- Document complex business logic
- Note security considerations
- Mark sections in large files

**Python Docstrings:**
```python
def function_name(param: str) -> str:
    """
    Brief description.

    Longer description if needed.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this happens
    """
```

**Section Separators:**
```python
# =============================================================================
# Section Name
# =============================================================================
```

**TypeScript:**
```typescript
// ============================================================================
// Section Name
// ============================================================================
```

**TODO Comments:**
- Format: `# TODO: description` (Python), `// TODO: description` (TypeScript)
- No username required (use git blame)

## Function Design

**Size:**
- Keep under 50-100 lines where practical
- Extract helpers for complex logic

**Parameters:**
- Python: Use type hints, keyword arguments for optional params
- TypeScript: Destructure objects in function signature
- Max 4-5 parameters before using options object

**Return Values:**
- Explicit return statements
- Return early for guard clauses
- Type hints on all public functions

## Module Design

**Exports:**
- Python: Import what you need directly
- TypeScript: Named exports preferred
- React components: Named exports (no default exports)

**Barrel Files:**
- Python: `__init__.py` for package imports
- TypeScript: Not used (direct imports)

**Lazy Imports:**
- Used to avoid circular dependencies
- Pattern: `_imports_initialized` flag with `_init_imports()` function
- See: `server/routers/projects.py`, `server/websocket.py`

## Type Hints

**Python:**
- Full type hints on all functions (Mypy strict mode)
- Use `Path` from pathlib for file paths
- Union types: `str | None` (modern syntax)
- Example: `def load_prompt(name: str, project_dir: Path | None = None) -> str:`

**TypeScript:**
- Strict mode enabled
- All props typed via interfaces
- Return types on functions

## React Patterns

**Components:**
```typescript
interface ComponentProps {
  required: string
  optional?: boolean
}

export function Component({ required, optional = false }: ComponentProps) {
  // Implementation
}
```

**Hooks:**
- Custom hooks return state and handlers
- Use React Query for server state
- WebSocket hooks for real-time updates

**State:**
- Local state: `useState`
- Server state: React Query
- Real-time: WebSocket subscriptions

---

*Convention analysis: 2026-01-10*
*Update when patterns change*
