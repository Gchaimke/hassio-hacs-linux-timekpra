"""Fixtures for Linux Timekpra integration tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_ssh_client():
    """Create a mock SSH client."""
    client = MagicMock()
    client.connect = AsyncMock()
    client.close = MagicMock()
    client.exec_command = MagicMock()

    # Mock command responses
    def create_command_result(output: str):
        stdin = MagicMock()
        stdout = MagicMock()
        stderr = MagicMock()
        stdout.read = MagicMock(return_value=output.encode())
        stderr.read = MagicMock(return_value=b"")
        return stdin, stdout, stderr

    client.exec_command.side_effect = lambda cmd: create_command_result(
        '{"time_left_day": 3600, "time_spent_day": 7200, "time_spent_week": 50400, "time_spent_month": 216000, "user": "child"}'
    )

    return client


@pytest.fixture
def mock_ssh_key():
    """Create a mock SSH key."""
    key = MagicMock()
    return key


@pytest.fixture
def config_entry_data(tmp_path):
    """Create mock config entry data."""
    key_path = tmp_path / "id_ed25519"
    key_path.write_text("test key")
    return {
        "ssh_host": "192.0.2.10",
        "ssh_user": "ha-control",
        "ssh_key_path": str(key_path),
        "ssh_port": 22,
        "scan_interval": 30,
        "command_path": "/usr/local/bin/ha_timekpra",
        "entry_id": "test_entry",
    }


@pytest.fixture
async def hass(tmp_path):
    """Create a test Home Assistant instance."""
    hass = HomeAssistant(str(tmp_path))
    yield hass
    await hass.async_block_till_done()


@pytest.fixture
def mock_config_entry(config_entry_data):
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = config_entry_data
    entry.options = {}
    entry.async_on_unload = MagicMock(return_value=MagicMock())
    entry.add_update_listener = MagicMock(return_value=MagicMock())
    return entry
