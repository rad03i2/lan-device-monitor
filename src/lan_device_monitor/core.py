from __future__ import annotations

import ipaddress
import json
import platform
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

MAC_RE = re.compile(r"(?i)\b([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

@dataclass(frozen=True)
class Device:
    ip: str
    mac: str
    state: str = "unknown"

    def __post_init__(self):
        ipaddress.ip_address(self.ip)
        if not MAC_RE.fullmatch(self.mac):
            raise ValueError(f"Invalid MAC address: {self.mac}")

    def normalized(self) -> "Device":
        return Device(self.ip, self.mac.replace("-", ":").lower(), self.state.lower())

@dataclass
class Snapshot:
    captured_at: str
    devices: list[Device]

    def to_dict(self) -> dict:
        return {"captured_at": self.captured_at, "devices": [asdict(d) for d in self.devices]}

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Snapshot":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(str(data["captured_at"]), [Device(**item).normalized() for item in data["devices"]])

def parse_neighbors(text: str) -> list[Device]:
    found: dict[tuple[str, str], Device] = {}
    for line in text.splitlines():
        ips = IP_RE.findall(line)
        macs = MAC_RE.findall(line)
        if not ips or not macs:
            continue
        ip, mac = ips[0], macs[0].replace("-", ":").lower()
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            continue
        low = line.lower()
        state = next((s for s in ("reachable", "stale", "delay", "probe", "permanent", "dynamic", "static") if s in low), "unknown")
        device = Device(ip, mac, state).normalized()
        found[(device.ip, device.mac)] = device
    return sorted(found.values(), key=lambda d: tuple(int(x) for x in d.ip.split(".")))

def neighbor_command(system: str | None = None) -> list[str]:
    system = (system or platform.system()).lower()
    if system == "windows":
        return ["arp", "-a"]
    if system == "linux":
        return ["ip", "neigh", "show"]
    if system == "darwin":
        return ["arp", "-an"]
    raise RuntimeError(f"Unsupported operating system: {system}")

def scan(timeout: float = 5.0) -> Snapshot:
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    cmd = neighbor_command()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required command not found: {cmd[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Neighbor discovery command timed out") from exc
    if result.returncode != 0:
        message = result.stderr.strip() or f"exit code {result.returncode}"
        raise RuntimeError(f"Neighbor discovery failed: {message}")
    return Snapshot(datetime.now(timezone.utc).isoformat(), parse_neighbors(result.stdout))

def compare(old: Snapshot, new: Snapshot) -> dict[str, list[Device]]:
    old_by_mac = {d.mac: d for d in old.devices}
    new_by_mac = {d.mac: d for d in new.devices}
    added = [new_by_mac[m] for m in sorted(new_by_mac.keys() - old_by_mac.keys())]
    removed = [old_by_mac[m] for m in sorted(old_by_mac.keys() - new_by_mac.keys())]
    changed = [new_by_mac[m] for m in sorted(old_by_mac.keys() & new_by_mac.keys()) if old_by_mac[m].ip != new_by_mac[m].ip]
    return {"added": added, "removed": removed, "ip_changed": changed}

def filter_network(devices: Iterable[Device], cidr: str | None) -> list[Device]:
    if not cidr:
        return list(devices)
    network = ipaddress.ip_network(cidr, strict=False)
    return [d for d in devices if ipaddress.ip_address(d.ip) in network]
