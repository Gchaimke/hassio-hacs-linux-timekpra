"""Tests for Linux Timekpra config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.core import HomeAssistant

from ..config_flow import TimekpraConfigFlow
from ..const import (
    CONF_COMMAND_PATH,
    CONF_SCAN_INTERVAL,
    CONF_SSH_HOST,
    CONF_SSH_KEY_PATH,
    CONF_SSH_PORT,
    CONF_SSH_USER,
    DOMAIN,
)


@pytest.mark.asyncio
async def test_config_flow_user_step_valid(hass: HomeAssistant, config_entry_data):
    """Test valid user step."""
    config_flow = TimekpraConfigFlow()
    config_flow.hass = hass

    with patch.object(
        config_flow, "_async_validate_connection", return_value=True
    ) as mock_validate:
        result = await config_flow.async_step_user(config_entry_data)

        assert result["type"] == "create_entry"
        assert result["title"] == f"Timekpra ({config_entry_data[CONF_SSH_HOST]})"
        mock_validate.assert_called_once_with(config_entry_data)


@pytest.mark.asyncio
async def test_config_flow_user_step_invalid(hass: HomeAssistant, config_entry_data):
    """Test invalid user step."""
    config_flow = TimekpraConfigFlow()
    config_flow.hass = hass

    with patch.object(
        config_flow, "_async_validate_connection", return_value=False
    ):
        result = await config_flow.async_step_user(config_entry_data)

        assert result["type"] == "form"
        assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_validate_connection_success(config_entry_data):
    """Test successful connection validation."""
    with patch("paramiko.SSHClient") as mock_ssh_class:
        mock_client = AsyncMock()
        mock_ssh_class.return_value = mock_client

        result = await TimekpraConfigFlow._async_validate_connection(config_entry_data)

        assert result is True
        mock_client.set_missing_host_key_policy.assert_called_once()
        mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_validate_connection_key_not_found(config_entry_data):
    """Test validation when key file is not found."""
    config_entry_data[CONF_SSH_KEY_PATH] = "/nonexistent/key"

    result = await TimekpraConfigFlow._async_validate_connection(config_entry_data)

    assert result is False


@pytest.mark.asyncio
async def test_validate_connection_failure(config_entry_data):
    """Test connection validation failure."""
    with patch("paramiko.SSHClient") as mock_ssh_class:
        mock_client = AsyncMock()
        mock_client.connect.side_effect = Exception("Connection failed")
        mock_ssh_class.return_value = mock_client

        result = await TimekpraConfigFlow._async_validate_connection(config_entry_data)

        assert result is False
