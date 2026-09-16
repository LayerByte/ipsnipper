# IPSNIPPER

IPSNIPPER is a polished Python terminal IP intelligence utility for retrieving publicly available network, ASN, RDAP, reverse DNS, ISP, and approximate geolocation information.

School Purpose Only.

## Overview

IPSNIPPER helps students and administrators inspect public IP address information from legitimate public data sources. It validates addresses locally, avoids unnecessary external requests for private or non-public addresses, and presents results in a clean Rich-powered cybersecurity-style interface.

IPSNIPPER is not an exploitation, tracking, DDoS, malware, credential attack, or remote-access tool.

## Features

- Rich terminal UI with panels, tables, columns, prompts, and status spinners
- Public IPv4 and IPv6 lookup
- My Public IP lookup
- Local IP classification before external provider requests
- Reverse DNS lookup
- Public IP intelligence provider integration
- RDAP / registry summaries
- Lookup duration timing
- SQLite lookup history
- JSON, TXT, and CSV exports
- Local settings file
- Optional short-term cache
- Direct CLI mode
- Machine-readable JSON mode
- Debug mode for tracebacks

## Information Available

- IP address and version
- Public/private/global/reserved/loopback/link-local/multicast classification
- Hostname / reverse DNS
- ISP and organization
- ASN and ASN organization
- Network / CIDR
- Country and country code
- Region
- City
- Postal code
- Timezone
- Approximate coordinates when supplied by the provider
- RDAP network name, handle, range, registry, registration, and update timestamps
- Data source and lookup duration

## Installation

```bash
git clone https://github.com/LayerByte/ipsnipper.git
cd ipsnipper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

## Interactive Mode

```bash
python main.py
```

## Direct CLI Mode

```bash
python main.py --lookup 8.8.8.8
python main.py --lookup 8.8.8.8 --json
python main.py --lookup 8.8.8.8 --save
python main.py --lookup 2001:4860:4860::8888
python main.py --debug
```

When `--json` is supplied, IPSNIPPER outputs machine-readable JSON without banners or Rich formatting.

## Lookup History

Lookup history is stored locally in:

```text
data/ipsnipper.db
```

Stored fields include IP, timestamp, country, city, ISP, organization, ASN, hostname, and lookup status. IPSNIPPER does not store raw provider responses.

## Export

Results can be exported as:

- JSON
- TXT
- CSV

Files are written under:

```text
results/
```

## Configuration

Settings are stored locally in:

```text
config/settings.json
```

Configurable options:

- Reverse DNS
- RDAP
- Save history
- Auto export
- Default export format
- Request timeout
- Show coordinates
- Cache TTL

If the settings file is corrupted, IPSNIPPER safely falls back to defaults.

## Data Sources

- IP intelligence: `ipwho.is`
- RDAP: `rdap.org` and regional registry RDAP data
- Reverse DNS: system DNS resolver
- My Public IP: `api.ipify.org`

All external requests use HTTPS and request timeouts.

## Privacy

IPSNIPPER does not collect analytics, upload lookup history, or silently store raw API responses.

Private, loopback, link-local, multicast, unspecified, invalid, and other non-public addresses are not sent to external geolocation providers unnecessarily.

## Geolocation Accuracy

IP-based geolocation is approximate and cannot reliably identify the exact physical location or home address of a person.

It may represent an ISP, VPN, proxy, hosting provider, cellular gateway, or network infrastructure rather than a specific device or person.

## Limitations

- Provider data can be incomplete, outdated, or rate-limited.
- Reverse DNS is often unavailable.
- RDAP fields vary by registry.
- Cache data may be reused only within the configured TTL.
- IPSNIPPER is an educational network intelligence tool, not a complete investigation platform.

## Disclaimer

Use IPSNIPPER only for school assignments, defensive learning, networking education, authorized troubleshooting, and legitimate public network-registration research.

Do not use IPSNIPPER for harassment, stalking, exploitation, unauthorized access, credential attacks, malware, phishing, DDoS activity, or attempts to identify a person's exact physical address.

## License

Released under the MIT License.
