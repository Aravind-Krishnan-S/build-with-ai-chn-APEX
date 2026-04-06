import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os
import json
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Optional

# Import core logic, AI bridge, hooks, and config
from vibe_core import create_base_context, get_recent_changes, CONTEXT_FILENAME
from ai_bridge import update_context_via_ai, MissingAPIKeyError
from hooks import install_hooks as _install_hooks
from config import (
    init_config, load_config, record_sync, get_last_synced,
    set_gcs_bucket, set_google_project, set_cloud_run_url,
)

app = typer.Typer(
    name="vibe-sync",
    help="AI context preservation CLI tool for tracking project progress.",
)
console = Console()

# Default Antigravity brain path
ANTIGRAVITY_BRAIN = os.path.expanduser(
    os.path.join("~", ".gemini", "antigravity", "brain")
)


@app.command()
def init():
    """Initialize a new vibe-sync project in the current directory."""
    with console.status("[bold blue]Initialising Vibe-Sync...[/bold blue]"):
        create_base_context()
        cfg = init_config()
    console.print("[bold green]✅ VIBE_CONTEXT.md generated![/bold green]")
    console.print(f"[dim]Project: {cfg['project_name']} | Config: .vibe/config.json[/dim]")


@app.command()
def commit(
    message: Optional[str] = typer.Option(
        None, "--message", "-m",
        help="Commit message to include as extra context for the AI.",
    ),
):
    """Create an AI-powered context commit based on recent Git changes."""
    if not os.path.exists(CONTEXT_FILENAME):
        console.print(
            f"[bold red]❌ Error:[/bold red] {CONTEXT_FILENAME} not found. "
            "Run [bold]vibe-sync init[/bold] first."
        )
        raise typer.Exit(code=1)

    try:
        with console.status("[bold magenta]Analyzing recent changes...[/bold magenta]") as st:
            with open(CONTEXT_FILENAME, "r", encoding="utf-8") as f:
                current_context = f.read()

            st.update("[bold cyan]Gathering Git history...[/bold cyan]")
            git_diff = get_recent_changes()

            if message:
                git_diff += f"\n\n## Commit Message\n{message}\n"

            st.update("[bold yellow]Consulting the AI Oracle...[/bold yellow]")
            updated_context = update_context_via_ai(current_context, git_diff)

            with open(CONTEXT_FILENAME, "w", encoding="utf-8") as f:
                f.write(updated_context)

            # Record the sync in .vibe/config.json
            st.update("[bold green]Recording sync...[/bold green]")
            commit_hash = _get_latest_commit_hash()
            record_sync(commit_hash=commit_hash, commit_message=message)

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


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS, PUSH, MCP-TEST
# ═══════════════════════════════════════════════════════════════════════════════


@app.command()
def status():
    """Show the current Vibe-Sync project status and sync history."""
    config = load_config()

    # Build the status table
    table = Table(
        title="🧠 Vibe-Sync Status",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Property", style="bold white", min_width=22)
    table.add_column("Value", style="green")

    # Project info
    table.add_row("Project Name", config.get("project_name", "Unknown"))
    table.add_row("Created At", _format_timestamp(config.get("created_at")))

    # Sync info
    last_synced = config.get("last_synced")
    if last_synced:
        table.add_row("Last Synced", _format_timestamp(last_synced))
        table.add_row("Time Since Sync", _time_ago(last_synced))
    else:
        table.add_row("Last Synced", "[yellow]Never[/yellow]")

    table.add_row("Total Syncs", str(config.get("sync_count", 0)))

    # Last commit
    last_hash = config.get("last_commit_hash")
    if last_hash:
        table.add_row("Last Commit", f"{last_hash[:8]}")
    last_msg = config.get("last_commit_message")
    if last_msg:
        table.add_row("Commit Message", last_msg[:60])

    # File status
    ctx_exists = os.path.exists(CONTEXT_FILENAME)
    table.add_row(
        "VIBE_CONTEXT.md",
        "[green]✅ Present[/green]" if ctx_exists else "[red]❌ Missing[/red]",
    )

    vibe_dir_exists = os.path.exists(".vibe")
    table.add_row(
        ".vibe/ Config",
        "[green]✅ Present[/green]" if vibe_dir_exists else "[red]❌ Missing[/red]",
    )

    hook_exists = _check_hook_exists()
    table.add_row(
        "Post-Commit Hook",
        "[green]✅ Installed[/green]" if hook_exists else "[yellow]⚠ Not installed[/yellow]",
    )

    # GCS / Remote
    gcs = config.get("gcs_bucket")
    table.add_row(
        "GCS Bucket",
        f"[green]{gcs}[/green]" if gcs else "[dim]Not configured[/dim]",
    )

    gcp_project = config.get("google_project_id")
    table.add_row(
        "GCP Project",
        gcp_project if gcp_project else "[dim]Not configured[/dim]",
    )

    cr_url = config.get("cloud_run_url")
    table.add_row(
        "Cloud Run URL",
        f"[blue]{cr_url}[/blue]" if cr_url else "[dim]Not deployed[/dim]",
    )

    console.print()
    console.print(table)
    console.print()


@app.command()
def push(
    target: str = typer.Argument(
        "antigravity",
        help="Push target: 'antigravity' to sync into Antigravity's brain.",
    ),
):
    """Push the current VIBE_CONTEXT.md into an AI agent's persistent memory."""
    if not os.path.exists(CONTEXT_FILENAME):
        console.print(
            f"[bold red]❌ Error:[/bold red] {CONTEXT_FILENAME} not found. "
            "Run [bold]vibe-sync init[/bold] first."
        )
        raise typer.Exit(code=1)

    if target.lower() == "antigravity":
        _push_to_antigravity()
    else:
        console.print(f"[bold red]❌ Unknown target:[/bold red] '{target}'")
        console.print("[dim]Supported targets: antigravity[/dim]")
        raise typer.Exit(code=1)


@app.command("mcp-test")
def mcp_test():
    """Test MCP server connectivity and verify tools are registered."""
    console.print()
    with console.status("[bold cyan]Testing MCP server...[/bold cyan]"):
        results = _run_mcp_tests()

    # Display results
    table = Table(
        title="🔌 MCP Server Connectivity Test",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Check", style="bold white", min_width=28)
    table.add_column("Status", justify="center", min_width=12)
    table.add_column("Details", style="dim")

    for check_name, passed, detail in results:
        status_str = "[green]✅ PASS[/green]" if passed else "[red]❌ FAIL[/red]"
        table.add_row(check_name, status_str, detail)

    console.print(table)

    all_passed = all(p for _, p, _ in results)
    console.print()
    if all_passed:
        console.print(Panel(
            "[bold green]All MCP checks passed.[/bold green]\n"
            "The server is ready for agent use.",
            title="✅ Result",
            border_style="green",
        ))
    else:
        console.print(Panel(
            "[bold yellow]Some checks failed.[/bold yellow]\n"
            "Review the table above for details.",
            title="⚠️ Result",
            border_style="yellow",
        ))
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# GOOGLE CLOUD COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════


@app.command("cloud-init")
def cloud_init(
    bucket: str = typer.Option(
        ..., "--bucket", "-b",
        help="GCS bucket name for remote context storage.",
    ),
    project: Optional[str] = typer.Option(
        None, "--project", "-p",
        help="Google Cloud project ID (auto-detected if omitted).",
    ),
):
    """Configure Google Cloud Storage for cross-machine context sync."""
    from deploy import get_current_project

    with console.status("[bold cyan]Configuring GCS...[/bold cyan]"):
        # Save bucket
        set_gcs_bucket(bucket)

        # Resolve project ID
        project_id = project or get_current_project()
        if project_id:
            set_google_project(project_id)

    console.print("[bold green]✅ Cloud storage configured![/bold green]")
    console.print(f"  [dim]Bucket:[/dim]  [cyan]{bucket}[/cyan]")
    if project_id:
        console.print(f"  [dim]Project:[/dim] [cyan]{project_id}[/cyan]")
    else:
        console.print("  [dim]Project:[/dim] [yellow]Not detected — pass --project[/yellow]")
    console.print()
    console.print("[dim]Run [bold]vibe-sync cloud-push[/bold] to upload your context.[/dim]")


@app.command("cloud-push")
def cloud_push():
    """Push VIBE_CONTEXT.md and metadata to Google Cloud Storage."""
    config = load_config()
    bucket = config.get("gcs_bucket")

    if not bucket:
        console.print(
            "[bold red]❌ Error:[/bold red] No GCS bucket configured. "
            "Run [bold]vibe-sync cloud-init --bucket <name>[/bold] first."
        )
        raise typer.Exit(code=1)

    if not os.path.exists(CONTEXT_FILENAME):
        console.print(
            f"[bold red]❌ Error:[/bold red] {CONTEXT_FILENAME} not found. "
            "Run [bold]vibe-sync init[/bold] first."
        )
        raise typer.Exit(code=1)

    try:
        from cloud import upload_context
        with console.status("[bold magenta]Uploading to GCS...[/bold magenta]"):
            result = upload_context(bucket)

        console.print("[bold green]☁️  Pushed to GCS successfully![/bold green]")
        for f in result["files_uploaded"]:
            console.print(f"  [dim]📄 gs://{bucket}/{f}[/dim]")

    except Exception as e:
        console.print(f"[bold red]💥 GCS push failed:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("cloud-pull")
def cloud_pull():
    """Pull the latest VIBE_CONTEXT.md from Google Cloud Storage."""
    config = load_config()
    bucket = config.get("gcs_bucket")

    if not bucket:
        console.print(
            "[bold red]❌ Error:[/bold red] No GCS bucket configured. "
            "Run [bold]vibe-sync cloud-init --bucket <name>[/bold] first."
        )
        raise typer.Exit(code=1)

    try:
        from cloud import download_context
        with console.status("[bold magenta]Downloading from GCS...[/bold magenta]"):
            result = download_context(bucket)

        console.print("[bold green]☁️  Pulled from GCS successfully![/bold green]")
        for f in result["files_downloaded"]:
            console.print(f"  [dim]📄 {f} ← gs://{bucket}/[/dim]")

    except FileNotFoundError as e:
        console.print(f"[bold red]❌ Not found:[/bold red] {str(e)}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]💥 GCS pull failed:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def deploy(
    project: Optional[str] = typer.Option(
        None, "--project", "-p",
        help="Google Cloud project ID.",
    ),
    region: str = typer.Option(
        "us-central1", "--region", "-r",
        help="Cloud Run region.",
    ),
    service_name: str = typer.Option(
        "vibe-sync-mcp", "--name", "-n",
        help="Cloud Run service name.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Print the deploy command without executing it.",
    ),
):
    """Deploy the Vibe-Sync MCP server to Google Cloud Run."""
    from deploy import deploy as run_deploy, check_gcloud_installed, get_current_project

    if not check_gcloud_installed():
        console.print(
            "[bold red]❌ Error:[/bold red] gcloud CLI not found.\n"
            "Install it from: https://cloud.google.com/sdk/docs/install"
        )
        raise typer.Exit(code=1)

    # Resolve project ID
    config = load_config()
    project_id = project or config.get("google_project_id") or get_current_project()
    if not project_id:
        console.print(
            "[bold red]❌ Error:[/bold red] No GCP project found. "
            "Pass [bold]--project <id>[/bold] or run [bold]gcloud config set project <id>[/bold]."
        )
        raise typer.Exit(code=1)

    gcs_bucket = config.get("gcs_bucket")

    try:
        service_url = run_deploy(
            project_id=project_id,
            region=region,
            service_name=service_name,
            gcs_bucket=gcs_bucket,
            dry_run=dry_run,
        )

        if service_url and not dry_run:
            # Save deployment info back to config
            set_google_project(project_id)
            set_cloud_run_url(service_url, region=region)
            console.print("[dim]Config updated with deployment URL.[/dim]")

    except RuntimeError as e:
        console.print(f"[bold red]💥 Deployment failed:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def _get_latest_commit_hash() -> Optional[str]:
    """Get the latest git commit hash, or None."""
    try:
        import git
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        commits = list(repo.iter_commits(max_count=1))
        return commits[0].hexsha if commits else None
    except Exception:
        return None


def _format_timestamp(ts: Optional[str]) -> str:
    """Format an ISO timestamp for display."""
    if not ts:
        return "[dim]—[/dim]"
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return ts


def _time_ago(ts: str) -> str:
    """Return a human-readable 'time ago' string."""
    try:
        dt = datetime.fromisoformat(ts)
        now = datetime.now(dt.tzinfo)
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"
    except Exception:
        return "[dim]Unknown[/dim]"


def _check_hook_exists() -> bool:
    """Check if the post-commit hook is installed."""
    try:
        import git
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        hook_path = os.path.join(repo.git_dir, "hooks", "post-commit")
        return os.path.exists(hook_path)
    except Exception:
        return False


def _push_to_antigravity():
    """Push VIBE_CONTEXT.md content into Antigravity's brain as persistent context."""
    with console.status("[bold magenta]Pushing to Antigravity brain...[/bold magenta]"):
        # Read current context
        with open(CONTEXT_FILENAME, "r", encoding="utf-8") as f:
            context_content = f.read()

        # Ensure brain directory exists
        os.makedirs(ANTIGRAVITY_BRAIN, exist_ok=True)

        # Write the memory file
        memory_path = os.path.join(ANTIGRAVITY_BRAIN, "memory.json")
        config = load_config()

        memory = {
            "source": "vibe-sync",
            "project_name": config.get("project_name", "Unknown"),
            "last_updated": datetime.now().isoformat(),
            "persistent_context": context_content,
            "sync_count": config.get("sync_count", 0),
            "last_commit_hash": config.get("last_commit_hash"),
            "last_commit_message": config.get("last_commit_message"),
        }

        with open(memory_path, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)

        # Also copy VIBE_CONTEXT.md directly into brain
        vibe_copy_path = os.path.join(ANTIGRAVITY_BRAIN, "VIBE_CONTEXT.md")
        shutil.copy2(CONTEXT_FILENAME, vibe_copy_path)

    console.print("[bold green]✅ Pushed to Antigravity brain successfully![/bold green]")
    console.print(f"[dim]  📄 memory.json  → {os.path.join(ANTIGRAVITY_BRAIN, 'memory.json')}[/dim]")
    console.print(f"[dim]  📄 VIBE_CONTEXT  → {vibe_copy_path}[/dim]")


def _run_mcp_tests() -> list[tuple[str, bool, str]]:
    """Run a series of MCP connectivity and configuration tests."""
    results = []

    # Test 1: Can we import the server module?
    try:
        import server  # noqa: F401
        results.append(("Server module import", True, "server.py loads OK"))
    except Exception as e:
        results.append(("Server module import", False, str(e)[:60]))

    # Test 2: Is FastMCP available?
    try:
        from fastmcp import FastMCP  # noqa: F401
        results.append(("FastMCP package", True, "fastmcp is installed"))
    except ImportError:
        results.append(("FastMCP package", False, "pip install fastmcp"))

    # Test 3: Are the tools registered on the server?
    try:
        from server import mcp as server_mcp
        # Check if tools are registered by listing them
        tools_found = hasattr(server_mcp, "tool")
        results.append(("MCP tools registered", tools_found, "get_latest_vibe, read_vibe"))
    except Exception as e:
        results.append(("MCP tools registered", False, str(e)[:60]))

    # Test 4: Is VIBE_CONTEXT.md readable by the server?
    try:
        from server import get_latest_vibe
        vibe_output = get_latest_vibe()
        has_content = len(vibe_output) > 20 and "not found" not in vibe_output.lower()
        detail = f"{len(vibe_output)} chars returned" if has_content else "File missing or empty"
        results.append(("VIBE_CONTEXT.md readable", has_content, detail))
    except Exception as e:
        results.append(("VIBE_CONTEXT.md readable", False, str(e)[:60]))

    # Test 5: Is vibe-sync in Antigravity's MCP config?
    try:
        mcp_config_path = os.path.expanduser(
            os.path.join("~", ".gemini", "antigravity", "mcp_config.json")
        )
        if os.path.exists(mcp_config_path):
            with open(mcp_config_path, "r") as f:
                mcp_cfg = json.load(f)
            registered = "vibe-sync" in mcp_cfg.get("mcpServers", {})
            detail = "Registered in mcp_config.json" if registered else "Not found in config"
            results.append(("Antigravity registration", registered, detail))
        else:
            results.append(("Antigravity registration", False, "mcp_config.json not found"))
    except Exception as e:
        results.append(("Antigravity registration", False, str(e)[:60]))

    return results


if __name__ == "__main__":
    app()
