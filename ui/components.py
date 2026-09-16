from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils.formatting import format_value

console = Console(safe_box=True)


def kv_table(rows: list[tuple[str, object]], value_style: str = "white") -> Table:
    table = Table(box=box.ROUNDED, show_header=False, expand=True)
    table.add_column("Field", style="bold cyan", no_wrap=True, width=18)
    table.add_column("Value", style=value_style, overflow="fold")
    for key, value in rows:
        table.add_row(key, format_value(value))
    return table


def error_panel(message: str, help_text: str | None = None) -> None:
    body = message if not help_text else f"{message}\n\n{help_text}"
    console.print(Panel(body, title="ERROR", border_style="red"))


def warning_panel(message: str) -> None:
    console.print(Panel(message, title="WARNING", border_style="yellow"))


def success(message: str) -> None:
    console.print(f"[bold green][OK][/bold green] {message}")
