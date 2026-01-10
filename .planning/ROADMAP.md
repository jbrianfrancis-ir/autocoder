# Roadmap: AutoCoder

## Overview

Validate and align the AutoCoder agent harness implementation with the definitive [Ralph Wiggum methodology](https://github.com/ghuntley/how-to-ralph-wiggum), ensuring the system follows established best practices for long-running autonomous coding agents.

## Domain Expertise

- Reference: https://github.com/ghuntley/how-to-ralph-wiggum (definitive)
- Reference: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents (supplementary)

## Milestones

- 🚧 **v1.0 Ralph Wiggum Alignment** - Phases 1-5 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Spec-Driven Architecture** - Align feature tracking with specs-as-source-truth pattern
- [ ] **Phase 2: Deterministic Loop** - Ensure agent starts from known state each iteration
- [ ] **Phase 3: Backpressure Validation** - Strengthen test/lint/type-check gates before commits
- [ ] **Phase 4: Context Optimization** - Implement markdown-over-JSON and token efficiency patterns
- [ ] **Phase 5: Sandbox Hardening** - Ensure isolated execution with understood blast radius

## Phase Details

### 🚧 v1.0 Ralph Wiggum Alignment (In Progress)

**Milestone Goal:** Validate and align the agent harness with Ralph Wiggum methodology patterns for reliable autonomous operation.

#### Phase 1: Spec-Driven Architecture

**Goal**: Align feature tracking with specs-as-source-truth pattern from Ralph Wiggum
**Depends on**: Nothing (first phase)
**Research**: Unlikely (internal patterns, methodology reference available)
**Plans**: TBD

Current state:
- Features stored in SQLite database (`features.db`) with JSON schema
- Features created by Initializer agent from app_spec.txt

Ralph Wiggum pattern:
- Specs in `specs/FILENAME.md` files (one per topic of concern)
- `IMPLEMENTATION_PLAN.md` as gap analysis between specs and code
- Markdown over JSON for token efficiency

Gap analysis needed:
- Compare current feature JSON format vs markdown specs pattern
- Evaluate if file-based specs provide benefits over database approach
- Assess impact on MCP server design

Plans:
- [x] 01-01: Spec format & parser (complete)
- [x] 01-02: Initializer spec generation (complete)
- [ ] 01-03: Hybrid approach integration

#### Phase 2: Deterministic Loop

**Goal**: Ensure agent starts from known state each iteration (fresh-start architecture)
**Depends on**: Phase 1
**Research**: Unlikely (internal patterns)
**Plans**: TBD

Current state:
- Agent reads `claude-progress.txt` and git history each session
- Process manager restarts agent subprocess
- Prompts loaded from templates with project fallback

Ralph Wiggum pattern:
- `cat PROMPT.md | claude` loop with identical context each iteration
- One task per loop = 100% smart zone context utilization
- Monolithic single-task operation before exit

Gap analysis needed:
- Verify agent gets clean context each session
- Confirm single-feature focus per session
- Check prompt seeding consistency

Plans:
- [ ] 02-01: TBD

#### Phase 3: Backpressure Validation

**Goal**: Strengthen test/lint/type-check gates as backpressure before commits
**Depends on**: Phase 2
**Research**: Unlikely (internal patterns)
**Plans**: TBD

Current state:
- Security hooks validate bash commands
- Playwright MCP for browser testing (optional in YOLO mode)
- Feature marked passing after agent verification

Ralph Wiggum pattern:
- "Anything can be wired in as back pressure to reject invalid code generation"
- Tests, type-checking, linting force correctness before commits
- Failure patterns trigger prompt guardrails

Gap analysis needed:
- Audit current validation gates in agent loop
- Identify missing backpressure points
- Evaluate prompt guardrails for common failures

Plans:
- [ ] 03-01: TBD

#### Phase 4: Context Optimization

**Goal**: Implement markdown-over-JSON and token efficiency patterns
**Depends on**: Phase 3
**Research**: Unlikely (internal patterns)
**Plans**: TBD

Current state:
- Feature list in JSON format (SQLite database)
- Prompts are markdown files
- App spec in XML format

Ralph Wiggum pattern:
- Markdown over JSON deliberately for token efficiency
- Plans are human-readable prose, not structured serialization
- Allocate ~5,000 tokens to specs upfront

Gap analysis needed:
- Measure token usage of current formats
- Evaluate conversion to markdown-based formats
- Consider impact on MCP tool design

Plans:
- [ ] 04-01: TBD

#### Phase 5: Sandbox Hardening

**Goal**: Ensure isolated execution with understood blast radius
**Depends on**: Phase 4
**Research**: Likely (security best practices)
**Research topics**: Sandbox escape vectors, process isolation patterns, credential handling
**Plans**: TBD

Current state:
- Bash command allowlist in `security.py`
- Filesystem restricted to project directory
- Output sanitization for secrets
- CORS currently over-permissive

Ralph Wiggum pattern:
- Run in isolated sandboxes
- "It's not if it gets popped, it's when. And what is the blast radius?"
- Requires `--dangerously-skip-permissions` (understood risk)

Gap analysis needed:
- Audit current security model against Ralph Wiggum expectations
- Document blast radius for this system
- Address CORS and other security concerns from CONCERNS.md

Plans:
- [ ] 05-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Spec-Driven Architecture | v1.0 | 2/3 | In progress | - |
| 2. Deterministic Loop | v1.0 | 0/? | Not started | - |
| 3. Backpressure Validation | v1.0 | 0/? | Not started | - |
| 4. Context Optimization | v1.0 | 0/? | Not started | - |
| 5. Sandbox Hardening | v1.0 | 0/? | Not started | - |
