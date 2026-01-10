# Spec Format Documentation

This document defines the markdown format for feature specifications used by the AutoCoder agent system.

## Overview

Specs follow the "specs-as-source-of-truth" pattern from the Ralph Wiggum methodology. Each spec file represents a single feature or topic of concern, written in human-readable markdown with minimal machine-readable metadata in YAML frontmatter.

## File Location

Specs live in the `specs/` directory of each project:

```
my-project/
  specs/
    user-login.md
    dashboard-metrics.md
    api-rate-limiting.md
```

## File Naming

- Use `kebab-case.md` for spec filenames
- Name should clearly describe the feature
- One spec per topic of concern (passes the "one sentence without 'and'" test)

## Format Structure

```markdown
---
category: functional
priority: 1
status: pending
---

# Feature Name

Brief description of what this feature does and why it matters.

## Acceptance Criteria

- First criterion (verifiable outcome)
- Second criterion
- Third criterion

## Test Steps

1. First test step
2. Second test step
3. Third test step
```

## Frontmatter Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Feature category: `functional`, `ui`, `api`, `security`, `performance` |
| `priority` | integer | Execution priority (lower = higher priority, default 999) |
| `status` | string | Current status: `pending`, `in_progress`, `passing`, `skipped` |

### Frontmatter Rules

- Keep frontmatter minimal - only machine-readable metadata
- Human-readable content belongs in the body
- All fields are optional (defaults applied by parser)

**Defaults:**
- `category`: "functional"
- `priority`: 999
- `status`: "pending"

## Body Sections

### Title (H1)

The H1 heading becomes the feature name. Keep it concise and descriptive.

```markdown
# User Login with Email
```

### Description

Free-form prose explaining what the feature does and why. No special formatting required.

```markdown
Users can authenticate using their email and password. This is the primary authentication method for the application.
```

### Acceptance Criteria

Bulleted list of verifiable outcomes. Each criterion should be independently testable.

```markdown
## Acceptance Criteria

- Login form accepts email and password
- Invalid credentials show error message
- Successful login redirects to dashboard
- Session persists after page refresh
```

### Test Steps

Numbered steps for verification. These map to the `steps` array in the database.

```markdown
## Test Steps

1. Navigate to /login
2. Enter test@example.com in email field
3. Enter "password123" in password field
4. Click Login button
5. Verify redirect to /dashboard
6. Refresh page and verify still logged in
```

## Design Principles

1. **Keep it simple** - Markdown with minimal structure
2. **Human-readable first** - Developers should easily understand specs
3. **Frontmatter for machines** - Only metadata that needs parsing
4. **No rigid template** - Let content dictate format
5. **Markdown over JSON** - Token-efficient for LLM context

## Mapping to Feature Model

The spec parser converts markdown specs to Feature-compatible dictionaries:

| Spec Element | Feature Field |
|--------------|---------------|
| `category` frontmatter | `category` |
| `priority` frontmatter | `priority` |
| H1 title | `name` |
| Description prose | `description` |
| Test Steps list | `steps` (JSON array) |
| `status` frontmatter | `passes` (true if "passing") |

## Example Spec

```markdown
---
category: functional
priority: 1
status: pending
---

# User Login with Email

Users can authenticate using their email and password. This is the primary authentication method for the application.

## Acceptance Criteria

- Login form displays email and password fields
- Invalid credentials show "Invalid email or password" error
- Successful login redirects to /dashboard
- Session persists after page refresh
- Login button is disabled while request is pending

## Test Steps

1. Navigate to /login
2. Enter test@example.com in email field
3. Enter "password123" in password field
4. Click Login button
5. Verify redirect to /dashboard
6. Refresh page and verify still logged in
```

---

*Spec format: v1.0*
*Based on Ralph Wiggum methodology*
