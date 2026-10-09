"""Discover a Linux host on the local network by its MAC address."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import logging
import re
import socket
import subprocess

from .const import normalize_mac_address

_LOGGER = logging.getLogger(__name__)
_MAC_PATTERN = re.compile(r"(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}")


def _read_neighbors(interface: str) -> dict[str, str]:
    """Read IP-to-MAC mappings from the Linux neighbor table."""
    devices: dict[str, str] = {}
    try:
        result = subprocess.run(
            ["ip", "neigh", "show", "dev", interface],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as err:
        _LOGGER.warning("Could not read network neighbors: %s", err)
        return devices

    for line in result.stdout.splitlines():
        fields = line.split()
        if "lladdr" not in fields or {"FAILED", "INCOMPLETE"}.intersection(fields):
            continue
        mac_index = fields.index("lladdr") + 1
        if mac_index < len(fields):
            devices[fields[0]] = normalize_mac_address(fields[mac_index])
    return devices


def _read_arp_table() -> dict[str, str]:
    """Read IP-to-MAC mappings from the Linux ARP table."""
    devices: dict[str, str] = {}
    try:
        with open("/proc/net/arp", encoding="utf-8") as arp_file:
            lines = arp_file.readlines()[1:]
    except (FileNotFoundError, PermissionError) as err:
        _LOGGER.debug("Could not read Linux ARP table: %s", err)
        return devices

    for line in lines:
        fields = line.split()
        if len(fields) >= 4 and fields[2] == "0x1":
            mac = normalize_mac_address(fields[3])
            if len(mac) == 12 and mac != "0" * 12:
                devices[fields[0]] = mac
    return devices


def _get_network_details() -> tuple[str, ipaddress.IPv4Network] | None:
    """Return the first global IPv4 interface and its subnet."""
    try:
        result = subprocess.run(
            ["ip", "-o", "-f", "inet", "addr", "show", "scope", "global"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as err:
        _LOGGER.error("Could not determine local network interface: %s", err)
        return None

    if result.returncode != 0:
        _LOGGER.error(
            "Could not determine local network interface: %s",
            result.stderr.strip(),
        )
        return None

    for line in result.stdout.splitlines():
        fields = line.split()
        try:
            iface_index = fields.index("inet") + 1
            address = ipaddress.ip_interface(fields[iface_index])
            interface = fields[1].split("@", 1)[0].rstrip(":")
        except (ValueError, IndexError):
            continue
        if isinstance(address.ip, ipaddress.IPv4Address):
            return interface, address.network

    _LOGGER.error("No global IPv4 network interface was found")
    return None


def _scan_with_arp_scan(interface: str) -> dict[str, str]:
    """Use arp-scan when installed to discover active LAN devices."""
    devices: dict[str, str] = {}
    try:
        result = subprocess.run(
            ["arp-scan", "--interface", interface, "--localnet", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError:
        return devices
    except subprocess.TimeoutExpired:
        _LOGGER.warning("LAN scan with arp-scan timed out")
        return devices

    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 2:
            continue
        try:
            ipaddress.IPv4Address(fields[0])
        except ValueError:
            continue
        if _MAC_PATTERN.fullmatch(fields[1]):
            devices[fields[0]] = normalize_mac_address(fields[1])
    return devices


def _probe_ssh_hosts(
    network: ipaddress.IPv4Network, port: int
) -> set[str]:
    """Probe SSH on local subnet addresses and return responsive IPs."""
    hosts = list(network.hosts())
    if len(hosts) > 1024:
        _LOGGER.warning(
            "Not scanning %s because it contains more than 1024 host addresses",
            network,
        )
        return set()

    def probe(address: ipaddress.IPv4Address) -> str | None:
        try:
            with socket.create_connection((str(address), port), timeout=0.4):
                return str(address)
        except OSError:
            return None

    with ThreadPoolExecutor(max_workers=64) as executor:
        return {
            address
            for address in executor.map(probe, hosts)
            if address is not None
        }


def find_device_by_mac(mac_address: str, port: int = 22) -> str | None:
    """Find the IPv4 address belonging to a MAC address on the local LAN."""
    target_mac = normalize_mac_address(mac_address)
    if len(target_mac) != 12 or not all(c in "0123456789abcdef" for c in target_mac):
        _LOGGER.error("Cannot search for invalid MAC address %s", mac_address)
        return None

    network_details = _get_network_details()
    if not network_details:
        return None
    interface, network = network_details

    active_devices = _scan_with_arp_scan(interface)
    for ip_address, mac_address_found in active_devices.items():
        if mac_address_found == target_mac:
            return ip_address

    responsive_hosts = _probe_ssh_hosts(network, port)
    devices = _read_arp_table()
    devices.update(_read_neighbors(interface))
    return next(
        (
            ip_address
            for ip_address in responsive_hosts
            if devices.get(ip_address) == target_mac
        ),
        None,
    )


async def async_find_device_by_mac(
    mac_address: str, port: int = 22
) -> str | None:
    """Run the LAN scan without blocking Home Assistant's event loop."""
    return await asyncio.to_thread(find_device_by_mac, mac_address, port)
