# AGENTS.md - Operational Reference

Quick reference for agents working on this project. Keep under 60 lines.

## Quick Start

```bash
# [One command to run the app - filled by initializer]
./init.sh
```

## Commands

| Action  | Command |
|---------|---------|
| Install | `[package manager install]` |
| Dev     | `[dev server command]` |
| Build   | `[build command]` |
| Test    | `[test command]` |
| Lint    | `[lint command]` |

## Key Locations

| Path | Purpose |
|------|---------|
| `specs/` | Feature specifications (source of truth) |
| `features.db` | Runtime feature tracking database |
| `[src/]` | Source code |
| `[tests/]` | Test files |

## Specs Workflow

1. Read spec from `specs/` directory
2. Implement the feature
3. Verify against test steps
4. Mark passing with `feature_mark_passing`

## Session Architecture

**Deterministic fresh-start loop:** Each session starts with identical context, works on one feature, exits cleanly. Database tracks progress (`features.db`), specs define requirements (`specs/`).

**State files:** `specs/` (source of truth), `features.db` (progress), `claude-progress.txt` (structured: Known Issues, Blocked, Next Session)

**Flow:** Fresh client → prompt → `feature_get_next` → implement → **validate** → verify → mark passing → commit → exit

**Validation gates:** Lint, type-check, build must pass before commits. Fix errors first.

## Context Efficiency

- MCP tools return markdown (not JSON) for efficient tokenization
- Spec files: ~5,000 tokens upfront at session start
- Progress check (`feature_get_stats`): ~200 tokens
- Next feature (`feature_get_next`): ~500 tokens
- Reserve ~70% context for implementation work

## Notes

[Project-specific notes]

*Updated: [date]*
