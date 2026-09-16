from __future__ import annotations

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from config import VERSION
from ui.components import console

BANNER_LABEL = "GITHUB.COM/LAYERBYTE"

BANNER = r"""
██╗██████╗     ███████╗███╗   ██╗██╗██████╗ ██████╗ ███████╗██████╗
██║██╔══██╗    ██╔════╝████╗  ██║██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║██████╔╝    ███████╗██╔██╗ ██║██║██████╔╝██████╔╝█████╗  ██████╔╝
██║██╔═══╝     ╚════██║██║╚██╗██║██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██║██║         ███████║██║ ╚████║██║██║     ██║     ███████╗██║  ██║
╚═╝╚═╝         ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
"""


def show_banner() -> None:
    width = console.size.width
    rows = []
    if width >= 82:
        rows.append(Align.center(Text(BANNER.strip("\n"), style="bold red")))
    rows.extend([
        Align.center(Text(BANNER_LABEL, style="bold white")),
        Text(""),
        Align.center(Text(f"Version: {VERSION}    Status: Ready", style="green")),
    ])
    console.print(Panel(Group(*rows), border_style="red"))
