import os

import git
from rich.console import Console

console = Console()

CONTEXT_FILENAME = "VIBE_CONTEXT.md"

CONTEXT_TEMPLATE = """\
# 🧠 VIBE-SYNC PROJECT CONTEXT

## 🏗 Architecture & Stack
[To be filled]

## 🚦 Current Progress
- **Completed Features:** None
- **Work in Progress:** Project Initialized

## 🐛 Known Issues / Technical Debt
None yet.

## ➡️ The Next Move
Define initial architecture.
"""


def create_base_context() -> None:
    """Create the VIBE_CONTEXT.md file if it doesn't already exist."""
    if os.path.exists(CONTEXT_FILENAME):
        console.print(
            f"[bold yellow]⚠  {CONTEXT_FILENAME} already exists. Skipping creation.[/bold yellow]"
        )
        return

    with open(CONTEXT_FILENAME, "w", encoding="utf-8") as f:
        f.write(CONTEXT_TEMPLATE)

    console.print(
        f"[bold green]✅ Created {CONTEXT_FILENAME} successfully.[/bold green]"
    )


def get_recent_changes() -> str:
    """Return a combined summary of uncommitted changes and the last commit.

    Returns a human-readable string containing:
    - The diff of any uncommitted (staged + unstaged) changes.
    - The message and diff of the most recent commit.

    If the current directory is not a git repository, returns a
    graceful fallback message instead of raising.
    """
    try:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        return "Not a git repository. No history available."

    sections: list[str] = []

    # --- Uncommitted changes (staged + unstaged) ---
    uncommitted_diff = repo.git.diff()          # unstaged
    staged_diff = repo.git.diff("--cached")     # staged

    combined_uncommitted = ""
    if staged_diff:
        combined_uncommitted += f"### Staged Changes\n```diff\n{staged_diff}\n```\n\n"
    if uncommitted_diff:
        combined_uncommitted += f"### Unstaged Changes\n```diff\n{uncommitted_diff}\n```\n\n"

    if combined_uncommitted:
        sections.append(f"## Uncommitted Changes\n\n{combined_uncommitted}")
    else:
        sections.append("## Uncommitted Changes\nNo uncommitted changes detected.\n")

    # --- Last commit ---
    commits = list(repo.iter_commits(max_count=1))
    if commits:
        last = commits[0]
        last_diff = repo.git.diff(f"{last.hexsha}~1", last.hexsha, _ok_code=[0, 128])
        sections.append(
            f"## Last Commit\n"
            f"- **Hash:** {last.hexsha[:8]}\n"
            f"- **Message:** {last.message.strip()}\n\n"
            f"```diff\n{last_diff}\n```\n"
        )
    else:
        sections.append("## Last Commit\nNo commits found in repository.\n")

    return "\n".join(sections)
