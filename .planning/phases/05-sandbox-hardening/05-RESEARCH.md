# Phase 5: Sandbox Hardening - Research

**Researched:** 2026-01-11
**Domain:** AI agent code execution security and process isolation
**Confidence:** HIGH

<research_summary>
## Summary

Researched security patterns for autonomous AI agents executing code. The current AutoCoder implementation uses a command allowlist approach which is a good first layer, but modern agent security requires defense-in-depth with multiple isolation boundaries.

Key finding: Python language-level sandboxing is fundamentally broken. Security experts consistently recommend OS-level isolation (containers, VMs, seccomp) rather than trying to restrict Python's dynamic features. The current allowlist approach is necessary but not sufficient.

Ralph Wiggum principle applies: "It's not if it gets popped, it's when. And what is the blast radius?" Focus should be on containment and limiting damage rather than perfect prevention.

**Primary recommendation:** Layer existing allowlist with container isolation for high-risk operations. Document blast radius explicitly. Address CORS and credential handling gaps identified in CONCERNS.md.
</research_summary>

<standard_stack>
## Standard Stack

The established tools for AI agent sandboxing:

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Docker | 24+ | Container isolation | Standard LXC-based isolation, minimal performance overhead |
| seccomp | (kernel) | System call filtering | Linux kernel feature, restricts dangerous syscalls |
| gVisor | Latest | User-space kernel | Extra isolation layer, intercepts syscalls |
| AppArmor | (kernel) | Mandatory access control | Profile-based restriction of file/network access |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| Firecracker | 1.x | microVM isolation | When hardware-level isolation needed (like E2B) |
| microsandbox | 0.4+ | Python sandbox SDK | For sandboxing Python code execution specifically |
| CodeJail | Latest | Python exec sandbox | OpenEdX's solution using AppArmor + resource limits |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Full Docker | subprocess + seccomp | Less isolation but simpler for simple commands |
| gVisor | Plain Docker | Plain Docker faster but less syscall filtering |
| On-prem sandbox | E2B/Fly Sprites | Cloud services add latency but provide strong isolation |

**Current AutoCoder Approach:**
```python
# Already implemented in security.py
ALLOWED_COMMANDS = {"ls", "cat", "npm", "git", ...}  # 57 commands

# Additional validation for sensitive commands
COMMANDS_NEEDING_EXTRA_VALIDATION = {"pkill", "chmod", "init.sh"}
```

This allowlist approach is good but should be supplemented with OS-level controls.
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Claude API (trusted)                                        │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  AutoCoder Agent Harness                                     │
│  - Command allowlist validation (security.py)                │
│  - Pre-execution hooks                                       │
│  - Output sanitization (secret redaction)                    │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  [LAYER 2] Sandbox/Container (NEW)                          │
│  - Filesystem isolation to project directory                 │
│  - Resource limits (CPU, memory, time)                       │
│  - Network restrictions (optional)                           │
│  - Non-root execution                                        │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Project Directory                                           │
│  - Source code                                               │
│  - features.db (SQLite)                                      │
│  - specs/ directory                                          │
└─────────────────────────────────────────────────────────────┘
```

### Pattern 1: Defense in Depth
**What:** Multiple layers of security controls
**When to use:** Always for production agents
**Layers:**
1. Input validation (command allowlist) - current
2. Process isolation (container/seccomp) - add
3. Filesystem restriction - partially current
4. Network control - not current
5. Credential isolation - not current
6. Output sanitization - current (secret redaction)

### Pattern 2: Blast Radius Documentation
**What:** Explicit documentation of what an escaped agent can access
**When to use:** Before production deployment
**Example:**
```markdown
## Blast Radius (AutoCoder)

**If agent is compromised, attacker can:**
- Execute 57 whitelisted commands within project directory
- Read/write files in project directory only
- Access environment variables visible to Python process
- Make network requests (no restrictions currently)
- Access any API keys passed via environment

**Attacker CANNOT:**
- Execute arbitrary commands (blocked by allowlist)
- Access files outside project directory (blocked by security.py)
- Modify system files (no sudo/su access)
- Install system packages (apt/yum not in allowlist)
```

### Pattern 3: Resource Limits
**What:** Prevent denial-of-service via resource exhaustion
**When to use:** Always
**Example using setrlimit:**
```python
import resource

def set_resource_limits():
    """Apply limits before subprocess execution."""
    # CPU time limit: 300 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
    # Memory limit: 1GB
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
    # File size limit: 100MB
    resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))
```

### Anti-Patterns to Avoid
- **Python language-level sandboxing:** Python's object system makes language-level sandboxing impossible to secure. Experts consistently recommend OS-level isolation instead.
- **Trusting allowlist alone:** Allowlists prevent obvious attacks but can be bypassed via allowed command features (e.g., `git config --global alias.x '!malicious'`).
- **Shared credentials:** Static API keys with broad permissions. Use short-lived tokens or scoped credentials.
- **shell=True without escaping:** Always use list arguments with subprocess, not shell strings.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Python code sandboxing | Custom AST validation | Container isolation or microsandbox | Python's introspection defeats any language-level sandbox |
| System call filtering | Custom syscall intercept | seccomp-bpf via Docker/gVisor | Kernel-level filtering is battle-tested |
| Resource limiting | Custom monitoring | setrlimit or cgroups | OS primitives handle edge cases |
| Secret detection | Custom regex patterns | gitleaks, trufflehog | Existing tools have comprehensive pattern libraries |
| Credential management | Env vars in code | Secret managers (Vault, AWS Secrets) | Proper rotation, audit, scoping |

**Key insight:** OS-level isolation mechanisms have decades of security research behind them. Custom sandboxing solutions consistently fail when exposed to determined attackers. The Python ecosystem specifically has a history of sandbox escapes (e.g., CVE-2025-9959 smolagents).
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Python Sandbox Escape via Introspection
**What goes wrong:** Attacker uses `__class__.__mro__` chain to escape restricted namespace
**Why it happens:** Python's object model provides multiple paths to access builtins
**How to avoid:** Don't rely on Python-level sandboxing. Use OS-level isolation.
**Warning signs:** Code using restricted exec/eval without container boundary
**Reference:** [The Glass Sandbox - Checkmarx](https://checkmarx.com/zero-post/glass-sandbox-complexity-of-python-sandboxing/)

### Pitfall 2: Command Injection via Allowed Commands
**What goes wrong:** Allowed commands have features that enable arbitrary code execution
**Why it happens:** Commands like `git`, `npm`, `node` can all execute arbitrary code
**How to avoid:** Layer allowlist with additional argument validation; use subprocess with list args
**Warning signs:** `shell=True` in subprocess calls, unvalidated user input in command args
**Current status:** AutoCoder validates pkill/chmod/init.sh specially, but git/npm are unrestricted

### Pitfall 3: Symlink Attack on Filesystem Boundary
**What goes wrong:** Agent creates symlink in project dir pointing to sensitive file outside
**Why it happens:** Path.resolve() follows symlinks before boundary check
**How to avoid:** Check for symlinks before resolving; use realpath validation
**Warning signs:** Path operations without explicit symlink checks
**Current status:** CONCERNS.md notes this issue in filesystem.py

### Pitfall 4: Environment Variable Leakage
**What goes wrong:** API keys/secrets accessible to compromised agent
**Why it happens:** Process inherits parent environment by default
**How to avoid:** Sanitize environment before subprocess; use scoped/short-lived tokens
**Warning signs:** `os.environ` passed directly to subprocesses

### Pitfall 5: CORS Allowing Unauthorized Access
**What goes wrong:** Malicious website can make requests to local agent API
**Why it happens:** `allow_origins=["*"]` accepts any origin
**How to avoid:** Restrict to specific origins or implement proper CSRF protection
**Warning signs:** CORS set to `*` in production
**Current status:** CONCERNS.md notes this issue in server/main.py:59
</common_pitfalls>

<code_examples>
## Code Examples

Verified patterns from official sources:

### Subprocess with List Arguments (Not Shell)
```python
# Source: OpenStack Security Guidelines
import subprocess

# GOOD: List arguments, no shell
subprocess.run(["git", "status"], cwd=project_dir, check=True)

# BAD: Shell string, vulnerable to injection
subprocess.run(f"git status {user_input}", shell=True)  # NEVER
```

### Resource Limits with setrlimit
```python
# Source: Python documentation / CodeJail patterns
import resource

def apply_limits(cpu_seconds=300, memory_bytes=1024*1024*1024):
    """Pre-exec function to apply resource limits."""
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))  # Limit child processes

# Use with subprocess
subprocess.run(
    ["python", "script.py"],
    preexec_fn=apply_limits
)
```

### Symlink-Safe Path Resolution
```python
# Source: Security best practices
from pathlib import Path

def safe_resolve(base_path: Path, user_path: str) -> Path | None:
    """Resolve path safely, rejecting symlinks that escape base."""
    full_path = base_path / user_path

    # Check for symlinks BEFORE resolving
    if full_path.is_symlink():
        target = full_path.resolve()
        if not target.is_relative_to(base_path):
            return None  # Symlink escapes boundary

    resolved = full_path.resolve()
    if not resolved.is_relative_to(base_path.resolve()):
        return None  # Path escapes boundary

    return resolved
```

### Sanitized Environment for Subprocess
```python
# Source: Security best practices
import os

def get_safe_env(project_dir: str) -> dict:
    """Create sanitized environment for subprocess."""
    # Start with minimal environment
    safe_env = {
        "PATH": "/usr/bin:/bin",
        "HOME": project_dir,
        "LANG": "C.UTF-8",
    }

    # Add only explicitly needed project variables
    for key in ["NODE_ENV", "PYTHON_PATH"]:
        if key in os.environ:
            safe_env[key] = os.environ[key]

    return safe_env
```

### CORS Restriction
```python
# Source: FastAPI documentation
from fastapi.middleware.cors import CORSMiddleware

# GOOD: Specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BAD: Wildcard (current AutoCoder state)
# allow_origins=["*"]  # Accepts ANY origin
```
</code_examples>

<sota_updates>
## State of the Art (2025-2026)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Python RestrictedPython | Container/VM isolation | 2024+ | Language-level sandboxing proven insecure |
| Static API keys | Short-lived tokens (Akeyless, JITA) | 2025 | Reduces blast radius of key compromise |
| Docker alone | Docker + gVisor/seccomp | 2024+ | Additional syscall filtering layer |
| Localhost binding | Zero-trust networking | 2025 | Assume network is hostile |

**New tools/patterns to consider:**
- **OWASP Top 10 for Agentic Applications** (Dec 2025): New framework specifically for AI agent security
- **E2B Sandboxes:** Firecracker microVMs with <200ms startup
- **microsandbox:** Python SDK for hardware-isolated code execution
- **MCP Security Patterns:** Standardized tool interfaces with security boundaries

**Deprecated/outdated:**
- **Python exec() sandboxing:** Proven bypassable via introspection
- **Static allowlist only:** Insufficient without additional layers
- **Trust in LLM output:** LLMs can be manipulated via prompt injection
</sota_updates>

<open_questions>
## Open Questions

1. **Container overhead for every command?**
   - What we know: Containers add latency but provide strong isolation
   - What's unclear: Performance impact on agent iteration speed
   - Recommendation: Profile with and without container isolation; consider container-per-session vs container-per-command

2. **Network isolation tradeoffs?**
   - What we know: Agent needs npm/pip access, API calls
   - What's unclear: How to allow needed access while blocking exfiltration
   - Recommendation: Consider allowlisted domains or proxy approach

3. **Credential scoping for multi-project?**
   - What we know: Current design has one agent per project
   - What's unclear: How credentials should be isolated between projects
   - Recommendation: Start with per-project credential isolation before multi-project
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) - Official security framework
- [Docker Security Best Practices](https://github.com/docker/docs) via Context7 - Container hardening
- [microsandbox documentation](https://github.com/microsandbox/microsandbox) via Context7 - Python sandboxing SDK
- [Ralph Wiggum methodology](https://github.com/ghuntley/how-to-ralph-wiggum) - Agent architecture patterns

### Secondary (MEDIUM confidence)
- [Setting Up a Secure Python Sandbox for LLM Agents](https://dida.do/blog/setting-up-a-secure-python-sandbox-for-llm-agents) - Verified against Docker docs
- [Code Sandboxes for LLMs and AI Agents](https://amirmalik.net/2025/03/07/code-sandboxes-for-llm-ai-agents) - Overview of approaches
- [OpenStack subprocess security guidelines](https://security.openstack.org/guidelines/dg_use-subprocess-securely.html) - Verified patterns
- [Common Risks of Giving Your API Keys to AI Agents](https://auth0.com/blog/api-key-security-for-ai-agents/) - Credential security

### Tertiary (LOW confidence - needs validation during implementation)
- [CVE-2025-4609 Chromium sandbox escape](https://www.ox.security/blog/the-aftermath-of-cve-2025-4609-critical-sandbox-escape-leaves-1-5m-developers-vulnerable/) - Recent vulnerability context
- [Smolagents sandbox escape CVE-2025-9959](https://research.jfrog.com/vulnerabilities/smolagents-local-python-sandbox-escape-jfsa-2025-001434277/) - Python sandbox failure example
</sources>

<action_items>
## Concrete Action Items for Phase 5

Based on research, recommended implementation:

### Priority 1: Quick Wins (Low effort, high impact)
1. **Fix CORS** - Replace `allow_origins=["*"]` with specific origins
2. **Add symlink checks** - Validate paths before resolution in filesystem.py
3. **Document blast radius** - Explicit security posture documentation

### Priority 2: Process Isolation
4. **Add resource limits** - Use setrlimit for CPU/memory bounds
5. **Sanitize subprocess environment** - Don't inherit full parent env
6. **Review command allowlist** - Audit git/npm for dangerous subcommands

### Priority 3: Optional Enhancements
7. **Container isolation** - Optional Docker wrapper for high-risk commands
8. **Credential isolation** - Per-project API key scoping
9. **Network restrictions** - Egress filtering (complex, may not be needed)

### Not Recommended
- Full Python-level sandboxing (proven insecure)
- Complete network isolation (breaks agent functionality)
- Hardware VM isolation (overkill for this use case)
</action_items>

<metadata>
## Metadata

**Research scope:**
- Core technology: Python subprocess security, agent isolation
- Ecosystem: Docker, gVisor, seccomp, AppArmor, microsandbox
- Patterns: Defense-in-depth, blast radius documentation
- Pitfalls: Python sandbox escape, symlink attacks, CORS misconfiguration

**Confidence breakdown:**
- Standard stack: HIGH - verified with official Docker docs, OWASP
- Architecture: HIGH - consistent recommendations across sources
- Pitfalls: HIGH - documented CVEs and security research
- Code examples: HIGH - from official documentation

**Research date:** 2026-01-11
**Valid until:** 2026-02-11 (30 days - security ecosystem relatively stable)
</metadata>

---

*Phase: 05-sandbox-hardening*
*Research completed: 2026-01-11*
*Ready for planning: yes*
