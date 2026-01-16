# Project: AutoCoder

## What This Is

An autonomous coding agent system with a React-based UI that uses the Claude Agent SDK to build complete applications over multiple sessions. Now aligned with the Ralph Wiggum methodology for reliable autonomous operation.

## Core Value

Enables developers to define application specifications and have an AI agent implement features autonomously across multiple sessions, with real-time progress tracking and human oversight through a modern web interface.

## Target User

Developers who want to prototype applications using AI-assisted coding with structured feature tracking and verifiable progress.

## Current Milestone: v1.1 Foundation Hardening

**Goal:** Improve observability, document security posture, and add test confidence for core modules.

**Target features:**
- Structured logging with consistent formatting and log levels
- Security blast radius documentation for resource limits and environment sanitization
- Test coverage for agent.py, client.py, and security.py

## Requirements

### Validated

- Spec-driven architecture with hybrid spec-database pattern - v1.0
- Deterministic fresh-start loop with structured progress file - v1.0
- Backpressure validation gates before commits - v1.0
- Markdown over JSON for token efficiency - v1.0
- Sandbox hardening with CORS, symlink checks, blast radius docs - v1.0
- Resource limits and environment sanitization helpers - v1.0

### Active

- Structured logging with consistent formatting and log levels
- Security blast radius documentation (where to apply existing helpers)
- Test coverage for agent.py, client.py, security.py

### Out of Scope

- Multi-project parallel execution - focus on single-project reliability first
- Cloud deployment - local development tool

## Current State

**Version:** v1.0 Ralph Wiggum Alignment (shipped 2026-01-11)

**Codebase:**
- 8,892 lines of Python
- Tech stack: Python, FastAPI, React, SQLite, Claude Agent SDK

**Architecture:**
- Two-agent system (Initializer + Coding Agent)
- React UI with WebSocket real-time updates
- Feature MCP server for feature management
- Playwright MCP for browser automation
- YOLO mode for rapid prototyping

**Ralph Wiggum Patterns Implemented:**
- Specs as source of truth (`specs/FILENAME.md` per feature)
- Deterministic fresh-start architecture (structured claude-progress.txt)
- Backpressure-driven validation (STEP 8: VALIDATION GATES)
- Markdown over JSON (MCP tools return markdown)
- Isolated sandboxes with understood blast radius (BLAST_RADIUS.md)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| YAML frontmatter for specs | Human-readable, aligns with markdown-over-JSON | Good |
| Hybrid spec-database architecture | Specs for content, database for status tracking | Good |
| Structured claude-progress.txt | Determinism with human observability | Good |
| Validation gates as STEP 8 | Enforces quality before any commit | Good |
| Markdown MCP responses | Token efficiency (~40% reduction) | Good |
| Localhost-only CORS | Security without complexity | Good |
| Resource/env helpers not wired in | Avoid scope creep, helpers ready when needed | Pending |

## Definitive Reference

The [Ralph Wiggum methodology](https://github.com/ghuntley/how-to-ralph-wiggum) by ghuntley is the authoritative guide for agent harness patterns.

## Codebase Documentation

See `.planning/codebase/` for detailed analysis:
- `STACK.md` - Technologies and dependencies
- `ARCHITECTURE.md` - System design and patterns
- `STRUCTURE.md` - Directory layout
- `CONVENTIONS.md` - Code style
- `TESTING.md` - Test structure
- `INTEGRATIONS.md` - External services
- `CONCERNS.md` - Technical debt
- `BLAST_RADIUS.md` - Security posture
- `COMMAND_AUDIT.md` - Allowed commands security audit

---

*Last updated: 2026-01-16 after milestone v1.1 started*
