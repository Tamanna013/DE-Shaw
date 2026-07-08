import typer
import os
import json
from testlens_cli.output_formatters import get_console

app = typer.Typer()

def _get_config_path() -> str:
    config_dir = os.path.expanduser("~/.testlens")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")

def _get_default_repo() -> str:
    path = _get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f).get("default_repo")
        except:
            pass
    return None

@app.command("set-repo")
def set_repo(repo_id: str):
    """Set the default repository ID for future CLI commands."""
    path = _get_config_path()
    cfg = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                cfg = json.load(f)
            except:
                pass
                
    cfg["default_repo"] = repo_id
    
    with open(path, "w") as f:
        json.dump(cfg, f)
        
    console = get_console()
    console.print(f"[green]Default repository set to [bold]{repo_id}[/bold][/green]")

@app.command("show")
def show():
    """Show current CLI configuration."""
    console = get_console()
    path = _get_config_path()
    
    if not os.path.exists(path):
        console.print("No configuration found.")
        return
        
    try:
        with open(path, "r") as f:
            cfg = json.load(f)
            
        # Don't print the raw token
        if "token" in cfg:
            cfg["token"] = "**********"
            
        from rich.table import Table
        table = Table(title="TestLens CLI Config", show_header=False)
        for k, v in cfg.items():
            table.add_row(k, str(v))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error reading config: {e}[/red]")
