# Phase 7 Research: Security Documentation

**Researched:** 2026-01-16
**Domain:** Security helper documentation and integration guidance
**Confidence:** HIGH - Based on direct codebase analysis

## Summary

This research documents the existing security helpers in the autocoder codebase and identifies the exact integration points where they should be wired in. The codebase has a well-designed security architecture with two helpers (`apply_resource_limits()` and `get_safe_environment()`) that are fully implemented in `security.py` but not yet integrated into the subprocess calls that run agent processes.

The existing BLAST_RADIUS.md provides good high-level security documentation, but lacks the specific "how to wire in" guidance that developers need to actually integrate these helpers. Phase 7 focuses on documenting exact code locations and step-by-step wiring instructions.

**Primary recommendation:** Document precise file:line integration points and provide copy-paste-ready code snippets for each helper.

## Existing Security Helpers

### Resource Limit Helper

**Location:** `/home/brianf/dev/autocoder/security.py:33-78`

**Function:** `apply_resource_limits()`

**Purpose:** Pre-exec function to apply resource limits to subprocess execution. Prevents runaway processes from consuming system resources.

**Limits Applied (Unix only):**
| Resource | Limit | Purpose |
|----------|-------|---------|
| `RLIMIT_CPU` | 300 seconds | Prevent CPU exhaustion attacks |
| `RLIMIT_AS` | 1 GB | Prevent memory exhaustion |
| `RLIMIT_FSIZE` | 100 MB | Prevent disk space exhaustion |
| `RLIMIT_NPROC` | 50 processes | Prevent fork bomb attacks |

**Configuration:** `RESOURCE_LIMITS` dict at `security.py:25-30`

**Platform Notes:**
- Works on Linux and macOS via Python's `resource` module
- Windows: No-op (resource module not available)

**Usage Pattern:**
```python
from security import apply_resource_limits

subprocess.Popen(
    cmd,
    preexec_fn=apply_resource_limits,  # <-- Add this parameter
    stdout=subprocess.PIPE,
    ...
)
```

### Environment Sanitization Helper

**Location:** `/home/brianf/dev/autocoder/security.py:81-138`

**Function:** `get_safe_environment(project_dir: str | None = None) -> dict[str, str]`

**Purpose:** Create a sanitized environment dictionary for subprocess execution, preventing credential leakage from parent process.

**Variables INCLUDED (allowlist):**
| Category | Variables |
|----------|-----------|
| Essential | `PATH`, `LANG`, `HOME`, `TERM` |
| Development | `NODE_ENV`, `PYTHONPATH`, `PYTHON_PATH` |
| Package caches | `npm_config_cache`, `XDG_CACHE_HOME` |
| Terminal | `COLORTERM`, `FORCE_COLOR` |

**Variables EXCLUDED (blocked):**
- API keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.
- Cloud credentials: `AWS_*`, `AZURE_*`, `GCP_*`
- Database: `DATABASE_URL`, `DB_PASSWORD`
- Tokens: `GITHUB_TOKEN`, `GITLAB_TOKEN`
- SSH/GPG: `SSH_*`, `GPG_*`

**Configuration:** `ALLOWED_ENV_VARS` set at `security.py:83-94`

**Usage Pattern:**
```python
from security import get_safe_environment

subprocess.Popen(
    cmd,
    env=get_safe_environment(project_dir=str(project_path)),  # <-- Add this parameter
    cwd=str(project_path),
    ...
)
```

## Integration Points

### Files That Could Use Resource Limits

#### 1. `server/services/process_manager.py:258`

**What it does:** Spawns the autonomous agent subprocess via `AgentProcessManager.start()`

**Current code:**
```python
self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
)
```

**Why it needs limits:** This is the PRIMARY integration point. The agent subprocess can run for extended periods, execute npm install, node commands, etc. Resource limits would prevent:
- CPU-bound infinite loops
- Memory exhaustion from large npm installs
- Fork bombs from malicious package scripts

**Priority:** HIGH - This is the most important integration point.

#### 2. `start.py:220`

**What it does:** Launches Claude Code CLI for interactive spec creation

**Current code:**
```python
subprocess.run(
    ["claude", f"/create-spec {project_dir}"],
    check=False,
    cwd=str(Path(__file__).parent)
)
```

**Why it needs limits:** User-initiated, interactive process. Lower risk but could still benefit from resource limits.

**Priority:** MEDIUM - Interactive process with user oversight.

#### 3. `start.py:372`

**What it does:** Runs the autonomous agent directly from CLI

**Current code:**
```python
subprocess.run(cmd, check=False)
```

**Why it needs limits:** Similar to process_manager.py but for CLI usage.

**Priority:** MEDIUM - Duplicate of process_manager.py path.

#### 4. `start_ui.py:165`, `start_ui.py:177`, `start_ui.py:190`

**What it does:** Launches backend (FastAPI) and frontend (Vite) servers

**Why it might need limits:** Development servers, generally trusted. Resource limits could prevent accidental resource exhaustion.

**Priority:** LOW - Trusted local development servers.

### Files That Could Use Environment Sanitization

#### 1. `server/services/process_manager.py:258`

**What it does:** Spawns agent subprocess with inherited environment

**Current code:**
```python
self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
    # NOTE: No env= parameter, inherits full environment
)
```

**Why it needs sanitization:** The agent subprocess inherits ALL environment variables from the server process, including:
- `ANTHROPIC_API_KEY` (needed but should be explicit)
- Any cloud credentials in the environment
- SSH keys, GitHub tokens, etc.

**CRITICAL CONSIDERATION:** The agent NEEDS `ANTHROPIC_API_KEY` to function. The `get_safe_environment()` function does NOT include this by default. The integration will need to either:
1. Add `ANTHROPIC_API_KEY` to `ALLOWED_ENV_VARS`
2. Explicitly pass it in the env dict after calling `get_safe_environment()`
3. Create a separate `get_agent_environment()` function

**Priority:** HIGH - Primary integration point for credential protection.

#### 2. `client.py:161-173` (MCP server config)

**What it does:** Configures environment for MCP server subprocess

**Current code:**
```python
mcp_servers = {
    "features": {
        "command": sys.executable,
        "args": ["-m", "mcp_server.feature_mcp"],
        "env": {
            **os.environ,  # <-- Inherits FULL environment
            "PROJECT_DIR": str(project_dir.resolve()),
            "PYTHONPATH": str(Path(__file__).parent.resolve()),
        },
    },
}
```

**Why it needs sanitization:** MCP servers currently inherit the full environment. While feature_mcp.py is trusted code, it doesn't need cloud credentials.

**Priority:** MEDIUM - MCP server is internal/trusted, but defense-in-depth applies.

#### 3. `start_ui.py:175-179`

**What it does:** Sets up environment for Vite frontend

**Current code:**
```python
vite_env = os.environ.copy()
vite_env["VITE_API_PORT"] = str(port)
frontend = subprocess.Popen([
    npm_cmd, "run", "dev"
], cwd=str(UI_DIR), env=vite_env)
```

**Why it needs sanitization:** Frontend dev server gets full environment. Less critical but could leak secrets in Vite's process.

**Priority:** LOW - Development server, local use only.

## Current Security Implementation

### Defense-in-Depth Layers

The codebase implements multiple security layers, as documented in `BLAST_RADIUS.md`:

1. **Bash Command Allowlist** (`security.py:141-188`)
   - 29 whitelisted commands
   - Extra validation for `pkill`, `chmod`, `init.sh`
   - Implemented via `bash_security_hook()` async function

2. **Security Hook Integration** (`client.py:190-194`)
   - Hooks registered on ClaudeSDKClient
   - Pre-tool-use validation for Bash commands

3. **Filesystem Sandbox** (`client.py:107-113`, `client.py:130-136`)
   - Relative paths restrict to project directory
   - OS-level sandbox enabled
   - Permissions explicitly granted for allowed operations

4. **CORS and Localhost Restriction** (`server/main.py`)
   - Server only accepts localhost connections
   - CORS restricted to specific origins

### Gap Analysis

The existing BLAST_RADIUS.md identifies these helpers as "ready but not wired in":

```
| Gap | Status | Mitigation |
|-----|--------|------------|
| Resource limits not wired in | Helper ready | `apply_resource_limits()` available but not yet integrated |
| Environment sanitization not wired in | Helper ready | `get_safe_environment()` available but not yet integrated |
```

This confirms that Phase 7's task is to document HOW to wire these in, not to implement new helpers.

## Blast Radius Analysis

### What Could Go Wrong If Helpers Not Wired In

**Without Resource Limits:**
| Attack Vector | Impact | Likelihood |
|---------------|--------|------------|
| CPU exhaustion (infinite loop) | System hang, requires manual kill | Low - agent usually well-behaved |
| Memory exhaustion (npm install malicious package) | OOM killer activates | Low - requires compromised package |
| Fork bomb (malicious install script) | System unusable | Very low - unlikely in normal use |
| Large file creation | Disk full | Low - filesystem sandbox limits impact |

**Without Environment Sanitization:**
| Attack Vector | Impact | Likelihood |
|---------------|--------|------------|
| API key exfiltration via curl | Attacker gets Anthropic API key | Medium - if curl to attacker server |
| Cloud credential leakage | AWS/Azure/GCP access compromised | Low - depends on user's env setup |
| Token theft in package scripts | GitHub/GitLab token stolen | Low - requires malicious dependency |

### Trust Boundaries

```
+------------------+
|  User's Machine  |
|  (full env vars) |
+--------+---------+
         |
         v
+--------+---------+
| Server Process   |
| (FastAPI/uvicorn)|  <-- Has ANTHROPIC_API_KEY
| (full env vars)  |
+--------+---------+
         |
         v
+--------+---------+
| Agent Subprocess |  <-- Currently inherits full env
| (autonomous_agent|      Should have sanitized env
|  _demo.py)       |
+--------+---------+
         |
         v
+--------+---------+
| Claude SDK /     |  <-- Executes bash commands
| Claude CLI       |      Commands go through allowlist
+--------+---------+
         |
         v
+--------+---------+
| MCP Servers      |  <-- Currently inherits full env
| (feature_mcp.py) |      Should have minimal env
+------------------+
```

## Key Findings

### Finding 1: Single Critical Integration Point

The PRIMARY integration point is `server/services/process_manager.py:258`. This is where 90% of the security benefit comes from wiring in both helpers.

### Finding 2: ANTHROPIC_API_KEY Must Be Preserved

The `get_safe_environment()` function does NOT include `ANTHROPIC_API_KEY`, but the agent subprocess NEEDS it. The documentation must explain how to add it explicitly or modify the helper.

**Recommendation:** Add `ANTHROPIC_API_KEY` to the safe environment explicitly when calling the helper:
```python
safe_env = get_safe_environment(project_dir=str(self.project_dir))
safe_env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")
```

### Finding 3: Platform-Specific Behavior

`apply_resource_limits()` is a no-op on Windows. Documentation should clearly state this and note that Windows users do not get resource protection.

### Finding 4: MCP Server Environment Needs Special Handling

The MCP server in `client.py` passes `**os.environ` which includes sensitive variables. However, changing this requires careful testing since MCP servers have their own environment requirements.

### Finding 5: Existing Tests for Security

`test_security.py` exists and tests command allowlist logic but does NOT test:
- `apply_resource_limits()` function
- `get_safe_environment()` function

## Documentation Gap Analysis

### What BLAST_RADIUS.md Currently Has
- High-level description of security layers
- Lists of allowed/blocked items
- Risk assessment tables
- Gap identification

### What BLAST_RADIUS.md Is Missing
- Exact file:line locations for integration
- Copy-paste-ready code snippets
- Step-by-step wiring instructions
- Testing verification steps
- Platform-specific considerations

## Sources

### Primary (HIGH confidence)
- `/home/brianf/dev/autocoder/security.py` - Direct code inspection
- `/home/brianf/dev/autocoder/server/services/process_manager.py` - Direct code inspection
- `/home/brianf/dev/autocoder/client.py` - Direct code inspection
- `/home/brianf/dev/autocoder/.planning/codebase/BLAST_RADIUS.md` - Existing documentation
- `/home/brianf/dev/autocoder/.planning/codebase/CONCERNS.md` - Existing documentation
- `/home/brianf/dev/autocoder/.planning/codebase/COMMAND_AUDIT.md` - Command security audit

## Metadata

**Confidence breakdown:**
- Existing helpers: HIGH - Direct code inspection
- Integration points: HIGH - Direct code inspection
- Blast radius: HIGH - Based on existing BLAST_RADIUS.md and code review

**Research date:** 2026-01-16
**Valid until:** Indefinite - codebase-specific research
