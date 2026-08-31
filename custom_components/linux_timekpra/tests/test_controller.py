"""Tests for Linux Timekpra controller."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.core import HomeAssistant

from ..const import (
    ATTR_TIME_LEFT_DAY,
    ATTR_TIME_SPENT_DAY,
    ATTR_TIME_SPENT_MONTH,
    ATTR_TIME_SPENT_WEEK,
    ATTR_USER,
)
from ..controller import TimekpraController


@pytest.mark.asyncio
async def test_controller_connect_success(hass: HomeAssistant, config_entry_data):
    """Test successful SSH connection."""
    controller = TimekpraController(hass, config_entry_data)

    with patch("paramiko.SSHClient") as mock_ssh_class:
        mock_client = MagicMock()
        mock_ssh_class.return_value = mock_client

        with patch("paramiko.Ed25519Key.from_private_key_file") as mock_key:
            mock_key.return_value = MagicMock()

            result = await controller.async_connect()

            assert result is True
            assert controller.is_connected is True
            mock_client.connect.assert_called_once()


@pytest.mark.asyncio
async def test_controller_get_status_success(hass: HomeAssistant, config_entry_data):
    """Test successful status retrieval."""
    controller = TimekpraController(hass, config_entry_data)
    controller.is_connected = True

    json_response = {
        "user": "child",
        "time_spent_day": 7200,
        "time_left_day": 3600,
        "time_spent_week": 50400,
        "time_spent_month": 216000,
    }

    with patch.object(controller, "execute_command") as mock_exec:
        mock_exec.return_value = json.dumps(json_response)

        result = await controller.async_get_status()

        assert result is True
        assert controller.data[ATTR_USER] == "child"
        assert controller.data[ATTR_TIME_SPENT_DAY] == 7200
        assert controller.data[ATTR_TIME_LEFT_DAY] == 3600


@pytest.mark.asyncio
async def test_controller_get_status_invalid_json(hass: HomeAssistant, config_entry_data):
    """Test status retrieval with invalid JSON."""
    controller = TimekpraController(hass, config_entry_data)
    controller.is_connected = True

    with patch.object(controller, "execute_command") as mock_exec:
        mock_exec.return_value = "invalid json"

        result = await controller.async_get_status()

        assert result is False


@pytest.mark.asyncio
async def test_controller_add_time(hass: HomeAssistant, config_entry_data):
    """Test adding screen time."""
    controller = TimekpraController(hass, config_entry_data)
    controller.is_connected = True

    with patch.object(controller, "execute_command") as mock_exec:
        mock_exec.return_value = "Time added successfully"
        with patch.object(controller, "async_get_status") as mock_status:
            mock_status.return_value = True

            result = await controller.async_add_time(15)

            assert result is True
            mock_exec.assert_called_once()
            mock_status.assert_called_once()


@pytest.mark.asyncio
async def test_controller_block_screen(hass: HomeAssistant, config_entry_data):
    """Test blocking screen."""
    controller = TimekpraController(hass, config_entry_data)
    controller.is_connected = True

    with patch.object(controller, "execute_command") as mock_exec:
        mock_exec.return_value = "Screen blocked"
        with patch.object(controller, "async_get_status") as mock_status:
            mock_status.return_value = True

            result = await controller.async_block_screen()

            assert result is True
            mock_exec.assert_called_once()
            mock_status.assert_called_once()


@pytest.mark.asyncio
async def test_controller_execute_command_success(
    hass: HomeAssistant, config_entry_data
):
    """Test successful command execution."""
    controller = TimekpraController(hass, config_entry_data)
    controller.is_connected = True

    stdin = MagicMock()
    stdout = MagicMock()
    stderr = MagicMock()
    stdout.read = MagicMock(return_value=b"command output")
    stderr.read = MagicMock(return_value=b"")

    with patch.object(controller._ssh_client, "exec_command") as mock_exec:
        controller._ssh_client = MagicMock()
        controller._ssh_client.exec_command = MagicMock(
            return_value=(stdin, stdout, stderr)
        )

        result = await controller.execute_command("test command")

        assert result == "command output"
