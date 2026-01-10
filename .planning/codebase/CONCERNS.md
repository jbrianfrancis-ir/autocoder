# Codebase Concerns

**Analysis Date:** 2026-01-10

## Tech Debt

**CORS Configuration is Over-Permissive:**
- Issue: `allow_origins=["*"]` accepts ALL origins despite comment about "LAN access only"
- Files: `server/main.py:59`
- Why: Quick development setup
- Impact: Security vulnerability if exposed to network
- Fix approach: Restrict to specific origins or implement proper origin validation

**Lazy Imports for Circular Dependencies:**
- Issue: Circular dependency requires lazy import initialization
- Files: `server/routers/projects.py:24-54`, `server/websocket.py:21-47`
- Why: Module interdependencies not properly structured
- Impact: Makes code harder to test and understand
- Fix approach: Restructure modules to eliminate circular imports

**Direct SQLite Queries Mixed with ORM:**
- Issue: Direct `cursor.execute()` queries alongside SQLAlchemy ORM
- Files: `progress.py:49, 75, 77, 81`, `api/database.py:67, 72`
- Why: Legacy code or quick implementation
- Impact: Maintenance burden, missed migration patterns
- Fix approach: Migrate all queries to SQLAlchemy ORM

## Known Bugs

**No Critical Bugs Identified:**
- Codebase appears stable for core functionality
- Edge cases may exist in error handling paths

## Security Considerations

**Silent Exception Handling:**
- Risk: Bare `except Exception:` blocks hide real errors
- Files: `server/websocket.py:85, 181, 191`, `server/routers/filesystem.py:164-165, 274`
- Current mitigation: None (errors logged to console sometimes)
- Recommendations: Add proper logging, re-raise where appropriate

**Symlink Attacks Not Explicitly Handled:**
- Risk: `Path.resolve()` called on untrusted input could follow symlinks to blocked directories
- Files: `server/routers/filesystem.py:128, 213, 377, 464`
- Current mitigation: Blocked path list checked after resolution
- Recommendations: Explicitly check for symlinks before resolution

**Windows Reserved Names Incomplete:**
- Risk: Invalid character check doesn't include all reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
- Files: `server/routers/filesystem.py:452`
- Current mitigation: Partial character validation
- Recommendations: Add complete Windows reserved name validation

## Performance Bottlenecks

**WebSocket Polling Causes Multiple DB Queries:**
- Problem: `_count_passing_tests()` does 3 database queries per poll
- Files: `server/websocket.py:118-146`
- Measurement: Not profiled, but queries on every poll cycle
- Cause: No caching of poll results
- Improvement path: Cache results, invalidate on feature update

**Regex Patterns Checked Per Line:**
- Problem: 40+ redaction patterns checked on every agent output line
- Files: `server/services/process_manager.py` (redaction logic)
- Measurement: Not profiled
- Cause: Security-first design
- Improvement path: Compile patterns once, consider batch processing

**Directory Iteration Without Pagination:**
- Problem: Lists all directory items with no limit
- Files: `server/routers/filesystem.py:239-275`
- Measurement: Slow on directories with many files
- Cause: Simple implementation
- Improvement path: Add pagination parameters

## Fragile Areas

**Authentication Middleware Chain:**
- Files: `server/main.py` (middleware order)
- Why fragile: Middleware functions run in specific order
- Common failures: Order change could break security
- Safe modification: Add tests before changing order
- Test coverage: No integration tests for middleware chain

**Webhook Event Processing:**
- Files: `progress.py:177-185`
- Why fragile: Single attempt with 5s timeout, no retry
- Common failures: Transient network errors cause silent failures
- Safe modification: Add retry logic with exponential backoff
- Test coverage: No tests for webhook logic

## Scaling Limits

**SQLite Per-Project:**
- Current capacity: Works well for typical project sizes
- Limit: SQLite concurrent write limitations
- Symptoms at limit: Lock timeouts in high-frequency operations
- Scaling path: Sufficient for intended use case (single agent per project)

**Single Process Manager Per Project:**
- Current capacity: One agent per project enforced by lock file
- Limit: By design (prevents conflicts)
- Symptoms at limit: Lock file prevents second agent
- Scaling path: Not needed (design constraint)

## Dependencies at Risk

**Tailwind CSS 4.0.0-beta:**
- Risk: Beta version, potential breaking changes
- Files: `ui/package.json`
- Impact: UI styling could break on update
- Migration plan: Update to stable when released, test thoroughly

**No Version Pinning for Python Dependencies:**
- Risk: `>=` constraints could break on major versions
- Files: `requirements.txt`
- Impact: Future installs might get incompatible versions
- Migration plan: Pin specific versions or use `~=` for minor version range

## Missing Critical Features

**No Retry Logic for External Calls:**
- Problem: Webhook failures silently dropped
- Files: `progress.py:177-185`
- Current workaround: None (feature completions may not notify)
- Blocks: Reliable external integrations
- Implementation complexity: Low (add exponential backoff)

**No Structured Logging:**
- Problem: All logging via `print()` statements
- Files: Throughout codebase
- Current workaround: Console output capture
- Blocks: Log aggregation, analysis, alerting
- Implementation complexity: Medium (add logging framework)

## Test Coverage Gaps

**Core Modules Untested:**
- What's not tested: `progress.py`, `client.py`, `registry.py`, `prompts.py`
- Files: No test files for these modules
- Risk: Regressions in core functionality undetected
- Priority: High
- Difficulty to test: Medium (need to mock Claude SDK, database)

**API Endpoints Untested:**
- What's not tested: All FastAPI routers
- Files: `server/routers/*.py`
- Risk: API breaking changes undetected
- Priority: High
- Difficulty to test: Low (FastAPI TestClient available)

**React Components Untested:**
- What's not tested: All UI components
- Files: `ui/src/components/*.tsx`
- Risk: UI regressions undetected
- Priority: Medium
- Difficulty to test: Medium (need to configure Vitest + React Testing Library)

---

*Concerns audit: 2026-01-10*
*Update as issues are fixed or new ones discovered*
