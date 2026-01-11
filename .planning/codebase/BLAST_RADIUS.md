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
| Resource limits not wired in | Helper ready | `apply_resource_limits()` available but not yet integrated into agent subprocess calls |
| Environment sanitization not wired in | Helper ready | `get_safe_environment()` available but not yet integrated into agent subprocess calls |
| HIGH-risk commands lack deep validation | Documented | See [COMMAND_AUDIT.md](./COMMAND_AUDIT.md) - bash/node/npm/docker have code execution capability |
| Silent exception handling in WebSocket | Known issue | Structured logging (future) |
| No structured logging framework | Known issue | Add in future phase |

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

---

*Security is a process, not a destination. This document should be reviewed and updated as the system evolves.*
