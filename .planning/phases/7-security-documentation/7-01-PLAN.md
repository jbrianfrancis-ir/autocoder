---
phase: 7-security-documentation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/codebase/BLAST_RADIUS.md
autonomous: true

must_haves:
  truths:
    - "Developer can find exact file:line locations for resource limit integration"
    - "Developer can find exact file:line locations for environment sanitization"
    - "Each helper has step-by-step wiring instructions with copy-paste code"
    - "Platform-specific considerations are documented"
  artifacts:
    - path: ".planning/codebase/BLAST_RADIUS.md"
      provides: "Security helper wiring documentation"
      contains: "## How to Wire In Security Helpers"
  key_links:
    - from: "BLAST_RADIUS.md wiring section"
      to: "security.py helper functions"
      via: "file:line references and code snippets"
      pattern: "process_manager\\.py.*258|security\\.py.*apply_resource_limits"
---

<objective>
Document how to wire in security helpers to BLAST_RADIUS.md

Purpose: Enable developers to integrate resource limits and environment sanitization
by providing exact code locations, step-by-step instructions, and copy-paste-ready snippets.

Output: Updated BLAST_RADIUS.md with complete wiring guide
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/7-security-documentation/7-RESEARCH.md
@.planning/codebase/BLAST_RADIUS.md
@security.py
@server/services/process_manager.py
@client.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add security helper wiring guide to BLAST_RADIUS.md</name>
  <files>.planning/codebase/BLAST_RADIUS.md</files>
  <action>
Add a new section "## How to Wire In Security Helpers" to BLAST_RADIUS.md after
the "Environment Sanitization" section (Section 6) and before "Blast Radius" section.

The new section must include:

**7.1 Integration Points Overview**
- Table listing all subprocess calls that should use these helpers
- Priority ranking (HIGH/MEDIUM/LOW) based on research
- Primary target: `server/services/process_manager.py:258`

**7.2 Wiring Resource Limits**
Step-by-step instructions:
1. Import statement: `from security import apply_resource_limits`
2. Exact file:line location: `server/services/process_manager.py:258`
3. Before/after code comparison
4. Platform note: No-op on Windows, works on Linux/macOS
5. How to verify: Check process with `cat /proc/{pid}/limits` on Linux

Code snippet to add:
```python
# Before
self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
)

# After
from security import apply_resource_limits

self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
    preexec_fn=apply_resource_limits,  # Add this line
)
```

**7.3 Wiring Environment Sanitization**
Step-by-step instructions:
1. Import statement: `from security import get_safe_environment`
2. Exact file:line location: `server/services/process_manager.py:258`
3. CRITICAL: Must explicitly add ANTHROPIC_API_KEY since agent needs it
4. Before/after code comparison
5. How to verify: Print `env` dict and confirm only allowed vars present

Code snippet:
```python
# Before
self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
)

# After
import os
from security import get_safe_environment

safe_env = get_safe_environment(project_dir=str(self.project_dir))
safe_env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")

self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
    env=safe_env,  # Add this line
)
```

**7.4 Combined Wiring (Both Helpers)**
Show the complete integration with both helpers:
```python
import os
from security import apply_resource_limits, get_safe_environment

safe_env = get_safe_environment(project_dir=str(self.project_dir))
safe_env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")

self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd=str(self.project_dir),
    preexec_fn=apply_resource_limits,
    env=safe_env,
)
```

**7.5 Secondary Integration Points**
Document lower-priority integration points:
- `start.py:220` (Claude CLI launch) - MEDIUM priority
- `start.py:372` (CLI agent run) - MEDIUM priority
- `client.py:161-173` (MCP server env) - MEDIUM priority
- `start_ui.py` (dev servers) - LOW priority

For each, note why it's lower priority and whether integration is recommended.

**7.6 Testing Verification**
How to verify helpers are working:
1. Resource limits: `cat /proc/{pid}/limits` shows configured limits
2. Environment: Log or print env dict to confirm sanitization
3. Both: Agent still functions correctly after integration

Also update the "Known Gaps" table to change status from "Helper ready" to
"Documented" with reference to the new wiring section.

Update Version History with entry for today's date.
  </action>
  <verify>
Verify the updated BLAST_RADIUS.md contains:
1. `grep -c "How to Wire In" .planning/codebase/BLAST_RADIUS.md` returns 1
2. `grep -c "process_manager.py:258" .planning/codebase/BLAST_RADIUS.md` returns at least 2
3. `grep -c "preexec_fn=apply_resource_limits" .planning/codebase/BLAST_RADIUS.md` returns at least 1
4. `grep -c "get_safe_environment" .planning/codebase/BLAST_RADIUS.md` returns at least 3
5. `grep -c "ANTHROPIC_API_KEY" .planning/codebase/BLAST_RADIUS.md` returns at least 2
  </verify>
  <done>
BLAST_RADIUS.md contains new "How to Wire In Security Helpers" section with:
- Integration points table with priorities
- Step-by-step instructions for resource limits
- Step-by-step instructions for environment sanitization
- Combined wiring example
- Secondary integration points documented
- Testing verification steps
- Known gaps table updated to "Documented" status
  </done>
</task>

<task type="auto">
  <name>Task 2: Validate documentation completeness</name>
  <files>.planning/codebase/BLAST_RADIUS.md</files>
  <action>
Read the updated BLAST_RADIUS.md and verify it satisfies all three requirements:

SEC-01: Exact integration points documented
- Verify file:line references exist for process_manager.py
- Verify priority rankings exist

SEC-02: Environment sanitization locations documented
- Verify ANTHROPIC_API_KEY handling is explained
- Verify get_safe_environment usage is shown

SEC-03: Step-by-step wiring instructions exist
- Verify before/after code comparisons exist
- Verify import statements are shown
- Verify combined example exists
- Verify testing verification steps exist

If any requirement is not fully satisfied, update the document to address gaps.
  </action>
  <verify>
Read BLAST_RADIUS.md and confirm:
1. A developer could follow the instructions without asking clarifying questions
2. All code snippets are syntactically correct
3. File paths and line numbers match actual codebase
4. Platform-specific notes are present for Windows limitation
  </verify>
  <done>
All three requirements (SEC-01, SEC-02, SEC-03) are fully satisfied:
- Developer can find exact code locations for resource limit integration
- Developer knows which functions need environment sanitization
- Each helper has step-by-step wiring instructions
  </done>
</task>

</tasks>

<verification>
Phase verification checklist:

1. **SEC-01 (Resource limit integration points):**
   - [ ] `server/services/process_manager.py:258` documented as PRIMARY
   - [ ] Secondary points documented with priority rankings
   - [ ] Platform limitations (Windows no-op) noted

2. **SEC-02 (Environment sanitization locations):**
   - [ ] Same integration points documented
   - [ ] ANTHROPIC_API_KEY preservation explained
   - [ ] Variables included/excluded clearly stated

3. **SEC-03 (Wiring instructions):**
   - [ ] Import statements provided
   - [ ] Before/after code comparisons
   - [ ] Combined example showing both helpers
   - [ ] Testing verification steps

4. **Document quality:**
   - [ ] Version history updated
   - [ ] Known gaps table updated
   - [ ] Copy-paste-ready code snippets
</verification>

<success_criteria>
Phase 7 is complete when:
1. BLAST_RADIUS.md has a "How to Wire In Security Helpers" section
2. A developer can find exact file:line locations for both helpers
3. Step-by-step instructions exist for each helper individually and combined
4. The document explains the ANTHROPIC_API_KEY preservation requirement
5. Platform-specific considerations are documented
6. Testing verification steps are included
</success_criteria>

<output>
After completion, create `.planning/phases/7-security-documentation/7-01-SUMMARY.md`
</output>
