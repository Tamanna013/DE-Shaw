import typer
import keyring
import os
import json
from testlens_cli.output_formatters import get_console

app = typer.Typer()

@app.callback(invoke_without_command=True)
def login(token: str = typer.Option(..., prompt=True, hide_input=True, help="Your TestLens API token")):
    """
    Authenticate with the TestLens platform.
    (Mocked: Normally this would do a device-code flow or open a browser).
    """
    console = get_console()
    
    try:
        keyring.set_password("testlens-cli", "auth-token", token)
        console.print("[green]Successfully saved token securely to OS keyring.[/green]")
    except Exception as e:
        console.print("[yellow]WARNING: Failed to access OS keyring (are you in a headless environment?).[/yellow]")
        console.print("[yellow]Falling back to ~/.testlens/config.json storage.[/yellow]")
        
        config_dir = os.path.expanduser("~/.testlens")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config.json")
        
        cfg = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                try:
                    cfg = json.load(f)
                except:
                    pass
                    
        cfg["token"] = token
        
        # Write securely
        with open(config_path, "w") as f:
            json.dump(cfg, f)
        os.chmod(config_path, 0o600)
        
        console.print("[green]Successfully saved token to ~/.testlens/config.json.[/green]")
