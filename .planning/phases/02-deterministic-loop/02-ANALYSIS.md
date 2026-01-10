# Phase 2: Deterministic Loop Analysis

Analysis of current agent session architecture and comparison against Ralph Wiggum patterns.

## Executive Summary

The current AutoCoder architecture is **partially deterministic**. The core loop provides consistent task selection via `feature_get_next`, but several elements introduce session-to-session variance that deviate from the pure Ralph Wiggum pattern.

---

## 1. Session Initialization Analysis

**How `create_client()` creates fresh context:**

```python
# client.py:76-200
client = create_client(project_dir, model, yolo_mode=yolo_mode)
```

**What IS deterministic (same each session):**
- Fresh `ClaudeSDKClient` instance created each iteration
- System prompt is hardcoded: "You are an expert full-stack developer..."
- Allowed tools list is static (BUILTIN_TOOLS, FEATURE_MCP_TOOLS, optionally PLAYWRIGHT_TOOLS)
- Security settings regenerated fresh (written to `.claude_settings.json`)
- MCP servers configuration is identical each session
- `cwd` is always `project_dir.resolve()`
- `max_turns=1000` is static

**What is NOT deterministic (varies between sessions):**
- Environment variables inherited from `os.environ` (could change between sessions)
- System CLI path via `shutil.which("claude")` (unlikely to change, but external dependency)
- MCP server startup (fresh process each session, but should behave identically)

**Verdict:** Session initialization is highly deterministic. The client configuration is rebuilt from scratch each session with identical parameters.

---

## 2. Prompt Loading Analysis

**How `get_coding_prompt()` produces the prompt:**

```python
# prompts.py:24-64
def load_prompt(name: str, project_dir: Path | None = None) -> str:
    # 1. Try project-specific: {project_dir}/prompts/{name}.md
    # 2. Fallback to base template: .claude/templates/{name}.template.md
```

**What IS deterministic:**
- Prompt file path resolution follows fixed fallback chain
- If files don't change between sessions, prompt content is identical
- No dynamic variable substitution in prompt loading (raw file read)

**What is NOT deterministic:**
- If user edits prompt files between sessions, prompt changes
- If project-specific prompts are added/removed, fallback behavior changes

**Verdict:** Prompt loading is deterministic given unchanged files. The prompt template itself is static - no runtime variable injection.

---

## 3. State Checks Analysis

**What `has_features()` and `print_progress_summary()` read:**

```python
# progress.py:20-56
def has_features(project_dir: Path) -> bool:
    # Checks: features.db exists AND has at least 1 feature
    # OR feature_list.json exists (legacy)
```

```python
# progress.py:58-90
def count_passing_tests(project_dir: Path) -> tuple[int, int, int]:
    # Direct SQLite query: SELECT COUNT(*) FROM features WHERE passes = 1
```

**External state READ:**
- `features.db` - SQLite database (passes, in_progress counts)
- `feature_list.json` - Legacy JSON file (if exists)

**External state WRITTEN:**
- `.progress_cache` - Webhook notification tracking (JSON)
- Webhook URL via `urllib.request.urlopen` (side effect)

**Determinism impact:**
- Database state changes between sessions (features marked passing)
- Progress counts will differ each session (expected, tracking progress)
- Cache file changes each session

**Verdict:** State checks are deterministic in behavior but return different values based on progress. This is expected - the loop should see different state as work completes.

---

## 4. Session Scoping Analysis

**How `async with client:` bounds the session:**

```python
# agent.py:192-194
async with client:
    status, response = await run_agent_session(client, prompt, project_dir)
```

**What IS deterministic:**
- Client context manager ensures clean setup/teardown
- Each session starts fresh with no conversation memory
- Session is bounded - no state leaks between `async with` blocks

**What is NOT deterministic:**
- Agent's response depends on external state (files, database)
- Agent may make different decisions based on what it reads

**Verdict:** Session scoping is fully deterministic. Each `async with client:` creates an isolated session with fresh context window.

---

## 5. Auto-Continue Analysis

**What happens between sessions in the while loop:**

```python
# agent.py:163-210
while True:
    iteration += 1

    # Create client (fresh context)
    client = create_client(project_dir, model, yolo_mode=yolo_mode)

    # Choose prompt based on session type
    if is_first_run:
        prompt = get_initializer_prompt(project_dir)
        is_first_run = False
    else:
        prompt = get_coding_prompt(project_dir) if not yolo_mode else get_coding_prompt_yolo(project_dir)

    # Run session
    async with client:
        status, response = await run_agent_session(client, prompt, project_dir)

    # Handle status
    if status == "continue":
        print_progress_summary(project_dir)
        await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)  # 3 seconds
```

**What IS deterministic:**
- New client created each iteration (fresh context)
- Same prompt loaded each iteration (after first run)
- Same 3-second delay between sessions
- Same status handling logic

**What is NOT deterministic:**
- `is_first_run` flag changes after first iteration (expected)
- `iteration` counter increments (expected)
- Database state changes based on agent actions

**Verdict:** Auto-continue is deterministic in loop mechanics. The only variance comes from progress made by the agent.

---

## Summary: Determinism Assessment

| Component | Deterministic? | Notes |
|-----------|----------------|-------|
| Client creation | ✅ Yes | Fresh instance, identical config |
| Prompt loading | ✅ Yes | Static file read, no variables |
| Session scoping | ✅ Yes | Clean context each session |
| Auto-continue loop | ✅ Yes | Identical mechanics |
| Database state | 🔶 Expected variance | Changes as work progresses |
| `claude-progress.txt` | ❓ Under analysis | See Section below |

---

## claude-progress.txt Assessment

### What the Prompt Instructs

**Standard mode (coding_prompt.template.md):**

```markdown
### STEP 1: GET YOUR BEARINGS (MANDATORY)
# 5. Read progress notes from previous sessions
cat claude-progress.txt
```

```markdown
### STEP 9: UPDATE PROGRESS NOTES
Update `claude-progress.txt` with:
- What you accomplished this session
- Which test(s) you completed
- Any issues discovered or fixed
- What should be worked on next
- Current completion status (e.g., "45/200 tests passing")
```

**YOLO mode (coding_prompt_yolo.template.md):**
Same pattern - Step 1 reads it, Step 8 updates it.

### What Agent Writes

The file is unstructured prose. Agent writes:
- Session accomplishments
- Completed features
- Issues discovered/fixed
- Recommendations for next session
- Progress counts

### What Agent Reads

Agent reads the entire file content each session to:
- Understand what previous sessions accomplished
- See if there are outstanding issues to address
- Get context on what was tried before

### Determinism Impact

**This is a source of session-to-session variance.**

Each session:
1. Reads `claude-progress.txt` (different content each time)
2. Gets different context about prior work
3. May make different decisions based on that context
4. Writes new content, changing what next session reads

This violates the Ralph Wiggum pattern where each iteration starts with identical context.

### Ralph Wiggum Comparison

| Aspect | Ralph Wiggum | AutoCoder |
|--------|--------------|-----------|
| State file | `IMPLEMENTATION_PLAN.md` | `claude-progress.txt` |
| Structure | Structured task list | Unstructured prose |
| Purpose | Drives next task selection | Human breadcrumb trail |
| Who reads | Agent (to select task) | Agent (for context) |
| Determinism | N/A (different pattern) | Reduces determinism |

**Key difference:** Ralph Wiggum's `IMPLEMENTATION_PLAN.md` is the source of truth for task selection. AutoCoder's `feature_get_next` already provides deterministic task selection via the database. The `claude-progress.txt` is redundant for task selection purposes.

### Value Assessment

**What would be lost if removed:**
- Human debugging trail (what each session did)
- Agent context about what was tried before (could prevent repeating failed approaches)
- Continuity notes (what to work on next)

**What would be gained:**
- Full determinism - every session starts with identical context
- Simpler architecture - fewer files to manage
- Faster startup - no file read in Step 1
- Alignment with Ralph Wiggum fresh-start pattern

### Recommendation

The `claude-progress.txt` file provides **human observability** but introduces **agent variance**.

The question is: Does the context from prior sessions help or hurt agent performance?

**Arguments for keeping (structured or write-only):**
- Debugging value for humans reviewing agent work
- May help agent avoid repeating failed approaches
- Provides session continuity for complex multi-step work

**Arguments for removing:**
- `feature_get_next` already provides deterministic task selection
- Each session should work on exactly one feature (per Ralph Wiggum pattern)
- Prior session notes may confuse agent more than help
- Reduces token usage (no file read in prompt execution)

---

## Decision Required

See Task 3 checkpoint for options:
1. **remove-progress**: Full Ralph Wiggum alignment, maximum determinism
2. **structure-progress**: Keep notes, make sections explicit
3. **read-only-progress**: Write breadcrumbs for humans, agent never reads
4. **keep-current**: Minor cleanup, trust existing system

The implementation in 02-02 will follow whichever approach is selected.
