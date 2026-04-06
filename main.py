import typer
from rich.console import Console
import os
from typing import Optional

# Import core logic, AI bridge, and hooks
from vibe_core import create_base_context, get_recent_changes, CONTEXT_FILENAME
from ai_bridge import update_context_via_ai, MissingAPIKeyError
from hooks import install_hooks as _install_hooks

app = typer.Typer(
    name="vibe-sync",
    help="AI context preservation CLI tool for tracking project progress.",
)
console = Console()


@app.command()
def init():
    """Initialize a new vibe-sync project in the current directory."""
    with console.status("[bold blue]Initialising Vibe-Sync...[/bold blue]"):
        create_base_context()
    console.print("[bold green]✅ VIBE_CONTEXT.md generated![/bold green]")


@app.command()
def commit(
    message: Optional[str] = typer.Option(
        None, "--message", "-m",
        help="Commit message to include as extra context for the AI.",
    ),
):
    """Create an AI-powered context commit based on recent Git changes."""
    # 1. Check if the context file exists
    if not os.path.exists(CONTEXT_FILENAME):
        console.print(
            f"[bold red]❌ Error:[/bold red] {CONTEXT_FILENAME} not found. "
            "Run [bold]vibe-sync init[/bold] first."
        )
        raise typer.Exit(code=1)

    try:
        with console.status("[bold magenta]Analyzing recent changes...[/bold magenta]") as status:
            # 2. Read existing context
            with open(CONTEXT_FILENAME, "r", encoding="utf-8") as f:
                current_context = f.read()

            # 3. Get Git diffs
            status.update("[bold cyan]Gathering Git history...[/bold cyan]")
            git_diff = get_recent_changes()

            # Append the commit message if provided (e.g. from the hook)
            if message:
                git_diff += f"\n\n## Commit Message\n{message}\n"

            # 4. Call Gemini to update context
            status.update("[bold yellow]Consulting the AI Oracle...[/bold yellow]")
            updated_context = update_context_via_ai(current_context, git_diff)

            # 5. Overwrite the file
            with open(CONTEXT_FILENAME, "w", encoding="utf-8") as f:
                f.write(updated_context)

        console.print("[bold blue]🧠 Vibe-Sync Brain Updated successfully![/bold blue]")

    except MissingAPIKeyError as e:
        console.print(f"[bold red]🔑 API Key Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]💥 An unexpected error occurred:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("install-hooks")
def install_hooks():
    """Install a Git post-commit hook to auto-update VIBE_CONTEXT.md on every commit."""
    _install_hooks()


if __name__ == "__main__":
    app()
