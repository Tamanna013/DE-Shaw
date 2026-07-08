import typer
import sys
from typing import Optional
from testlens_cli.commands import login, failures, flaky, config

# Lazy imports for performance
_rich_console = None

def get_console():
    global _rich_console
    if _rich_console is None:
        from rich.console import Console
        _rich_console = Console()
    return _rich_console

app = typer.Typer(
    name="testlens",
    help="TestLens CLI - The AI-powered CI failure analysis platform.",
    no_args_is_help=True
)

app.add_typer(login.app, name="login", help="Authenticate with TestLens (OAuth device code flow)")
app.add_typer(failures.app, name="failures", help="View and analyze recent test failures")
app.add_typer(flaky.app, name="flaky", help="View the flaky test leaderboard")
app.add_typer(config.app, name="config", help="Manage local repository configuration")

@app.callback()
def main(
    json: bool = typer.Option(False, "--json", help="Output raw JSON for machine parsing"),
):
    """
    TestLens CLI Global Options
    """
    # Store global state in Typer context if needed, though for CLI it's often 
    # easier to pass the `json` flag directly into the commands via a context object.
    pass

def cli():
    try:
        app()
    except Exception as e:
        # Prevent raw tracebacks for unhandled errors unless in debug mode
        console = get_console()
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
