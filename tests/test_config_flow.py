"""Tests for Linux Timekpra config flow."""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from custom_components.linux_timekpra import async_migrate_entry
from custom_components.linux_timekpra.config_flow import (
    TimekpraConfigFlow,
    TimekpraOptionsFlow,
    _validate_connection,
)
from custom_components.linux_timekpra.const import (
    CONF_AUTO_SEARCH_IP,
    CONF_MAC_ADDRESS,
    CONF_SSH_HOST,
    CONF_SSH_KEY_PATH,
)


@pytest.mark.asyncio
async def test_config_flow_user_step_valid(hass, config_entry_data):
    """Test valid user step."""
    config_flow = TimekpraConfigFlow()
    config_flow.hass = hass

    with patch.object(
        config_flow, "_async_validate_connection", return_value=True
    ) as mock_validate:
        result = await config_flow.async_step_user(config_entry_data)

        assert result.get("type") == "create_entry"
        assert result.get("title") == "Timekpra"
        mock_validate.assert_called_once_with(config_entry_data)


@pytest.mark.asyncio
async def test_config_flow_user_step_invalid(hass, config_entry_data):
    """Test invalid user step."""
    config_flow = TimekpraConfigFlow()
    config_flow.hass = hass

    with patch.object(
        config_flow, "_async_validate_connection", return_value=False
    ):
        result = await config_flow.async_step_user(config_entry_data)

        assert result.get("type") == "form"
        errors = result.get("errors")
        assert errors is not None
        assert errors["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_config_flow_rejects_invalid_mac(hass, config_entry_data):
    """Test malformed MAC addresses are rejected before SSH validation."""
    config_flow = TimekpraConfigFlow()
    config_flow.hass = hass
    user_input = {**config_entry_data, CONF_MAC_ADDRESS: "not-a-mac"}

    with patch.object(config_flow, "_async_validate_connection") as mock_validate:
        result = await config_flow.async_step_user(user_input)

    assert result.get("type") == "form"
    errors = result.get("errors")
    assert errors is not None
    assert errors["base"] == "invalid_mac"
    mock_validate.assert_not_called()


@pytest.mark.asyncio
async def test_migrate_entry_removes_host_from_title():
    """Test existing entries get a stable title."""
    hass = MagicMock()
    entry = MagicMock(entry_id="test_entry", version=1)

    assert await async_migrate_entry(hass, entry) is True
    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        title="Timekpra",
        version=2,
    )


@pytest.mark.asyncio
async def test_options_flow_can_update_connection(mock_config_entry):
    """Test options flow exposes and saves updated SSH connection settings."""
    flow = TimekpraConfigFlow.async_get_options_flow(mock_config_entry)
    assert isinstance(flow, TimekpraOptionsFlow)

    with patch.object(
        TimekpraOptionsFlow,
        "config_entry",
        new_callable=PropertyMock,
        return_value=mock_config_entry,
    ):
        result = await flow.async_step_init()
        assert result.get("type") == "form"
        schema_keys = {
            key.schema for key in result["data_schema"].schema
        }
        assert CONF_SSH_HOST in schema_keys
        assert CONF_MAC_ADDRESS in schema_keys
        assert CONF_AUTO_SEARCH_IP in schema_keys

        updated_config = {
            **mock_config_entry.data,
            CONF_SSH_HOST: "192.0.2.25",
            CONF_MAC_ADDRESS: "00:11:22:33:44:55",
            CONF_AUTO_SEARCH_IP: True,
        }
        result = await flow.async_step_init(updated_config)

    assert result.get("type") == "create_entry"
    assert result["data"][CONF_SSH_HOST] == "192.0.2.25"
    assert result["data"][CONF_MAC_ADDRESS] == "00:11:22:33:44:55"
    assert result["data"][CONF_AUTO_SEARCH_IP] is True


@pytest.mark.asyncio
async def test_validate_connection_success(config_entry_data):
    """Test successful connection validation."""
    with (
        patch("paramiko.SSHClient") as mock_ssh_class,
        patch(
            "custom_components.linux_timekpra.config_flow.Ed25519Key."
            "from_private_key_file"
        ) as mock_key,
    ):
        mock_client = MagicMock()
        mock_ssh_class.return_value = mock_client
        mock_key.return_value = MagicMock()

        result = _validate_connection(config_entry_data)

        assert result is True
        mock_client.set_missing_host_key_policy.assert_called_once()
        mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_validate_connection_key_not_found(config_entry_data):
    """Test validation when key file is not found."""
    config_entry_data[CONF_SSH_KEY_PATH] = "/nonexistent/key"

    result = _validate_connection(config_entry_data)

    assert result is False


@pytest.mark.asyncio
async def test_validate_connection_failure(config_entry_data):
    """Test connection validation failure."""
    with (
        patch("paramiko.SSHClient") as mock_ssh_class,
        patch(
            "custom_components.linux_timekpra.config_flow.Ed25519Key."
            "from_private_key_file",
            return_value=MagicMock(),
        ),
    ):
        mock_client = MagicMock()
        mock_client.connect.side_effect = Exception("Connection failed")
        mock_ssh_class.return_value = mock_client

        result = _validate_connection(config_entry_data)

        assert result is False
