import pytest
from lan_device_monitor.core import Device, Snapshot, compare, filter_network, neighbor_command, parse_neighbors

def test_parse_linux_neighbors():
    text = "192.168.1.5 dev eth0 lladdr AA:BB:CC:DD:EE:FF REACHABLE\n192.168.1.9 dev eth0 lladdr 11:22:33:44:55:66 STALE"
    devices = parse_neighbors(text)
    assert [(d.ip, d.mac, d.state) for d in devices] == [
        ("192.168.1.5", "aa:bb:cc:dd:ee:ff", "reachable"),
        ("192.168.1.9", "11:22:33:44:55:66", "stale"),
    ]

def test_parse_windows_arp():
    text = "  192.168.0.10          aa-bb-cc-dd-ee-ff     dynamic"
    assert parse_neighbors(text)[0] == Device("192.168.0.10", "aa:bb:cc:dd:ee:ff", "dynamic")

def test_compare_added_removed_and_ip_change():
    old = Snapshot("old", [Device("10.0.0.2", "aa:aa:aa:aa:aa:aa"), Device("10.0.0.3", "bb:bb:bb:bb:bb:bb")])
    new = Snapshot("new", [Device("10.0.0.8", "aa:aa:aa:aa:aa:aa"), Device("10.0.0.4", "cc:cc:cc:cc:cc:cc")])
    result = compare(old, new)
    assert [d.mac for d in result["added"]] == ["cc:cc:cc:cc:cc:cc"]
    assert [d.mac for d in result["removed"]] == ["bb:bb:bb:bb:bb:bb"]
    assert result["ip_changed"][0].ip == "10.0.0.8"

def test_network_filter():
    devices = [Device("192.168.1.2", "aa:aa:aa:aa:aa:aa"), Device("10.0.0.2", "bb:bb:bb:bb:bb:bb")]
    assert filter_network(devices, "192.168.1.0/24") == devices[:1]

def test_commands():
    assert neighbor_command("Windows") == ["arp", "-a"]
    assert neighbor_command("Linux") == ["ip", "neigh", "show"]
    assert neighbor_command("Darwin") == ["arp", "-an"]
    with pytest.raises(RuntimeError):
        neighbor_command("Plan9")

def test_invalid_device():
    with pytest.raises(ValueError):
        Device("999.1.1.1", "aa:bb:cc:dd:ee:ff")
    with pytest.raises(ValueError):
        Device("127.0.0.1", "not-a-mac")
