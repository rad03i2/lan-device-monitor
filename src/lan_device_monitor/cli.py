from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from .core import Snapshot, compare, filter_network, scan

VERSION = "1.0.0"

def _print_devices(devices):
    if not devices:
        print("No devices found.")
        return
    print(f"{'IP':<16} {'MAC':<18} STATE")
    for d in devices:
        print(f"{d.ip:<16} {d.mac:<18} {d.state}")

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="lan-monitor", description="Inspect local OS neighbor tables and detect LAN device changes.")
    parser.add_argument("--version", action="version", version=f"lan-device-monitor {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = parser.add_subparsers(dest="command", required=True)
    pscan = sub.add_parser("scan", help="Capture the current neighbor table")
    pscan.add_argument("--network", help="Optional CIDR filter, e.g. 192.168.1.0/24")
    pscan.add_argument("--save", help="Write snapshot JSON")
    pscan.add_argument("--json", action="store_true", help="Print JSON")
    pscan.add_argument("--timeout", type=float, default=5.0)
    pdiff = sub.add_parser("diff", help="Compare a saved snapshot with a new scan")
    pdiff.add_argument("snapshot")
    pdiff.add_argument("--network")
    pdiff.add_argument("--json", action="store_true")
    pdiff.add_argument("--fail-on-change", action="store_true")
    try:
        args = parser.parse_args(argv)
        if args.command == "scan":
            snap = scan(args.timeout)
            snap.devices = filter_network(snap.devices, args.network)
            if args.save:
                snap.save(args.save)
            if args.json:
                print(json.dumps(snap.to_dict(), indent=2, ensure_ascii=False))
            else:
                _print_devices(snap.devices)
            return 0
        old = Snapshot.load(args.snapshot)
        current = scan()
        current.devices = filter_network(current.devices, args.network)
        result = compare(old, current)
        if args.json:
            print(json.dumps({k: [asdict(d) for d in v] for k, v in result.items()}, indent=2, ensure_ascii=False))
        else:
            for label, devices in result.items():
                print(f"\n{label.replace('_', ' ').title()} ({len(devices)})")
                _print_devices(devices)
        changed = any(result.values())
        return 1 if changed and args.fail_on_change else 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
