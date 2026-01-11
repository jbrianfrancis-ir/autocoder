---
phase: 05-sandbox-hardening
plan: 01
subsystem: security
tags: [cors, symlink, blast-radius, filesystem, fastapi]

# Dependency graph
requires:
  - phase: 04
    provides: Context optimization complete, foundation ready for hardening
provides:
  - CORS restricted to localhost origins
  - Symlink escape detection in filesystem router
  - Blast radius documentation
affects: [05-02, future security work]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Symlink escape detection before path resolution
    - Defense-in-depth security documentation

key-files:
  created:
    - .planning/codebase/BLAST_RADIUS.md
  modified:
    - server/main.py
    - server/routers/filesystem.py

key-decisions:
  - "Localhost-only CORS with ports 5173 and 8888"
  - "Symlink check happens BEFORE path resolution to prevent TOCTOU"
  - "Blast radius docs in .planning/codebase/ for discoverability"

patterns-established:
  - "is_symlink_escape() helper for symlink attack prevention"
  - "Security documentation as BLAST_RADIUS.md with risk assessment"

issues-created: []

# Metrics
duration: 3 min
completed: 2026-01-11
---

# Phase 5 Plan 1: Sandbox Hardening - Quick Wins Summary

**CORS restricted to localhost, symlink escape detection added, blast radius documented**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-11T14:00:27Z
- **Completed:** 2026-01-11T14:03:46Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Replaced wildcard CORS (`["*"]`) with specific localhost origins (5173, 8888)
- Added `is_symlink_escape()` helper to detect symlinks pointing outside base directory
- Updated `is_path_blocked()` to check symlinks BEFORE path resolution
- Created comprehensive BLAST_RADIUS.md documenting 29 allowed commands and security posture

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix CORS Configuration** - `50e10ae` (fix)
2. **Task 2: Add Symlink Attack Mitigation** - `54a5c06` (fix)
3. **Task 3: Document Blast Radius** - `b15d6a0` (docs)

## Files Created/Modified

- `server/main.py` - CORS middleware now restricts to localhost origins
- `server/routers/filesystem.py` - Added symlink escape detection (67 lines added)
- `.planning/codebase/BLAST_RADIUS.md` - New security documentation (136 lines)

## Decisions Made

1. **CORS origins:** Chose `localhost:5173` (Vite) and `localhost:8888` (FastAPI) as the specific allowed origins, plus 127.0.0.1 variants
2. **Symlink check order:** Check BEFORE `resolve()` to prevent TOCTOU attacks where symlink target changes between check and use
3. **Blast radius location:** Placed in `.planning/codebase/` alongside other architecture documentation for discoverability

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- Quick wins complete, ready for 05-02 (Process Isolation)
- CORS and symlink mitigations in place
- Security posture documented for reference in future work

---
*Phase: 05-sandbox-hardening*
*Completed: 2026-01-11*
