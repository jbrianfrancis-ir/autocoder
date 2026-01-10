"""
Spec Parser Module
==================

Parses markdown spec files into structured data compatible with the Feature model.
Uses only standard library to minimize dependencies.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parse YAML-like frontmatter from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    frontmatter: dict[str, Any] = {}

    # Check for frontmatter delimiters
    if not content.startswith("---"):
        return frontmatter, content

    # Find closing delimiter
    lines = content.split("\n")
    end_index = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break

    if end_index == -1:
        return frontmatter, content

    # Parse frontmatter lines
    for line in lines[1:end_index]:
        line = line.strip()
        if not line or ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Type conversion
        if value.lower() in ("true", "false"):
            frontmatter[key] = value.lower() == "true"
        elif value.isdigit():
            frontmatter[key] = int(value)
        else:
            frontmatter[key] = value

    # Return remaining content after frontmatter
    remaining = "\n".join(lines[end_index + 1 :]).strip()
    return frontmatter, remaining


def extract_title(content: str) -> tuple[str, str]:
    """
    Extract H1 title from markdown content.

    Args:
        content: Markdown content (without frontmatter)

    Returns:
        Tuple of (title, remaining content)
    """
    lines = content.split("\n")
    title = ""
    start_index = 0

    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            start_index = i + 1
            break

    remaining = "\n".join(lines[start_index:]).strip()
    return title, remaining


def extract_section(content: str, heading: str) -> str:
    """
    Extract content under a specific H2 heading.

    Args:
        content: Markdown content
        heading: H2 heading to find (without ##)

    Returns:
        Content under that heading, or empty string if not found
    """
    lines = content.split("\n")
    section_lines: list[str] = []
    in_section = False

    for line in lines:
        # Check for heading match
        if line.lower().strip().startswith(f"## {heading.lower()}"):
            in_section = True
            continue

        # Check for next H2 heading (end of section)
        if in_section and line.strip().startswith("## "):
            break

        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def extract_description(content: str) -> str:
    """
    Extract description (content before first H2 heading).

    Args:
        content: Markdown content (without title)

    Returns:
        Description text
    """
    lines = content.split("\n")
    desc_lines: list[str] = []

    for line in lines:
        if line.strip().startswith("## "):
            break
        desc_lines.append(line)

    return "\n".join(desc_lines).strip()


def extract_list_items(section: str) -> list[str]:
    """
    Extract list items from a section.

    Handles both ordered (1. item) and unordered (- item) lists.

    Args:
        section: Section content

    Returns:
        List of item texts
    """
    items: list[str] = []
    lines = section.split("\n")

    for line in lines:
        line = line.strip()
        # Unordered list
        if line.startswith("- "):
            items.append(line[2:].strip())
        # Ordered list
        elif re.match(r"^\d+\.\s+", line):
            items.append(re.sub(r"^\d+\.\s+", "", line).strip())

    return items


def parse_spec(filepath: Path) -> dict[str, Any]:
    """
    Parse a single spec file into a structured dictionary.

    Args:
        filepath: Path to the spec markdown file

    Returns:
        Dictionary with spec data:
        - category: str (from frontmatter, default "functional")
        - priority: int (from frontmatter, default 999)
        - name: str (from H1 title)
        - description: str (from content before first H2)
        - steps: list[str] (from Test Steps section)
        - status: str (from frontmatter, default "pending")
        - filepath: str (source file path)
    """
    content = filepath.read_text(encoding="utf-8")

    # Parse frontmatter
    frontmatter, body = parse_frontmatter(content)

    # Extract title
    title, body = extract_title(body)

    # Extract description (content before first H2)
    description = extract_description(body)

    # Extract test steps
    steps_section = extract_section(body, "test steps")
    steps = extract_list_items(steps_section)

    # Extract acceptance criteria (for description enrichment if no description)
    if not description:
        criteria_section = extract_section(body, "acceptance criteria")
        if criteria_section:
            criteria = extract_list_items(criteria_section)
            description = "; ".join(criteria) if criteria else ""

    return {
        "category": frontmatter.get("category", "functional"),
        "priority": frontmatter.get("priority", 999),
        "name": title or filepath.stem.replace("-", " ").title(),
        "description": description,
        "steps": steps,
        "status": frontmatter.get("status", "pending"),
        "filepath": str(filepath),
    }


def parse_specs_directory(specs_dir: Path) -> list[dict[str, Any]]:
    """
    Parse all spec files in a directory.

    Args:
        specs_dir: Path to directory containing spec markdown files

    Returns:
        List of parsed spec dictionaries, sorted by priority
    """
    if not specs_dir.exists():
        return []

    specs: list[dict[str, Any]] = []

    for filepath in specs_dir.glob("*.md"):
        try:
            spec = parse_spec(filepath)
            specs.append(spec)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
            continue

    # Sort by priority (lower = higher priority)
    specs.sort(key=lambda s: s["priority"])
    return specs


def spec_to_feature_dict(spec: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a parsed spec to Feature model-compatible dictionary.

    Args:
        spec: Parsed spec dictionary from parse_spec()

    Returns:
        Dictionary compatible with Feature model fields
    """
    return {
        "category": spec["category"],
        "priority": spec["priority"],
        "name": spec["name"],
        "description": spec["description"],
        "steps": spec["steps"],
        "passes": spec["status"] == "passing",
        "in_progress": spec["status"] == "in_progress",
    }
