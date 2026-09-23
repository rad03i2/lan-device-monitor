from lan_device_monitor.core import Device, Snapshot

def test_snapshot_roundtrip(tmp_path):
    path = tmp_path / "snapshot.json"
    original = Snapshot("2026-01-01T00:00:00+00:00", [Device("192.168.1.2", "AA:BB:CC:DD:EE:FF").normalized()])
    original.save(path)
    loaded = Snapshot.load(path)
    assert loaded.captured_at == original.captured_at
    assert loaded.devices == original.devices
