# Blast Radius Documentation

**Last Updated:** 2026-01-11
**Applies to:** AutoCoder autonomous coding agent
**Related:** [COMMAND_AUDIT.md](./COMMAND_AUDIT.md) - Detailed command security analysis

## Executive Summary

This document describes the security posture and blast radius of the AutoCoder agent system. It answers: "If the agent is compromised, what can an attacker access?"

## Security Layers

AutoCoder implements defense-in-depth with multiple security layers:

### 1. Bash Command Allowlist (`security.py`)

**Total allowed commands:** 29

| Category | Commands |
|----------|----------|
| File inspection | `ls`, `cat`, `head`, `tail`, `wc`, `grep` |
| File operations | `cp`, `mkdir`, `chmod`, `mv`, `rm`, `touch` |
| Directory | `pwd` |
| Output | `echo` |
| Node.js | `npm`, `npx`, `pnpm`, `node` |
| Version control | `git` |
| Containers | `docker` |
| Process management | `ps`, `lsof`, `sleep`, `kill`, `pkill` |
| Network/API | `curl` |
| Shell scripts | `sh`, `bash`, `init.sh` |

**Extra validation required for:**
- `pkill`: Only allowed for dev processes (node, npm, npx, vite, next)
- `chmod`: Only allowed with `+x` mode (make executable)
- `init.sh`: Only allowed as `./init.sh`

### 2. Filesystem Sandbox (`server/routers/filesystem.py`)

**Blocked paths by platform:**
- **Linux:** `/etc`, `/var`, `/usr`, `/bin`, `/sbin`, `/boot`, `/proc`, `/sys`, `/dev`, `/root`, `/lib`, `/lib64`, `/run`, `/tmp`, `/opt`
- **macOS:** `/System`, `/Library`, `/private`, `/usr`, `/bin`, `/sbin`, `/etc`, `/var`, `/Volumes`, `/cores`, `/opt`
- **Windows:** `C:\Windows`, `C:\Program Files`, `C:\Program Files (x86)`, `C:\ProgramData`, `C:\System Volume Information`, `C:\$Recycle.Bin`, `C:\Recovery`

**Universal blocked (relative to home):**
- `.ssh`, `.aws`, `.gnupg`, `.config/gh`, `.netrc`, `.docker`, `.kube`, `.terraform`

**Hidden file patterns blocked:**
- `.env*`, `*.key`, `*.pem`, `*credentials*`, `*secrets*`

### 3. Network Access (`server/main.py`)

**Localhost-only middleware:**
- Requests only accepted from `127.0.0.1`, `::1`, and private IP ranges
- CORS restricted to localhost origins (ports 5173, 8888)
- No external network exposure by default

### 4. Symlink Protection (`server/routers/filesystem.py`)

**Symlink escape detection:**
- Checks symlinks BEFORE path resolution
- Blocks symlinks pointing outside base directory
- Prevents TOCTOU (time-of-check-time-of-use) attacks

### 5. Resource Limits (`security.py`)

**Available via `apply_resource_limits()` function:**

| Resource | Limit | Purpose |
|----------|-------|---------|
| CPU time | 300 seconds | Prevent CPU exhaustion attacks |
| Virtual memory | 1 GB | Prevent memory exhaustion |
| File size | 100 MB | Prevent disk space exhaustion |
| Max processes | 50 | Prevent fork bomb attacks |

**Usage:** Pass as `preexec_fn` to `subprocess.run()` or `subprocess.Popen()`.

**Platform notes:** Only effective on Unix systems (Linux, macOS). Windows is a no-op.

### 6. Environment Sanitization (`security.py`)

**Available via `get_safe_environment()` function:**

Provides minimal environment for subprocess execution, preventing credential leakage.

**Variables passed through:**
- Essential: `PATH`, `LANG`, `HOME`, `TERM`
- Development: `NODE_ENV`, `PYTHONPATH`, `PYTHON_PATH`
- Caches: `npm_config_cache`, `XDG_CACHE_HOME`
- Terminal: `COLORTERM`, `FORCE_COLOR`

**Variables explicitly excluded:**
- API keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.
- Cloud credentials: `AWS_*`, `AZURE_*`, `GCP_*`
- Database: `DATABASE_URL`, `DB_PASSWORD`
- Tokens: `GITHUB_TOKEN`, `GITLAB_TOKEN`
- SSH/GPG: `SSH_*`, `GPG_*`

## How to Wire In Security Helpers

This section provides step-by-step instructions for integrating the resource limits and environment sanitization helpers into subprocess calls.

### 7.1 Integration Points Overview

| Location | Priority | Description |
|----------|----------|-------------|
| `server/services/process_manager.py:258` | **HIGH** | Primary agent subprocess launch point |
| `start.py:220` | MEDIUM | Claude CLI launch via `subprocess.run()` |
| `start.py:372` | MEDIUM | CLI agent run via `subprocess.run()` |
| `client.py:161-173` | MEDIUM | MCP server environment configuration |
| `start_ui.py` | LOW | Development server launchers |

**Primary target:** `server/services/process_manager.py:258` - This is where the UI launches agent subprocesses. All agent activity runs through this path, making it the highest-priority integration point.

### 7.2 Wiring Resource Limits

**Step 1: Add import**

```python
from security import apply_resource_limits
```

**Step 2: Locate the integration point**

File: `server/services/process_manager.py`
Line: 258 (inside `AgentProcessManager.start()` method)

**Step 3: Add `preexec_fn` parameter**

Before:
```python
self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
)
```

After:
```python
from security import apply_resource_limits

self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
    preexec_fn=apply_resource_limits,  # Apply resource limits
)
```

**Platform Note:** `apply_resource_limits()` is a no-op on Windows. On Linux/macOS, it sets:
- CPU time: 300 seconds
- Virtual memory: 1 GB
- File size: 100 MB
- Max processes: 50

**Verification:**

On Linux, verify limits are applied:
```bash
cat /proc/{pid}/limits | grep -E "(Max cpu time|Max address space|Max file size|Max processes)"
```

### 7.3 Wiring Environment Sanitization

**Step 1: Add imports**

```python
import os
from security import get_safe_environment
```

**Step 2: Locate the integration point**

File: `server/services/process_manager.py`
Line: 258 (inside `AgentProcessManager.start()` method)

**Step 3: Build safe environment and add required keys**

**CRITICAL:** The agent subprocess needs `ANTHROPIC_API_KEY` to function. The `get_safe_environment()` function intentionally excludes API keys for security. You must explicitly add it back.

Before:
```python
self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
)
```

After:
```python
import os
from security import get_safe_environment

safe_env = get_safe_environment(project_dir=str(self.project_dir))
safe_env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")

self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
    env=safe_env,  # Use sanitized environment
)
```

**Verification:**

Add temporary logging to confirm sanitization:
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Safe env keys: %s", list(safe_env.keys()))
```

Expected keys: `PATH`, `LANG`, `HOME`, `TERM`, `ANTHROPIC_API_KEY`, plus any development variables present in parent environment.

### 7.4 Combined Wiring (Both Helpers)

For maximum security, apply both helpers together:

```python
import os
from security import apply_resource_limits, get_safe_environment

# Build sanitized environment
safe_env = get_safe_environment(project_dir=str(self.project_dir))
safe_env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")

self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
    preexec_fn=apply_resource_limits,  # Resource limits (Unix only)
    env=safe_env,  # Sanitized environment
)
```

### 7.5 Secondary Integration Points

These points are lower priority but may benefit from the helpers in specific scenarios.

**`start.py:220` - Claude CLI launch**
- Priority: MEDIUM
- Context: Interactive spec creation via `subprocess.run(["claude", ...])`
- Recommendation: Not critical since this is user-initiated and short-lived
- If desired: Add `preexec_fn=apply_resource_limits`

**`start.py:372` - CLI agent run**
- Priority: MEDIUM
- Context: Direct CLI agent launch via `subprocess.run()`
- Recommendation: Same as above - user-initiated
- If desired: Same pattern as Section 7.4

**`client.py:161-173` - MCP server environment**
- Priority: MEDIUM
- Context: MCP servers receive `env=os.environ` (inherits everything)
- Current code:
  ```python
  "env": {
      **os.environ,
      "PROJECT_DIR": str(project_dir.resolve()),
      "PYTHONPATH": str(Path(__file__).parent.resolve()),
  },
  ```
- Recommendation: Consider using `get_safe_environment()` as base, then add required vars
- Tradeoff: MCP servers may need more environment access than agent subprocess
- If desired:
  ```python
  from security import get_safe_environment
  safe_env = get_safe_environment(project_dir=str(project_dir))
  safe_env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")
  safe_env["PROJECT_DIR"] = str(project_dir.resolve())
  safe_env["PYTHONPATH"] = str(Path(__file__).parent.resolve())
  # ... use safe_env in MCP config
  ```

**`start_ui.py` - Development servers**
- Priority: LOW
- Context: Local development only, launches npm/python dev servers
- Recommendation: Not needed - development servers are trusted
- Note: These are for local development, not production

### 7.6 Testing Verification

After integrating the helpers, verify everything works:

**1. Resource Limits (Linux/macOS only)**
```bash
# Start agent via UI, get PID from logs
cat /proc/{pid}/limits
```

Look for configured limits (300 sec CPU, 1GB memory, etc.)

**2. Environment Sanitization**
```bash
# Add temporary logging in process_manager.py:
logger.info("Environment keys: %s", list(safe_env.keys()))
# Check logs for expected keys
```

Expected: `PATH`, `LANG`, `HOME`, `TERM`, `ANTHROPIC_API_KEY`, plus any `ALLOWED_ENV_VARS` present

**3. Agent Functionality**
- Start agent from UI
- Verify agent can still:
  - Initialize features from spec
  - Run npm/npx commands
  - Execute allowed bash commands
  - Access the Claude API (requires `ANTHROPIC_API_KEY`)

**4. Security Validation**
- Verify agent does NOT have access to:
  - `AWS_*` credentials
  - `GITHUB_TOKEN`
  - Other sensitive environment variables

## Blast Radius

### If Agent is Compromised, Attacker CAN:

| Access | Details |
|--------|---------|
| Execute 29 whitelisted commands | Within project directory only |
| Read/write files in project directory | Unrestricted within sandbox |
| Access environment variables | Visible to Python process |
| Make network requests | No outbound restrictions via curl |
| Access API keys in environment | If passed via env vars |
| Run Node.js code | Via npm/npx/node commands |
| Run shell scripts | Via sh/bash (still command-restricted) |
| Access Docker | Can manage containers if Docker is running |

### If Agent is Compromised, Attacker CANNOT:

| Restriction | Enforcement |
|-------------|-------------|
| Execute arbitrary commands | Blocked by allowlist (`security.py`) |
| Access files outside project | Blocked by filesystem sandbox |
| Access sensitive directories | `.ssh`, `.aws`, etc. explicitly blocked |
| Modify system files | No sudo/su access |
| Install system packages | apt/yum not in allowlist |
| Access Windows system folders | Blocked by platform-specific lists |
| Escape via symlinks | Symlink escape detection |
| Access network shares | UNC paths blocked |

## Risk Assessment

### High-Risk Operations (Allowed)

| Risk | Mitigation |
|------|------------|
| `rm` can delete project files | User can restore from git |
| `curl` can exfiltrate data | Monitor network traffic |
| `docker` access | Container isolation; watch for privileged containers |
| `git push` | Code review before accepting agent PRs |
| Environment variable access | Don't pass production secrets |

### Known Gaps

| Gap | Status | Mitigation |
|-----|--------|------------|
| No outbound network filtering | Deferred | Run in network-isolated environment for sensitive projects |
| Resource limits not wired in | Documented | See [Section 7.2](#72-wiring-resource-limits) for step-by-step integration instructions |
| Environment sanitization not wired in | Documented | See [Section 7.3](#73-wiring-environment-sanitization) for step-by-step integration instructions |
| HIGH-risk commands lack deep validation | Documented | See [COMMAND_AUDIT.md](./COMMAND_AUDIT.md) - bash/node/npm/docker have code execution capability |
| Silent exception handling in WebSocket | Known issue | Structured logging implemented (Phase 6) |
| No structured logging framework | Resolved | Implemented in Phase 6 - see logging configuration in `logging_config.py` |

## Recommendations

### For Production Use

1. **Run in isolated VM or container** - Adds another security layer
2. **Use dedicated project directories** - Don't run agent in home directory
3. **Audit environment variables** - Only pass required credentials
4. **Review agent-created code** - Before committing/deploying
5. **Monitor network traffic** - Watch for unexpected outbound connections

### For Development Use

1. **Current security is appropriate** - Defense-in-depth for dev workloads
2. **YOLO mode acceptable** - When prototyping in isolated environments
3. **Keep project isolated** - Each project in its own directory

## Version History

| Date | Change |
|------|--------|
| 2026-01-11 | Initial documentation |
| 2026-01-11 | Added resource limits helper (Section 5) |
| 2026-01-11 | Added environment sanitization helper (Section 6) |
| 2026-01-11 | Added reference to COMMAND_AUDIT.md |
| 2026-01-11 | Updated known gaps with helper status |
| 2026-01-16 | Added "How to Wire In Security Helpers" section (Section 7) |
| 2026-01-16 | Updated known gaps: resource limits and env sanitization now documented |
| 2026-01-16 | Updated known gaps: structured logging resolved (Phase 6) |

---

*Security is a process, not a destination. This document should be reviewed and updated as the system evolves.*
