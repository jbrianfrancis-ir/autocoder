---
phase: 03-backpressure-validation
plan: 01
subsystem: prompts
tags: [backpressure, validation, lint, type-check, guardrails]

# Dependency graph
requires:
  - phase: 02-02
    provides: Deterministic loop architecture, structured claude-progress.txt
provides:
  - Validation gates step in standard coding prompt
  - Common failure pattern guardrails in both prompts
  - Backpressure documentation in AGENTS.md template
affects: [agent-sessions, future-projects]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "STEP 8: VALIDATION GATES (BLOCKING) before commits"
    - "Failure pattern guardrails tables for TypeScript, Python, Build errors"
    - "Backpressure principle: fix errors before proceeding"

key-files:
  created: []
  modified:
    - .claude/templates/coding_prompt.template.md
    - .claude/templates/coding_prompt_yolo.template.md
    - .claude/templates/agents.template.md

key-decisions:
  - "Insert validation step between feature marking and commit (STEP 8)"
  - "Use tables for failure pattern guardrails (easy to scan)"
  - "Keep AGENTS.md under 60 lines with compact validation note"

patterns-established:
  - "Validation gates are BLOCKING - must pass before commits"
  - "Error pattern tables: Error | Cause | Fix format"

issues-created: []

# Metrics
duration: 5min
completed: 2026-01-10
---

# Phase 3 Plan 1: Backpressure Validation Gates Summary

**Added validation gates step and failure pattern guardrails to agent prompts, enforcing code quality before commits**

## Accomplishments

- Added STEP 8: VALIDATION GATES (BLOCKING) to standard coding prompt
- Renumbered subsequent steps (8→9, 9→10, 10→11)
- Added COMMON FAILURE PATTERNS section to both prompt templates
- Updated AGENTS.md template with validation flow and backpressure note

## Task Commits

1. **Task 1:** `fa41244` - Add validation gates step to standard coding prompt
2. **Task 2:** `4500465` - Add common failure pattern guardrails to prompts
3. **Task 3:** `99b01ea` - Document backpressure validation in AGENTS.md

## Files Created/Modified

- `.claude/templates/coding_prompt.template.md` - Added STEP 8: VALIDATION GATES, COMMON FAILURE PATTERNS section
- `.claude/templates/coding_prompt_yolo.template.md` - Added COMMON FAILURE PATTERNS section
- `.claude/templates/agents.template.md` - Updated flow with validate step, added validation gates note

## Decisions Made

- **Validation step placement:** Between feature marking (STEP 7) and commit (now STEP 9) - ensures code is validated before any commit attempt
- **Guardrails format:** Tables with Error | Cause | Fix columns for quick scanning
- **Backpressure principle:** Explicitly documented - "fix errors before proceeding" enforces quality

## Issues Encountered

None

## Next Step

Phase 3: Backpressure Validation complete. Ready for Phase 4: Context Optimization.

---
*Phase: 03-backpressure-validation*
*Completed: 2026-01-10*
