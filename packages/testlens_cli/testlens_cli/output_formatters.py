import json
from typing import Any, List, Dict
import sys

def print_json(data: Any):
    """Outputs raw JSON for machine parsing."""
    print(json.dumps(data, indent=2))

def print_failure_table(failures: List[Dict]):
    # Lazy import for fast CLI startup
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    table = Table(title="Recent Test Failures")
    
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Test Case", style="magenta")
    table.add_column("Status", justify="right", style="green")
    table.add_column("Created At", justify="right")
    
    for f in failures:
        table.add_row(
            str(f.get("id", "")),
            f.get("test_name", ""),
            f.get("status", ""),
            f.get("created_at", "")
        )
        
    console.print(table)

def print_flaky_table(tests: List[Dict]):
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    table = Table(title="Flaky Test Leaderboard")
    
    table.add_column("Test Case", style="magenta")
    table.add_column("Flaky Score", justify="right")
    table.add_column("Flip Count", justify="right", style="cyan")
    
    for t in tests:
        score = t.get("flaky_score", 0.0)
        # Color code the score
        score_str = f"{score:.2f}"
        if score > 0.7:
            score_str = f"[red]{score_str}[/red]"
        elif score > 0.4:
            score_str = f"[yellow]{score_str}[/yellow]"
            
        table.add_row(
            t.get("test_case_name", ""),
            score_str,
            str(t.get("flip_count", 0))
        )
        
    console.print(table)
    
def print_error(msg: str):
    from rich.console import Console
    console = Console()
    console.print(f"[bold red]Error:[/bold red] {msg}")
