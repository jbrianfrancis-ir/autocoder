# Migration Guide: Database to Specs Pattern

This guide helps you convert existing AutoCoder projects from database-only feature tracking to the hybrid specs-first pattern.

## Overview

**Before (database-only):**
- Features stored in SQLite database (`features.db`)
- Created by Initializer agent from `app_spec.txt`
- Feature content lives in database only

**After (hybrid specs-first):**
- Features defined in `specs/*.md` files (one per feature)
- Database tracks completion status (passes, in_progress)
- Specs are authoritative for WHAT to build
- Database tracks PROGRESS

## Is Migration Required?

**No.** Migration is optional. The MCP server handles both patterns:

- Projects with `specs/` directory: Uses specs for content, database for status
- Projects without `specs/` directory: Uses database for everything (current behavior)

Migrate if you want:
- Human-readable feature definitions
- Version control of requirements (specs are markdown files)
- Easier manual editing of acceptance criteria
- Token efficiency (markdown over JSON)

## Migration Steps

### Step 1: Export Existing Features to Specs

Run this from your project directory:

```bash
python -c "
from api.database import create_database, Feature
from pathlib import Path
import re

project_dir = Path('.')
engine, Session = create_database(project_dir)
session = Session()

specs_dir = project_dir / 'specs'
specs_dir.mkdir(exist_ok=True)

for feature in session.query(Feature).order_by(Feature.priority):
    # Sanitize name for filename
    safe_name = re.sub(r'[^a-z0-9]+', '-', feature.name.lower()).strip('-')
    filename = f'{feature.priority:02d}-{safe_name}.md'

    content = f'''---
category: {feature.category}
priority: {feature.priority}
status: {'passing' if feature.passes else 'pending'}
---

# {feature.name}

{feature.description}

## Test Steps

'''
    for i, step in enumerate(feature.steps, 1):
        content += f'{i}. {step}\\n'

    (specs_dir / filename).write_text(content)
    print(f'Created {filename}')

session.close()
print(f'\\nExported {session.query(Feature).count()} features to specs/')
"
```

### Step 2: Verify Specs Were Created

```bash
ls specs/
# Should show one .md file per feature, like:
# 01-user-login.md
# 02-dashboard-display.md
# 03-settings-page.md
```

### Step 3: Create AGENTS.md

Create an operational reference file for the coding agent:

```bash
cat > AGENTS.md << 'EOF'
# AGENTS.md - Quick Reference

## Build & Run

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## Project Structure

- `specs/` - Feature specifications (authoritative requirements)
- `features.db` - SQLite database (tracks completion status)
- `app_spec.txt` - Original application specification (reference only)

## Useful Commands

```bash
# List pending features
ls specs/

# Check feature progress
# Use MCP: feature_get_stats
```
EOF
```

### Step 4: Test the Integration

```bash
# Delete the database to test fresh load from specs
# WARNING: Only do this if you want to reset progress!
# rm features.db

# Start the agent - it will load specs into fresh database
python autonomous_agent_demo.py --project-dir .
```

The MCP server will:
1. Detect `specs/` directory exists
2. See database is empty (or newly created)
3. Load all specs into database with initial `passes=false`

### Step 5: Sync After Editing Specs

If you edit spec files manually, sync changes to database:

```
# Use MCP tool (from agent context)
feature_sync_from_specs
```

This updates database content while preserving status:
- New specs → added as pending features
- Changed specs → content updated, status preserved
- Removed specs → database entries NOT deleted (manual cleanup if needed)

## File Format Reference

See [spec-format.md](./spec-format.md) for the complete spec file format.

Quick reference:

```markdown
---
category: functional
priority: 1
status: pending
---

# Feature Name

Description of what this feature does.

## Acceptance Criteria

- User can do X
- System responds with Y
- Error handling for Z

## Test Steps

1. Navigate to /page
2. Click button
3. Verify result appears
```

## Rollback

To revert to database-only mode:

```bash
# Simply delete or rename the specs directory
mv specs specs.backup

# MCP server will use database-only mode
```

Your database remains intact with all progress.

## Troubleshooting

### Features not loading from specs

Check that:
1. `specs/` directory exists in project root
2. Spec files have `.md` extension
3. Each spec has valid frontmatter (between `---` delimiters)
4. Each spec has an H1 title (`# Feature Name`)

### Sync not updating features

Features are matched by name (H1 title). If you rename a feature:
- Old database entry remains (with old name)
- New entry created (with new name)
- Manually delete old entry if needed

### Status not preserved after sync

Status (passes, in_progress) is preserved for features matched by name.
New features start with `passes=false`.
