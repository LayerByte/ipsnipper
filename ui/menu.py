from __future__ import annotations

from collections.abc import Callable

from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ui.components import console


class Menu:
    def __init__(self, title: str) -> None:
        self.title = title
        self.items: dict[str, tuple[str, Callable[[], None]]] = {}

    def register(self, key: str, label: str, callback: Callable[[], None]) -> None:
        self.items[key] = (label, callback)

    def ask(self) -> str:
        table = Table.grid(padding=(0, 2))
        table.add_column(justify="right", style="bold red")
        table.add_column(style="white")
        for key, (label, _) in self.items.items():
            table.add_row(f"[{key}]", label)
        table.add_row("[0]", "Exit")
        console.print(Panel(table, title=self.title, border_style="cyan"))
        return Prompt.ask("Select option").strip().upper()
