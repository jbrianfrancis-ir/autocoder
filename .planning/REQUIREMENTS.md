# Requirements: AutoCoder v1.1

**Defined:** 2026-01-16
**Core Value:** Enables developers to define application specifications and have an AI agent implement features autonomously across multiple sessions, with real-time progress tracking and human oversight through a modern web interface.

## v1 Requirements

Requirements for v1.1 Foundation Hardening milestone.

### Logging

- [x] **LOG-01**: All Python modules use consistent log format (timestamp, level, module, message)
- [x] **LOG-02**: Log levels are configurable (DEBUG/INFO/WARNING/ERROR) globally or per-module

### Security Documentation

- [x] **SEC-01**: BLAST_RADIUS.md documents exact integration points for resource limit helpers
- [x] **SEC-02**: BLAST_RADIUS.md documents where environment sanitization should be applied
- [x] **SEC-03**: BLAST_RADIUS.md includes "how to wire in" guidance for each helper

### Testing

- [x] **TEST-01**: agent.py has unit tests for core session loop
- [x] **TEST-02**: agent.py has tests for error handling paths

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Logging

- **LOG-03**: Structured JSON output option for machine-parseable logs
- **LOG-04**: Log rotation and file output management

### Security Documentation

- **SEC-04**: Inline code comments at integration points

### Testing

- **TEST-03**: client.py configuration and security hook tests
- **TEST-04**: security.py ALLOWED_COMMANDS validation tests
- **TEST-05**: Integration tests (end-to-end agent runs)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Multi-project parallel execution | Not core to v1.1, reliability first |
| Cloud deployment | Local development tool |
| client.py tests | Deferred to v2 |
| security.py tests | Deferred to v2 |

## Traceability

Which phases cover which requirements. Updated by create-roadmap.

| Requirement | Phase | Status |
|-------------|-------|--------|
| LOG-01 | Phase 6 | Complete |
| LOG-02 | Phase 6 | Complete |
| SEC-01 | Phase 7 | Complete |
| SEC-02 | Phase 7 | Complete |
| SEC-03 | Phase 7 | Complete |
| TEST-01 | Phase 8 | Complete |
| TEST-02 | Phase 8 | Complete |

**Coverage:**
- v1 requirements: 7 total
- Mapped to phases: 7 ✓
- Unmapped: 0

---
*Requirements defined: 2026-01-16*
*Last updated: 2026-01-16 after roadmap creation*
