"""
Vibe-Sync MCP Server
Exposes project context to AI agents via the Model Context Protocol.
"""

import os
from fastmcp import FastMCP

CONTEXT_FILENAME = "VIBE_CONTEXT.md"

mcp = FastMCP(
    name="vibe-sync",
    instructions=(
        "Vibe-Sync is a project context preservation tool. "
        "Use the get_latest_vibe tool to read the current project state "
        "before exploring the filesystem. This saves tokens and prevents "
        "cold-start waste."
    ),
)


@mcp.tool()
def get_latest_vibe() -> str:
    """
    Returns the last 10 lines of VIBE_CONTEXT.md along with any active goals.

    Use this tool at the START of every session to understand the project's
    current state, architecture, progress, and next steps — without needing
    to explore the file tree.
    """
    # Locate VIBE_CONTEXT.md — search cwd and common project roots
    context_path = _find_context_file()
    if context_path is None:
        return (
            "⚠️  VIBE_CONTEXT.md not found. "
            "Run `vibe-sync init` in your project directory first."
        )

    with open(context_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # --- Build the response ---
    sections: list[str] = []

    # Full context summary (last 10 lines give the most recent state)
    tail = lines[-10:] if len(lines) > 10 else lines
    sections.append("## 📋 Latest Vibe (last 10 lines)")
    sections.append("".join(tail).strip())

    # Extract active goals from "The Next Move" section
    active_goals = _extract_section(lines, "➡️ The Next Move")
    if active_goals:
        sections.append("\n## 🎯 Active Goals")
        sections.append(active_goals)

    # Extract work in progress
    wip = _extract_section(lines, "Work in Progress")
    if wip:
        sections.append("\n## 🔨 Work in Progress")
        sections.append(wip)

    return "\n\n".join(sections)


@mcp.tool()
def read_vibe() -> str:
    """
    Returns the full contents of VIBE_CONTEXT.md.

    Use this as the FIRST action in a new session to load full project context
    in a single read, avoiding expensive file-tree exploration.
    """
    context_path = _find_context_file()
    if context_path is None:
        return (
            "⚠️  VIBE_CONTEXT.md not found. "
            "Run `vibe-sync init` in your project directory first."
        )

    with open(context_path, "r", encoding="utf-8") as f:
        return f.read()


# ── Helpers ──────────────────────────────────────────────────────────────────


def _find_context_file() -> str | None:
    """Search for VIBE_CONTEXT.md starting from cwd, walking upward."""
    current = os.getcwd()
    while True:
        candidate = os.path.join(current, CONTEXT_FILENAME)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def _extract_section(lines: list[str], heading_fragment: str) -> str:
    """Pull the text under a heading that contains `heading_fragment`."""
    capturing = False
    captured: list[str] = []
    for line in lines:
        if heading_fragment in line:
            capturing = True
            continue
        if capturing:
            # Stop at the next heading
            if line.startswith("## "):
                break
            captured.append(line)
    return "".join(captured).strip()


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
