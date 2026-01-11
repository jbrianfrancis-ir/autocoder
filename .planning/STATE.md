# Project State: AutoCoder

## Current Position

Phase: 5 of 5 (Sandbox Hardening)
Plan: 1 of 2 in current phase
Status: In progress
Last activity: 2026-01-11 - Completed 05-01-PLAN.md

Progress: █████████░ 90%

## Accumulated Context

### Key Decisions Made

| Phase | Decision | Rationale |
|-------|----------|-----------|
| 05-01 | Localhost-only CORS (5173, 8888) | Security hardening, no wildcard origins |
| 05-01 | Symlink check before path resolution | Prevents TOCTOU attacks |
| 05-01 | Blast radius docs in .planning/codebase/ | Discoverability with other architecture docs |
| 04-01 | Markdown over JSON for MCP tools | Token efficiency per Ralph Wiggum principle |
| 04-01 | Keep feature_create_bulk as JSON | Initialization utility, not agent context |
| 03-01 | Validation gates as STEP 8 before commit | Enforces quality before any commit attempt |
| 03-01 | Table format for failure guardrails | Easy to scan Error | Cause | Fix structure |
| 02-02 | Selective grep for section reading | Avoids full file read, maintains determinism |
| 02-02 | Session Log marked "do not read" | Prevents unstructured prose from confusing agent |
| 02-01 | structure-progress for claude-progress.txt | Balances determinism with human observability, enables selective reading |
| 01-01 | YAML frontmatter over JSON | More human-readable, aligns with Ralph Wiggum's "markdown over JSON" principle |
| 01-01 | Test Steps → steps array | Direct mapping to existing Feature model structure |
| 01-01 | No external YAML parser | Simple inline parsing keeps dependencies minimal |
| 01-02 | Numbered prefixes (01-, 02-) for spec priority | Natural sort order, simpler than frontmatter-only |
| 01-02 | AGENTS.md under 60 lines | Ralph Wiggum guidance for quick parsing |
| 01-02 | Hybrid database approach | Keep feature_create_bulk for runtime tracking |
| 01-03 | Match specs to features by name | H1 title matching, simple and predictable |
| 01-03 | Sync preserves status | Update content but keep passes/in_progress intact |
| 01-03 | Include full spec in feature_get_next | Agent has complete requirements without extra file read |

### Patterns Established

From 01-01:
- Spec format: YAML frontmatter + H1 title + description + criteria + steps
- Parser uses standard library only (no new dependencies)

From 01-02:
- Spec file naming: `specs/{NN}-{feature-name}.md`
- AGENTS.md as operational quick reference (<60 lines)

From 01-03:
- Hybrid architecture: specs for content, database for status
- Auto-load specs on startup if database empty
- feature_sync_from_specs for manual spec edits

From 02-02:
- Structured claude-progress.txt: Session Log, Known Issues, Blocked Features, Next Session
- Selective reading via grep for structured sections only
- Session Architecture section in AGENTS.md template

From 04-01:
- MCP tools return markdown for token efficiency
- format_feature_markdown helper for consistent formatting
- Token budget targets: specs ~5k, stats ~200, next ~500 tokens

From 03-01:
- STEP 8: VALIDATION GATES (BLOCKING) before commits
- COMMON FAILURE PATTERNS section with Error | Cause | Fix tables
- Backpressure principle: fix errors before proceeding

From 05-01:
- is_symlink_escape() helper for symlink attack prevention
- BLAST_RADIUS.md for security posture documentation

From codebase analysis:
- Two-agent pattern (Initializer + Coding Agent) already implemented
- Feature MCP server for agent-database communication
- WebSocket real-time updates to UI
- Security allowlist for bash commands

### Blockers/Concerns Carried Forward

From `.planning/codebase/CONCERNS.md`:
- ~~CORS configuration over-permissive~~ (FIXED in 05-01)
- Silent exception handling in WebSocket code
- No structured logging framework
- Test coverage gaps in core modules

## Roadmap Evolution

- Project initialized: 2026-01-10
- Codebase mapped: 2026-01-10 (7 documents in `.planning/codebase/`)
- Milestone v1.0 created: Ralph Wiggum Alignment, 5 phases (Phase 1-5)

## Session Continuity

Last session: 2026-01-11
Stopped at: Completed 05-01-PLAN.md
Resume file: None (ready to execute 05-02-PLAN.md)

## Phase Dependencies

```
Phase 1 (Spec-Driven Architecture)
    ↓
Phase 2 (Deterministic Loop)
    ↓
Phase 3 (Backpressure Validation)
    ↓
Phase 4 (Context Optimization)
    ↓
Phase 5 (Sandbox Hardening)
```

## Quick Reference

**Definitive Reference:** https://github.com/ghuntley/how-to-ralph-wiggum

**Key Ralph Wiggum Patterns to Validate:**
1. Specs-as-source-truth (not database-first)
2. Deterministic fresh-start architecture
3. One task per loop = 100% context utilization
4. Backpressure-driven validation
5. Markdown over JSON for token efficiency
6. Isolated sandboxes with understood blast radius

**Codebase Documentation:** `.planning/codebase/`

---

*State updated: 2026-01-11 - Completed 05-01-PLAN.md*
