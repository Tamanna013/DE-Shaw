import typer
import sys
from typing import Optional
from testlens_cli.api_client import TestLensClient, TestLensAPIError, AuthRequiredError
from testlens_cli.output_formatters import print_json, print_failure_table, print_error
from testlens_cli.commands.config import _get_default_repo

app = typer.Typer()

def _handle_error(e: Exception):
    if isinstance(e, AuthRequiredError):
        print_error(str(e))
        sys.exit(2) # Auth exit code
    elif isinstance(e, TestLensAPIError):
        print_error(str(e))
        sys.exit(1)
    else:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

@app.command("list")
def list_failures(
    ctx: typer.Context,
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository ID"),
    limit: int = typer.Option(20, help="Number of results to fetch"),
    page: int = typer.Option(1, help="Page number")
):
    """View recent test failures."""
    try:
        repo_to_use = repo or _get_default_repo()
        if not repo_to_use:
            print_error("No repository specified. Use --repo or run `testlens config set-repo <repo_id>`")
            sys.exit(1)
            
        client = TestLensClient()
        data = client.get_failures(repo_to_use, limit=limit, page=page)
        
        # `ctx.parent.params` holds the global options if passed that way, 
        # or we check `sys.argv` for a simpler mock.
        is_json = "--json" in sys.argv
        
        if is_json:
            print_json(data)
        else:
            print_failure_table(data.get("items", []))
            
    except Exception as e:
        _handle_error(e)

@app.command("analyze")
def analyze(
    ctx: typer.Context,
    failure_id: str = typer.Argument(..., help="The ID of the failure to analyze")
):
    """Trigger the AI Reasoning Engine to re-analyze a failure."""
    try:
        client = TestLensClient()
        data = client.analyze_failure(failure_id)
        
        is_json = "--json" in sys.argv
        if is_json:
            print_json(data)
        else:
            from testlens_cli.output_formatters import get_console
            console = get_console()
            console.print(f"[green]Analysis requested for failure {failure_id}. Status: {data.get('status', 'pending')}[/green]")
            
    except Exception as e:
        _handle_error(e)
