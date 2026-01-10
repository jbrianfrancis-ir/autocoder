---
phase: 02-deterministic-loop
plan: 01
subsystem: architecture
tags: [determinism, session-architecture, claude-progress, ralph-wiggum]

# Dependency graph
requires:
  - phase: 01-03
    provides: Hybrid spec-database architecture, feature_get_next with spec content
provides:
  - Session architecture analysis document
  - Determinism assessment of all components
  - Decision on structured progress file approach
affects: [02-02-implementation, future-sessions]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Structured claude-progress.txt with defined sections"
    - "Session Log append-only, Known Issues read by agent"

key-files:
  created:
    - .planning/phases/02-deterministic-loop/02-ANALYSIS.md
  modified: []

key-decisions:
  - "structure-progress: Structure claude-progress.txt with defined sections"
  - "Session Log is write-only (append, never read by agent)"
  - "Known Issues and Blocked Features are read by agent"

patterns-established:
  - "Selective reading: Agent reads structured sections, not unstructured prose"
  - "Append-only logs: Session summaries for human debugging"

issues-created: []

# Metrics
duration: 6min
completed: 2026-01-10
---

# Phase 2 Plan 1: Deterministic Loop Analysis & Design Summary

**Session architecture analyzed: 5 components verified deterministic, claude-progress.txt identified as variance source, structured-sections approach selected**

## Performance

- **Duration:** 6 min
- **Started:** 2026-01-10T21:55:03Z
- **Completed:** 2026-01-10T22:00:43Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- Analyzed 5 session architecture components (init, prompt, state, scope, loop)
- Verified core loop is highly deterministic (fresh client, static prompt, clean sessions)
- Identified `claude-progress.txt` as primary source of session-to-session variance
- Compared current system against Ralph Wiggum patterns
- Selected "structure-progress" approach for balancing determinism with observability

## Task Commits

Each task was committed atomically:

1. **Task 1: Analyze current session architecture** - `ae9c51d` (docs)
2. **Task 2: Assess claude-progress.txt role** - included in ae9c51d (docs)
3. **Task 3: Select deterministic state approach** - `e23114a` (docs)

**Plan metadata:** (this commit)

## Analysis Findings

### What IS Deterministic

| Component | Status | Notes |
|-----------|--------|-------|
| Client creation | ✅ | Fresh instance, identical config each session |
| Prompt loading | ✅ | Static file read, no runtime variables |
| Session scoping | ✅ | Clean context via `async with client:` |
| Auto-continue loop | ✅ | Identical mechanics, 3s delay |
| Task selection | ✅ | `feature_get_next` from database |

### What Introduces Variance

| Source | Impact | Resolution |
|--------|--------|------------|
| claude-progress.txt | Agent reads different context each session | Structure with defined sections |
| Database state | Different pass counts each session | Expected (tracks progress) |
| Environment variables | Inherited from os.environ | Low risk, rarely changes |

## Decision Made

**Selected: structure-progress** — Structure claude-progress.txt with defined sections

### Sections to Implement in 02-02

1. `## Session Log` - Append-only session summaries (human reference, not read by agent)
2. `## Known Issues` - Active issues agent should be aware of (read by agent)
3. `## Blocked Features` - Features skipped due to external blockers (read by agent)
4. `## Next Session` - Specific guidance for next session (read and clear)

### Rationale

- Maintains human debugging value (breadcrumb trail preserved)
- Enables selective reading (agent reads only structured sections)
- Reduces variance (structured content more predictable than prose)
- Backwards compatible (existing projects can migrate incrementally)

## Files Created/Modified

- `.planning/phases/02-deterministic-loop/02-ANALYSIS.md` - Complete determinism analysis with decision

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## Next Step

Ready for 02-02-PLAN.md (Deterministic Loop Implementation) which will:
- Define structured claude-progress.txt format
- Update prompt templates to use selective reading
- Implement session log append behavior

---
*Phase: 02-deterministic-loop*
*Completed: 2026-01-10*
