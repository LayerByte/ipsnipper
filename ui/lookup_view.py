from __future__ import annotations

from io import StringIO

from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models import IPLookupResult
from ui.components import console, kv_table
from utils.formatting import format_value

LOCATION_NOTICE = (
    "IP geolocation is approximate. It may represent an ISP, VPN, proxy, hosting "
    "provider, cellular gateway, or network infrastructure rather than the physical "
    "location of a person or device."
)


def show_lookup_result(result: IPLookupResult) -> None:
    heading = Text("IP LOOKUP RESULT", style="bold red")
    heading.append(f"\n{result.ip}", style="bold white")
    console.print(Panel(heading, border_style="red"))

    overview = kv_table(
        [
            ("IP Address", result.ip),
            ("Version", f"IPv{result.version}"),
            ("Scope", result.scope),
            ("Hostname", result.network.hostname),
        ]
    )
    network = kv_table(
        [
            ("ISP", result.network.isp),
            ("Organization", result.network.organization),
            ("ASN", result.network.asn),
            ("Network", result.network.cidr),
        ],
        value_style="magenta",
    )
    location_rows = [
        ("Country", result.location.country),
        ("Country Code", result.location.country_code),
        ("Region", result.location.region),
        ("City", result.location.city),
        ("Postal Code", result.location.postal),
        ("Timezone", result.location.timezone),
    ]
    if result.location.latitude is not None or result.location.longitude is not None:
        location_rows.append(("Coordinates", f"{format_value(result.location.latitude)}, {format_value(result.location.longitude)}"))
    location = kv_table(location_rows)
    rdap = kv_table(
        [
            ("Network Name", result.rdap.network_name),
            ("Registry", result.network.registry or result.rdap.registry),
            ("Handle", result.rdap.handle),
            ("Start Address", result.rdap.start_address),
            ("End Address", result.rdap.end_address),
            ("Last Updated", result.rdap.last_updated),
        ],
        value_style="magenta",
    )

    console.print(Columns([
        Panel(overview, title="OVERVIEW", border_style="cyan"),
        Panel(network, title="NETWORK", border_style="cyan"),
    ], equal=True, expand=True))
    console.print(Columns([
        Panel(location, title="APPROXIMATE IP LOCATION", border_style="cyan"),
        Panel(rdap, title="RDAP / REGISTRY", border_style="magenta"),
    ], equal=True, expand=True))
    console.print(Panel(LOCATION_NOTICE, title="GEOLOCATION ACCURACY", border_style="yellow"))
    if result.metadata.warnings:
        console.print(Panel("\n".join(f"- {w}" for w in result.metadata.warnings), title="WARNINGS", border_style="yellow"))


def show_technical_details(result: IPLookupResult) -> None:
    classification = kv_table(
        [
            ("IPv4", result.version == 4),
            ("IPv6", result.version == 6),
            ("Public", result.classification.public_lookup_allowed),
            ("Private", result.classification.private),
            ("Global", result.classification.global_address),
            ("Reserved", result.classification.reserved),
            ("Loopback", result.classification.loopback),
            ("Link Local", result.classification.link_local),
            ("Multicast", result.classification.multicast),
            ("Unspecified", result.classification.unspecified),
        ]
    )
    sources = kv_table(
        [
            ("IP Intelligence", result.metadata.source),
            ("RDAP", result.metadata.rdap_source),
            ("Reverse DNS", result.metadata.reverse_dns_source),
            ("Cache", "Source: Cache" if result.metadata.cache_hit else "Fresh lookup"),
            ("Duration", f"{result.metadata.duration_seconds:.2f}s"),
        ]
    )
    console.print(Columns([
        Panel(classification, title="IP CLASSIFICATION", border_style="cyan"),
        Panel(sources, title="DATA SOURCES", border_style="magenta"),
    ], equal=True, expand=True))


def show_rdap_details(result: IPLookupResult) -> None:
    console.print(Panel(kv_table(list(result.rdap.to_dict().items())), title="RDAP DETAILS", border_style="magenta"))


def result_to_text(result: IPLookupResult) -> str:
    capture = Console(file=StringIO(), width=100, record=True, safe_box=True)
    table = Table(box=box.SIMPLE)
    table.add_column("Field")
    table.add_column("Value")
    for key, value in flatten_for_text(result):
        table.add_row(key, format_value(value))
    capture.print(table)
    return capture.export_text()


def flatten_for_text(result: IPLookupResult) -> list[tuple[str, object]]:
    rows: list[tuple[str, object]] = [
        ("IP", result.ip),
        ("Version", f"IPv{result.version}"),
        ("Scope", result.scope),
        ("Hostname", result.network.hostname),
        ("Country", result.location.country),
        ("Region", result.location.region),
        ("City", result.location.city),
        ("Postal Code", result.location.postal),
        ("ISP", result.network.isp),
        ("Organization", result.network.organization),
        ("ASN", result.network.asn),
        ("Network", result.network.cidr),
        ("Registry", result.network.registry),
        ("RDAP Network", result.rdap.network_name),
        ("Duration", f"{result.metadata.duration_seconds:.2f}s"),
    ]
    return rows
