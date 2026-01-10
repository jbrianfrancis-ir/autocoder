# Project: AutoCoder

## What This Is

An autonomous coding agent system with a React-based UI that uses the Claude Agent SDK to build complete applications over multiple sessions using a two-agent pattern (Initializer + Coding Agent).

## Core Value

Enables developers to define application specifications and have an AI agent implement features autonomously across multiple sessions, with real-time progress tracking and human oversight through a modern web interface.

## Target User

Developers who want to prototype applications using AI-assisted coding with structured feature tracking and verifiable progress.

## Definitive Reference

The [Ralph Wiggum methodology](https://github.com/ghuntley/how-to-ralph-wiggum) by ghuntley is the authoritative guide for agent harness patterns. This project should align with those principles.

## Key Patterns from Ralph Wiggum

**Core Loop Principles:**
- Deterministic fresh-start architecture (agent starts from known state each iteration)
- Monolithic single-task operation (one task per loop = 100% context utilization)
- Backpressure-driven validation (tests/lint/type-check force correctness before commits)

**Feature Tracking:**
- Specs as source of truth (`specs/FILENAME.md` per topic of concern)
- Gap analysis planning (compare specs against code, produce implementation plan)
- Implementation plan as shared state between iterations

**Progress Management:**
- File-based state persistence (`IMPLEMENTATION_PLAN.md`)
- Plan updates as side effects during building
- Iterative convergence through repeated execution

**Key Files:**
- `PROMPT_plan.md` - Planning mode instructions
- `PROMPT_build.md` - Building mode instructions
- `AGENTS.md` - Operational reference (build/test commands)
- `IMPLEMENTATION_PLAN.md` - Current task list

**Best Practices:**
- Use subagents to extend memory (~156KB per subagent)
- Markdown over JSON for token efficiency
- Isolated sandboxes with understood blast radius
- Add guardrails to prompts when failure patterns emerge

## Current State

- Working two-agent system (Initializer + Coding Agent)
- React UI with WebSocket real-time updates
- Feature MCP server for feature management
- Playwright MCP for browser automation
- YOLO mode for rapid prototyping

## Codebase Documentation

See `.planning/codebase/` for detailed analysis:
- `STACK.md` - Technologies and dependencies
- `ARCHITECTURE.md` - System design and patterns
- `STRUCTURE.md` - Directory layout
- `CONVENTIONS.md` - Code style
- `TESTING.md` - Test structure
- `INTEGRATIONS.md` - External services
- `CONCERNS.md` - Technical debt

---

*Project initialized: 2026-01-10*
