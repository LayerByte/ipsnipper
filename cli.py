from __future__ import annotations

import argparse
import ctypes
import json
import platform
import sys
import traceback

from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from config import APP_NAME, AUTHOR, LICENSE, REPOSITORY, VERSION
from models import IPLookupResult
from providers.base import ProviderError
from providers.public_ip_provider import PublicIPProvider
from services.exporter import Exporter
from services.ip_lookup import IPLookupService
from storage.database import HistoryDatabase
from storage.settings import Settings
from ui.banner import show_banner
from ui.components import console, error_panel, success, warning_panel
from ui.history_view import show_history
from ui.lookup_view import show_lookup_result, show_rdap_details, show_technical_details
from ui.menu import Menu
from utils.network import clear_screen
from utils.validators import InvalidIPAddress


class IPSniperApp:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.settings = Settings.load()
        self.lookup_service = IPLookupService(self.settings)
        self.history = HistoryDatabase()
        self.exporter = Exporter()
        self.last_result: IPLookupResult | None = None

    def run(self) -> int:
        try:
            while True:
                clear_screen()
                show_banner()
                menu = Menu("MAIN MENU")
                menu.register("1", "IP Lookup", self.menu_lookup)
                menu.register("2", "My Public IP", self.menu_my_public_ip)
                menu.register("3", "Lookup History", self.menu_history)
                menu.register("4", "Export Results", self.menu_export_results)
                menu.register("5", "Settings", self.menu_settings)
                menu.register("6", "About", self.menu_about)
                choice = menu.ask()
                if choice in {"0", "Q"}:
                    success("Goodbye.")
                    return 0
                item = menu.items.get(choice)
                if not item:
                    warning_panel("Unknown option.")
                    self.pause()
                    continue
                item[1]()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled.[/yellow]")
            return 130

    def menu_lookup(self) -> None:
        clear_screen()
        ip = Prompt.ask("[bold cyan]Enter IPv4 / IPv6 address[/bold cyan]").strip()
        result = self.perform_lookup(ip)
        if result:
            self.result_actions(result)

    def perform_lookup(self, ip: str, force_refresh: bool = False) -> IPLookupResult | None:
        try:
            with console.status("[cyan]Validating IP address...[/cyan]", spinner="dots"):
                result = self.lookup_service.lookup(ip, force_refresh=force_refresh)
            success(f"Lookup completed in {result.metadata.duration_seconds:.2f}s")
            show_lookup_result(result)
            self.last_result = result
            if self.settings.save_history:
                self.history.add(result, "success" if not result.metadata.warnings else "warning")
            if self.settings.auto_export:
                path = self.exporter.export(result, self.settings.default_export)
                success(f"Auto-exported: {path}")
            return result
        except InvalidIPAddress as exc:
            error_panel(str(exc), "Enter a valid IPv4 or IPv6 value.")
        except Exception as exc:
            self.handle_exception(exc)
        return None

    def result_actions(self, result: IPLookupResult) -> None:
        while True:
            console.print(Panel(
                "[1] View Technical Details\n"
                "[2] View RDAP Details\n"
                "[3] Export JSON\n"
                "[4] Export TXT\n"
                "[5] Export CSV\n"
                "[6] Repeat Lookup\n\n"
                "[B] Back to Menu",
                title="ACTIONS",
                border_style="cyan",
            ))
            choice = Prompt.ask("Select action", default="B").strip().upper()
            if choice == "1":
                show_technical_details(result)
            elif choice == "2":
                show_rdap_details(result)
            elif choice == "3":
                success(f"Exported: {self.exporter.export(result, 'json')}")
            elif choice == "4":
                success(f"Exported: {self.exporter.export(result, 'txt')}")
            elif choice == "5":
                success(f"Exported: {self.exporter.export(result, 'csv')}")
            elif choice == "6":
                refreshed = self.perform_lookup(result.ip, force_refresh=True)
                if refreshed:
                    result = refreshed
            elif choice in {"B", "Q"}:
                return
            else:
                warning_panel("Unknown action.")

    def menu_my_public_ip(self) -> None:
        clear_screen()
        provider = PublicIPProvider(self.settings.request_timeout)
        try:
            with console.status("[cyan]Retrieving current public IP...[/cyan]", spinner="dots"):
                ip = provider.lookup()
            success(f"My public IP: {ip}")
            if Confirm.ask("Run full lookup for this IP?", default=True):
                result = self.perform_lookup(ip)
                if result:
                    self.result_actions(result)
        except ProviderError as exc:
            error_panel(str(exc))
            self.pause()

    def menu_history(self) -> None:
        while True:
            clear_screen()
            entries = self.history.list()
            show_history(entries)
            console.print("[V] View result  [R] Repeat lookup  [D] Delete entry  [C] Clear history  [B] Back")
            choice = Prompt.ask("Select option", default="B").strip().upper()
            if choice == "B":
                return
            if choice == "C":
                if Confirm.ask("Clear all lookup history?", default=False):
                    self.history.clear()
                continue
            entry_id = IntPrompt.ask("History ID", default=0)
            entry = self.history.get(entry_id)
            if not entry:
                warning_panel("History entry not found.")
                self.pause()
                continue
            if choice == "R":
                result = self.perform_lookup(entry.ip, force_refresh=True)
                if result:
                    self.result_actions(result)
            elif choice == "V":
                console.print(Panel(
                    f"IP: {entry.ip}\nCountry: {entry.country or 'N/A'}\nCity: {entry.city or 'N/A'}\n"
                    f"ISP: {entry.isp or 'N/A'}\nASN: {entry.asn or 'N/A'}\nTime: {entry.timestamp}",
                    title=f"HISTORY #{entry.id}",
                    border_style="cyan",
                ))
                self.pause()
            elif choice == "D":
                if Confirm.ask(f"Delete history entry #{entry.id}?", default=False):
                    self.history.delete(entry.id)

    def menu_export_results(self) -> None:
        if not self.last_result:
            warning_panel("No lookup result is available yet.")
            self.pause()
            return
        kind = Prompt.ask("Export format", choices=["json", "txt", "csv"], default=self.settings.default_export)
        success(f"Exported: {self.exporter.export(self.last_result, kind)}")
        self.pause()

    def menu_settings(self) -> None:
        while True:
            clear_screen()
            console.print(Panel(
                f"[1] Reverse DNS       {'ON' if self.settings.reverse_dns else 'OFF'}\n"
                f"[2] RDAP              {'ON' if self.settings.rdap else 'OFF'}\n"
                f"[3] Save History      {'ON' if self.settings.save_history else 'OFF'}\n"
                f"[4] Auto Export       {'ON' if self.settings.auto_export else 'OFF'}\n"
                f"[5] Default Export    {self.settings.default_export.upper()}\n"
                f"[6] Request Timeout   {self.settings.request_timeout}s\n"
                f"[7] Show Coordinates  {'ON' if self.settings.show_coordinates else 'OFF'}\n\n"
                "[B] Back",
                title="SETTINGS",
                border_style="cyan",
            ))
            choice = Prompt.ask("Select setting", default="B").strip().upper()
            if choice == "B":
                self.settings.save()
                self.lookup_service = IPLookupService(self.settings)
                return
            if choice == "1":
                self.settings.reverse_dns = not self.settings.reverse_dns
            elif choice == "2":
                self.settings.rdap = not self.settings.rdap
            elif choice == "3":
                self.settings.save_history = not self.settings.save_history
            elif choice == "4":
                self.settings.auto_export = not self.settings.auto_export
            elif choice == "5":
                self.settings.default_export = Prompt.ask("Default export", choices=["json", "txt", "csv"], default=self.settings.default_export)
            elif choice == "6":
                self.settings.request_timeout = float(IntPrompt.ask("Timeout seconds", default=int(self.settings.request_timeout)))
            elif choice == "7":
                self.settings.show_coordinates = not self.settings.show_coordinates
            self.settings.save()

    def menu_about(self) -> None:
        clear_screen()
        console.print(Panel(
            f"{APP_NAME}\n\n"
            f"Version: {VERSION}\n"
            f"Python: {sys.version.split()[0]}\n"
            f"Platform: {platform.platform()}\n"
            f"Repository: {REPOSITORY}\n"
            f"Author: {AUTHOR}\n"
            f"License: {LICENSE}\n\n"
            "A lightweight Python IP intelligence utility for retrieving publicly available "
            "network, ASN, RDAP, reverse DNS and approximate geolocation information.\n\n"
            "School Purpose Only.",
            title="ABOUT",
            border_style="red",
        ))
        self.pause()

    def pause(self) -> None:
        Prompt.ask("Press Enter to continue", default="")

    def handle_exception(self, exc: Exception) -> None:
        if self.debug:
            console.print_exception()
        else:
            error_panel(str(exc) or exc.__class__.__name__)


def set_terminal_title(title: str) -> None:
    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            pass
    if sys.stdout.isatty():
        sys.stdout.write(f"\033]0;{title}\a")
        sys.stdout.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=APP_NAME)
    parser.add_argument("--lookup", help="Lookup a public IPv4 or IPv6 address.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON only.")
    parser.add_argument("--save", action="store_true", help="Save lookup output locally.")
    parser.add_argument("--debug", action="store_true", help="Show tracebacks for diagnostics.")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.json:
        set_terminal_title(APP_NAME)
    app = IPSniperApp(debug=args.debug)

    if args.lookup:
        try:
            result = app.lookup_service.lookup(args.lookup)
            if app.settings.save_history:
                app.history.add(result, "success" if not result.metadata.warnings else "warning")
            saved_path = None
            if args.save:
                saved_path = app.exporter.export(result, app.settings.default_export)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                success(f"Lookup completed in {result.metadata.duration_seconds:.2f}s")
                show_lookup_result(result)
                if saved_path:
                    success(f"Exported: {saved_path}")
            return 0
        except Exception as exc:
            if args.debug:
                traceback.print_exc()
            else:
                if args.json:
                    print(json.dumps({"error": str(exc)}))
                else:
                    error_panel(str(exc))
            return 2

    return app.run()
