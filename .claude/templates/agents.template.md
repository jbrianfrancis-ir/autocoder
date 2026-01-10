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

## Notes

[Project-specific notes added by initializer or coding agent]

---

*Updated: [date]*
