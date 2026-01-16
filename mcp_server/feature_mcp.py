#!/usr/bin/env python3
"""
MCP Server for Feature Management
==================================

Provides tools to manage features in the autonomous coding system,
replacing the previous FastAPI-based REST API.

Tools:
- feature_get_stats: Get progress statistics
- feature_get_next: Get next feature to implement
- feature_get_for_regression: Get random passing features for testing
- feature_mark_passing: Mark a feature as passing
- feature_skip: Skip a feature (move to end of queue)
- feature_mark_in_progress: Mark a feature as in-progress
- feature_clear_in_progress: Clear in-progress status
- feature_create_bulk: Create multiple features at once
"""

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from sqlalchemy.sql.expression import func

# Add parent directory to path so we can import from api module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging for subprocess context
# MCP server runs as separate process, needs own configuration
from logging_config import configure_logging
configure_logging()

logger = logging.getLogger(__name__)

from api.database import Feature, create_database
from api.migration import migrate_json_to_sqlite
from spec_parser import parse_specs_directory, spec_to_feature_dict

# Configuration from environment
PROJECT_DIR = Path(os.environ.get("PROJECT_DIR", ".")).resolve()


# Pydantic models for input validation
class MarkPassingInput(BaseModel):
    """Input for marking a feature as passing."""
    feature_id: int = Field(..., description="The ID of the feature to mark as passing", ge=1)


class SkipFeatureInput(BaseModel):
    """Input for skipping a feature."""
    feature_id: int = Field(..., description="The ID of the feature to skip", ge=1)


class MarkInProgressInput(BaseModel):
    """Input for marking a feature as in-progress."""
    feature_id: int = Field(..., description="The ID of the feature to mark as in-progress", ge=1)


class ClearInProgressInput(BaseModel):
    """Input for clearing in-progress status."""
    feature_id: int = Field(..., description="The ID of the feature to clear in-progress status", ge=1)


class RegressionInput(BaseModel):
    """Input for getting regression features."""
    limit: int = Field(default=3, ge=1, le=10, description="Maximum number of passing features to return")


class FeatureCreateItem(BaseModel):
    """Schema for creating a single feature."""
    category: str = Field(..., min_length=1, max_length=100, description="Feature category")
    name: str = Field(..., min_length=1, max_length=255, description="Feature name")
    description: str = Field(..., min_length=1, description="Detailed description")
    steps: list[str] = Field(..., min_length=1, description="Implementation/test steps")


class BulkCreateInput(BaseModel):
    """Input for bulk creating features."""
    features: list[FeatureCreateItem] = Field(..., min_length=1, description="List of features to create")


# Global database session maker (initialized on startup)
_session_maker = None
_engine = None


def format_feature_markdown(
    feature: Feature,
    include_spec: bool = False,
    spec_filepath: str | None = None,
    spec_description: str | None = None,
    spec_steps: list[str] | None = None,
) -> str:
    """Format a Feature as markdown for token-efficient agent consumption.

    Args:
        feature: The Feature object to format
        include_spec: Whether to include spec file information
        spec_filepath: Path to the spec file (if include_spec is True)
        spec_description: Description from the spec (if include_spec is True)
        spec_steps: Steps from the spec (if include_spec is True)

    Returns:
        Markdown-formatted string representation of the feature
    """
    status = "passing" if feature.passes else "in_progress" if feature.in_progress else "pending"

    lines: list[str] = [
        f"**ID:** {feature.id} | **Priority:** {feature.priority} | **Category:** {feature.category} | **Status:** {status}",
        "",
        f"### {feature.name}",
        "",
        str(feature.description),
        "",
        "### Test Steps",
    ]
    for i, step in enumerate(feature.steps, 1):
        lines.append(f"{i}. {step}")

    if include_spec and spec_filepath:
        lines.extend([
            "",
            "### Spec File",
            f"`{spec_filepath}`",
        ])
        if spec_description:
            lines.extend([
                "",
                "### Spec Description",
                spec_description,
            ])
        if spec_steps:
            lines.extend([
                "",
                "### Spec Steps",
            ])
            for i, step in enumerate(spec_steps, 1):
                lines.append(f"{i}. {step}")

    return "\n".join(lines)


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Initialize database on startup, cleanup on shutdown."""
    global _session_maker, _engine

    logger.info("Initializing MCP server for project: %s", PROJECT_DIR)

    # Create project directory if it doesn't exist
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database
    _engine, _session_maker = create_database(PROJECT_DIR)
    logger.debug("Database initialized at %s", PROJECT_DIR / "features.db")

    # Run migration if needed (converts legacy JSON to SQLite)
    migrate_json_to_sqlite(PROJECT_DIR, _session_maker)

    # Load specs if specs/ directory exists and database is empty
    specs_dir = PROJECT_DIR / "specs"
    if specs_dir.exists():
        session = _session_maker()
        try:
            feature_count = session.query(Feature).count()
            if feature_count == 0:
                # Database is empty, load from specs
                specs = parse_specs_directory(specs_dir)
                for spec in specs:
                    feature_dict = spec_to_feature_dict(spec)
                    feature_dict["spec_filepath"] = spec["filepath"]
                    db_feature = Feature(
                        priority=feature_dict["priority"],
                        category=feature_dict["category"],
                        name=feature_dict["name"],
                        description=feature_dict["description"],
                        steps=feature_dict["steps"],
                        passes=feature_dict["passes"],
                        in_progress=feature_dict["in_progress"],
                    )
                    session.add(db_feature)
                session.commit()
                logger.info("Loaded %d features from specs directory", len(specs))
        finally:
            session.close()

    yield

    # Cleanup
    if _engine:
        _engine.dispose()
    logger.info("MCP server shutdown, database connection closed")


# Initialize the MCP server
mcp = FastMCP("features", lifespan=server_lifespan)


def get_session():
    """Get a new database session."""
    if _session_maker is None:
        logger.error("Database not initialized")
        raise RuntimeError("Database not initialized")
    return _session_maker()


@mcp.tool()
def feature_get_stats() -> str:
    """Get statistics about feature completion progress.

    Returns the number of passing features, in-progress features, total features,
    and completion percentage. Use this to track overall progress of the implementation.

    Returns:
        Markdown-formatted progress statistics for token-efficient consumption.
    """
    logger.debug("Getting feature stats")
    session = get_session()
    try:
        total = session.query(Feature).count()
        passing = session.query(Feature).filter(Feature.passes == True).count()
        in_progress = session.query(Feature).filter(Feature.in_progress == True).count()
        percentage = round((passing / total) * 100, 1) if total > 0 else 0.0
        remaining = total - passing - in_progress

        return f"""## Progress
- Passing: {passing}/{total} ({percentage}%)
- In Progress: {in_progress}
- Remaining: {remaining}"""
    finally:
        session.close()


@mcp.tool()
def feature_get_next() -> str:
    """Get the highest-priority pending feature to work on.

    Returns the feature with the lowest priority number that has passes=false.
    Use this at the start of each coding session to determine what to implement next.

    If specs/ directory exists, also includes spec_filepath pointing to the
    authoritative spec file. The spec file contains full acceptance criteria
    and detailed requirements.

    Returns:
        Markdown-formatted feature details for token-efficient consumption.
        Returns error message if all features are passing.
    """
    logger.debug("Getting next feature to implement")
    session = get_session()
    try:
        feature = (
            session.query(Feature)
            .filter(Feature.passes == False)
            .order_by(Feature.priority.asc(), Feature.id.asc())
            .first()
        )

        if feature is None:
            return "**Error:** All features are passing! No more work to do."

        # Check for matching spec file
        spec_filepath = None
        spec_description = None
        spec_steps = None
        specs_dir = PROJECT_DIR / "specs"
        if specs_dir.exists():
            # Find spec by matching name
            specs = parse_specs_directory(specs_dir)
            for spec in specs:
                if spec["name"] == feature.name:
                    spec_filepath = spec["filepath"]
                    spec_description = spec["description"]
                    spec_steps = spec["steps"]
                    break

        result = "## Next Feature\n\n"
        result += format_feature_markdown(
            feature,
            include_spec=bool(spec_filepath),
            spec_filepath=spec_filepath,
            spec_description=spec_description,
            spec_steps=spec_steps,
        )
        return result
    finally:
        session.close()


@mcp.tool()
def feature_get_for_regression(
    limit: Annotated[int, Field(default=3, ge=1, le=10, description="Maximum number of passing features to return")] = 3
) -> str:
    """Get random passing features for regression testing.

    Returns a random selection of features that are currently passing.
    Use this to verify that previously implemented features still work
    after making changes.

    Args:
        limit: Maximum number of features to return (1-10, default 3)

    Returns:
        Markdown-formatted list of features for token-efficient consumption.
    """
    logger.debug("Getting %d random passing features for regression", limit)
    session = get_session()
    try:
        features = (
            session.query(Feature)
            .filter(Feature.passes == True)
            .order_by(func.random())
            .limit(limit)
            .all()
        )

        if not features:
            return "## Regression Features\n\nNo passing features available for regression testing."

        lines = [
            f"## Regression Features ({len(features)} selected)",
            "",
        ]
        for feature in features:
            lines.append(format_feature_markdown(feature))
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines).rstrip("\n---\n")
    finally:
        session.close()


@mcp.tool()
def feature_mark_passing(
    feature_id: Annotated[int, Field(description="The ID of the feature to mark as passing", ge=1)]
) -> str:
    """Mark a feature as passing after successful implementation.

    Updates the feature's passes field to true and clears the in_progress flag.
    Use this after you have implemented the feature and verified it works correctly.

    Args:
        feature_id: The ID of the feature to mark as passing

    Returns:
        Markdown confirmation of the status change, or error if not found.
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return f"**Error:** Feature with ID {feature_id} not found"

        feature.passes = True
        feature.in_progress = False
        session.commit()
        session.refresh(feature)

        logger.info("Feature %d marked as passing", feature_id)
        return f"Feature marked passing: **{feature.name}** (ID: {feature.id})"
    finally:
        session.close()


@mcp.tool()
def feature_skip(
    feature_id: Annotated[int, Field(description="The ID of the feature to skip", ge=1)]
) -> str:
    """Skip a feature by moving it to the end of the priority queue.

    Use this when a feature cannot be implemented yet due to:
    - Dependencies on other features that aren't implemented yet
    - External blockers (missing assets, unclear requirements)
    - Technical prerequisites that need to be addressed first

    The feature's priority is set to max_priority + 1, so it will be
    worked on after all other pending features. Also clears the in_progress
    flag so the feature returns to "pending" status.

    Args:
        feature_id: The ID of the feature to skip

    Returns:
        Markdown confirmation of the skip action, or error if not found/already passing.
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return f"**Error:** Feature with ID {feature_id} not found"

        if feature.passes:
            return "**Error:** Cannot skip a feature that is already passing"

        old_priority = feature.priority

        # Get max priority and set this feature to max + 1
        max_priority_result = session.query(Feature.priority).order_by(Feature.priority.desc()).first()
        new_priority = (max_priority_result[0] + 1) if max_priority_result else 1

        feature.priority = new_priority
        feature.in_progress = False
        session.commit()
        session.refresh(feature)

        logger.info("Feature %d skipped, moved to priority %d", feature_id, new_priority)
        return f"""Feature skipped: **{feature.name}** (ID: {feature.id})
- Old priority: {old_priority}
- New priority: {new_priority}
- Moved to end of queue"""
    finally:
        session.close()


@mcp.tool()
def feature_mark_in_progress(
    feature_id: Annotated[int, Field(description="The ID of the feature to mark as in-progress", ge=1)]
) -> str:
    """Mark a feature as in-progress. Call immediately after feature_get_next().

    This prevents other agent sessions from working on the same feature.
    Use this as soon as you retrieve a feature to work on.

    Args:
        feature_id: The ID of the feature to mark as in-progress

    Returns:
        Markdown confirmation with feature details, or error if not found or already in-progress.
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return f"**Error:** Feature with ID {feature_id} not found"

        if feature.passes:
            return f"**Error:** Feature with ID {feature_id} is already passing"

        if feature.in_progress:
            return f"**Error:** Feature with ID {feature_id} is already in-progress"

        feature.in_progress = True
        session.commit()
        session.refresh(feature)

        logger.debug("Feature %d marked in-progress", feature_id)
        return f"Feature marked in-progress: **{feature.name}** (ID: {feature.id})"
    finally:
        session.close()


@mcp.tool()
def feature_clear_in_progress(
    feature_id: Annotated[int, Field(description="The ID of the feature to clear in-progress status", ge=1)]
) -> str:
    """Clear in-progress status from a feature.

    Use this when abandoning a feature or manually unsticking a stuck feature.
    The feature will return to the pending queue.

    Args:
        feature_id: The ID of the feature to clear in-progress status

    Returns:
        Markdown confirmation, or error if not found.
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return f"**Error:** Feature with ID {feature_id} not found"

        feature.in_progress = False
        session.commit()
        session.refresh(feature)

        logger.debug("Feature %d in-progress cleared", feature_id)
        return f"In-progress cleared: **{feature.name}** (ID: {feature.id}) - returned to pending"
    finally:
        session.close()


@mcp.tool()
def feature_create_bulk(
    features: Annotated[list[dict], Field(description="List of features to create, each with category, name, description, and steps")]
) -> str:
    """Create multiple features in a single operation.

    Features are assigned sequential priorities based on their order.
    All features start with passes=false.

    This is typically used by the initializer agent to set up the initial
    feature list from the app specification.

    Args:
        features: List of features to create, each with:
            - category (str): Feature category
            - name (str): Feature name
            - description (str): Detailed description
            - steps (list[str]): Implementation/test steps

    Returns:
        JSON with: created (int) - number of features created
    """
    session = get_session()
    try:
        # Get the starting priority
        max_priority_result = session.query(Feature.priority).order_by(Feature.priority.desc()).first()
        start_priority = (max_priority_result[0] + 1) if max_priority_result else 1

        created_count = 0
        for i, feature_data in enumerate(features):
            # Validate required fields
            if not all(key in feature_data for key in ["category", "name", "description", "steps"]):
                return json.dumps({
                    "error": f"Feature at index {i} missing required fields (category, name, description, steps)"
                })

            db_feature = Feature(
                priority=start_priority + i,
                category=feature_data["category"],
                name=feature_data["name"],
                description=feature_data["description"],
                steps=feature_data["steps"],
                passes=False,
            )
            session.add(db_feature)
            created_count += 1

        session.commit()

        logger.info("Created %d features in bulk", created_count)
        return json.dumps({"created": created_count}, indent=2)
    except Exception as e:
        session.rollback()
        logger.error("Bulk create failed: %s", e)
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@mcp.tool()
def feature_sync_from_specs() -> str:
    """Sync features from specs/ directory to database.

    Re-parses the specs/ directory and updates the database:
    - New specs are added as new features
    - Existing features (matched by name) have content updated but preserve status
    - Specs not in directory are NOT deleted (preserves manual features)

    Use this after adding or modifying spec files to update the feature list
    without losing progress on already-passing features.

    Returns:
        Markdown summary of sync results.
    """
    specs_dir = PROJECT_DIR / "specs"
    if not specs_dir.exists():
        return "**Error:** No specs/ directory found. Create specs/ with markdown spec files first."

    session = get_session()
    try:
        specs = parse_specs_directory(specs_dir)

        added = 0
        updated = 0
        unchanged = 0

        for spec in specs:
            feature_dict = spec_to_feature_dict(spec)

            # Try to find existing feature by name
            existing = session.query(Feature).filter(Feature.name == spec["name"]).first()

            if existing:
                # Update content but preserve status (passes, in_progress)
                content_changed = (
                    existing.category != feature_dict["category"]
                    or existing.description != feature_dict["description"]
                    or existing.steps != feature_dict["steps"]
                )

                if content_changed:
                    existing.category = feature_dict["category"]
                    existing.description = feature_dict["description"]
                    existing.steps = feature_dict["steps"]
                    # Note: priority from spec may differ; update if spec is authoritative
                    existing.priority = feature_dict["priority"]
                    updated += 1
                else:
                    unchanged += 1
            else:
                # New feature from spec
                db_feature = Feature(
                    priority=feature_dict["priority"],
                    category=feature_dict["category"],
                    name=feature_dict["name"],
                    description=feature_dict["description"],
                    steps=feature_dict["steps"],
                    passes=feature_dict["passes"],
                    in_progress=feature_dict["in_progress"],
                )
                session.add(db_feature)
                added += 1

        session.commit()

        logger.info("Synced specs: added=%d, updated=%d, unchanged=%d", added, updated, unchanged)
        return f"""## Specs Synced
- Added: {added}
- Updated: {updated}
- Unchanged: {unchanged}
- Total specs: {len(specs)}"""
    except Exception as e:
        session.rollback()
        logger.error("Sync from specs failed: %s", e)
        return f"**Error:** {e}"
    finally:
        session.close()


if __name__ == "__main__":
    mcp.run()
