# Roadmap: AutoCoder

## Overview

Autonomous coding agent system aligned with the Ralph Wiggum methodology for reliable long-running agent operation.

## Domain Expertise

- Reference: https://github.com/ghuntley/how-to-ralph-wiggum (definitive)
- Reference: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents (supplementary)

## Milestones

- ✅ **v1.0 MVP** - Phases 1-5 (shipped 2026-01-11)
- 🚧 **v1.1 Foundation Hardening** - Phases 6-8 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

<details>
<summary>✅ v1.0 Ralph Wiggum Alignment (Phases 1-5) - SHIPPED 2026-01-11</summary>

- [x] **Phase 1: Spec-Driven Architecture** (3/3 plans) - completed 2026-01-10
- [x] **Phase 2: Deterministic Loop** (2/2 plans) - completed 2026-01-10
- [x] **Phase 3: Backpressure Validation** (1/1 plan) - completed 2026-01-10
- [x] **Phase 4: Context Optimization** (1/1 plan) - completed 2026-01-11
- [x] **Phase 5: Sandbox Hardening** (2/2 plans) - completed 2026-01-11

See [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md) for full details.

</details>

### 🚧 v1.1 Foundation Hardening (In Progress)

**Milestone Goal:** Improve observability, document security posture, and add test confidence for core modules.

- [ ] **Phase 6: Structured Logging** - Consistent, configurable logging across all Python modules
- [ ] **Phase 7: Security Documentation** - BLAST_RADIUS.md documents how to wire in security helpers
- [ ] **Phase 8: Agent Testing** - Core agent session loop has test coverage

## Phase Details

### Phase 6: Structured Logging
**Goal**: Consistent, configurable logging across all Python modules
**Depends on**: Phase 5 (v1.0 complete)
**Requirements**: LOG-01, LOG-02
**Success Criteria** (what must be TRUE):
  1. All log messages include timestamp, level, module name, and message
  2. Log level can be changed via environment variable or config
  3. Different modules can have different log levels when needed
**Plans**: TBD

Plans:
- [ ] 06-01: TBD

### Phase 7: Security Documentation
**Goal**: BLAST_RADIUS.md fully documents how to wire in security helpers
**Depends on**: Phase 6
**Requirements**: SEC-01, SEC-02, SEC-03
**Success Criteria** (what must be TRUE):
  1. Developer can find exact code locations for resource limit integration
  2. Developer knows which functions need environment sanitization
  3. Each helper has step-by-step wiring instructions
**Plans**: TBD

Plans:
- [ ] 07-01: TBD

### Phase 8: Agent Testing
**Goal**: Core agent session loop has test coverage
**Depends on**: Phase 7
**Requirements**: TEST-01, TEST-02
**Success Criteria** (what must be TRUE):
  1. Unit tests verify session loop handles normal flow
  2. Tests verify error handling paths (crashes, timeouts, etc.)
  3. Tests can be run with pytest
**Plans**: TBD

Plans:
- [ ] 08-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 6 → 7 → 8

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Spec-Driven Architecture | v1.0 | 3/3 | Complete | 2026-01-10 |
| 2. Deterministic Loop | v1.0 | 2/2 | Complete | 2026-01-10 |
| 3. Backpressure Validation | v1.0 | 1/1 | Complete | 2026-01-10 |
| 4. Context Optimization | v1.0 | 1/1 | Complete | 2026-01-11 |
| 5. Sandbox Hardening | v1.0 | 2/2 | Complete | 2026-01-11 |
| 6. Structured Logging | v1.1 | 0/? | Not started | - |
| 7. Security Documentation | v1.1 | 0/? | Not started | - |
| 8. Agent Testing | v1.1 | 0/? | Not started | - |
