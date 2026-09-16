from __future__ import annotations

import os
import platform
import sys


def clear_screen() -> None:
    if not sys.stdout.isatty():
        return
    command = "cls" if platform.system().lower() == "windows" else "clear"
    os.system(command)
