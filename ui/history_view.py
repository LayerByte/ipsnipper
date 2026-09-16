from __future__ import annotations

from rich import box
from rich.table import Table

from storage.database import HistoryEntry
from ui.components import console
from utils.formatting import format_value


def show_history(entries: list[HistoryEntry]) -> None:
    table = Table(box=box.ROUNDED, title="LOOKUP HISTORY")
    table.add_column("ID", justify="right", style="red")
    table.add_column("IP", style="cyan")
    table.add_column("Country")
    table.add_column("City")
    table.add_column("ISP")
    table.add_column("ASN", style="magenta")
    table.add_column("Time", style="dim")
    for entry in entries:
        table.add_row(
            str(entry.id),
            entry.ip,
            format_value(entry.country),
            format_value(entry.city),
            format_value(entry.isp),
            format_value(entry.asn),
            entry.timestamp[11:16] if len(entry.timestamp) >= 16 else entry.timestamp,
        )
    console.print(table)
