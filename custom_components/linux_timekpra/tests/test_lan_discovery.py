"""Tests for MAC-based LAN discovery."""

from __future__ import annotations

from ipaddress import IPv4Network
from unittest.mock import patch

from .. import lan_discovery


def test_find_device_by_mac_uses_active_lan_scan():
    """Return a matching device found by arp-scan."""
    with (
        patch.object(
            lan_discovery,
            "_get_network_details",
            return_value=("eth0", IPv4Network("192.0.2.0/24")),
        ),
        patch.object(lan_discovery, "_scan_with_arp_scan",
                     return_value={"192.0.2.25": "001122334455"}),
        patch.object(lan_discovery, "_probe_ssh_hosts") as probe,
    ):
        result = lan_discovery.find_device_by_mac("00:11:22:33:44:55")

    assert result == "192.0.2.25"
    probe.assert_not_called()


def test_find_device_by_mac_uses_reachable_ip_not_stale_neighbor():
    """Prefer the responsive address when the ARP cache still has an old IP."""
    with (
        patch.object(
            lan_discovery,
            "_get_network_details",
            return_value=("eth0", IPv4Network("192.0.2.0/24")),
        ),
        patch.object(lan_discovery, "_scan_with_arp_scan", return_value={}),
        patch.object(
            lan_discovery,
            "_probe_ssh_hosts",
            return_value={"192.0.2.25"},
        ),
        patch.object(
            lan_discovery,
            "_read_arp_table",
            return_value={"192.0.2.10": "001122334455"},
        ),
        patch.object(
            lan_discovery,
            "_read_neighbors",
            return_value={"192.0.2.25": "001122334455"},
        ),
    ):
        result = lan_discovery.find_device_by_mac("00:11:22:33:44:55")

    assert result == "192.0.2.25"
