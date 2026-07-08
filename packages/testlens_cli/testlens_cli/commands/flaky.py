import typer
import sys
from typing import Optional
from testlens_cli.api_client import TestLensClient, TestLensAPIError, AuthRequiredError
from testlens_cli.output_formatters import print_json, print_flaky_table, print_error
from testlens_cli.commands.config import _get_default_repo
from testlens_cli.commands.failures import _handle_error

app = typer.Typer()

@app.command("list")
def list_flaky(
    ctx: typer.Context,
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository ID")
):
    """View the flaky test leaderboard."""
    try:
        repo_to_use = repo or _get_default_repo()
        if not repo_to_use:
            print_error("No repository specified. Use --repo or run `testlens config set-repo <repo_id>`")
            sys.exit(1)
            
        client = TestLensClient()
        data = client.get_flaky_leaderboard(repo_to_use)
        
        is_json = "--json" in sys.argv
        
        if is_json:
            print_json(data)
        else:
            print_flaky_table(data)
            
    except Exception as e:
        _handle_error(e)
