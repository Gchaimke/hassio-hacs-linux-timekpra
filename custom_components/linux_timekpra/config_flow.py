"""Config flow for Linux Timekpra integration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import paramiko
import voluptuous as vol
from paramiko import Ed25519Key, RSAKey

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_COMMAND_PATH,
    CONF_SCAN_INTERVAL,
    CONF_SSH_HOST,
    CONF_SSH_KEY_PATH,
    CONF_SSH_PORT,
    CONF_SSH_USER,
    DEFAULT_COMMAND_PATH,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class TimekpraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Linux Timekpra."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle user step."""
        errors = {}

        if user_input is not None:
            # Validate connection
            if await self._async_validate_connection(user_input):
                return self.async_create_entry(
                    title=f"Timekpra ({user_input[CONF_SSH_HOST]})",
                    data=user_input,
                )
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SSH_HOST): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(CONF_SSH_USER): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(CONF_SSH_KEY_PATH): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(CONF_SSH_PORT, default=22): NumberSelector(
                    NumberSelectorConfig(min=1, max=65535, step=1)
                ),
            }),
            errors=errors,
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle advanced settings."""
        if user_input is not None:
            return self.async_create_entry(
                title="Linux Timekpra",
                data=user_input,
            )

        config_entry = self.hass.config_entries.async_get_entry(
            self.context.get("entry_id")
        )
        if not config_entry:
            return self.async_abort(reason="reconfigure_failed")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=config_entry.data.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): NumberSelector(
                    NumberSelectorConfig(min=5, max=3600, step=5)
                ),
                vol.Required(
                    CONF_COMMAND_PATH,
                    default=config_entry.data.get(
                        CONF_COMMAND_PATH, DEFAULT_COMMAND_PATH
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
            }),
        )

    @staticmethod
    async def _async_validate_connection(config: dict[str, Any]) -> bool:
        """Validate SSH connection."""
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Load key
            key_path = Path(config[CONF_SSH_KEY_PATH])
            if not key_path.exists():
                _LOGGER.error("SSH key file not found: %s", config[CONF_SSH_KEY_PATH])
                return False

            try:
                # Try Ed25519 key first
                key = Ed25519Key.from_private_key_file(str(key_path))
            except Exception:
                try:
                    # Fall back to RSA
                    key = RSAKey.from_private_key_file(str(key_path))
                except Exception as err:
                    _LOGGER.error("Failed to load SSH key: %s", err)
                    return False

            # Connect
            ssh_client.connect(
                hostname=config[CONF_SSH_HOST],
                port=config[CONF_SSH_PORT],
                username=config[CONF_SSH_USER],
                pkey=key,
                timeout=10,
            )

            ssh_client.close()
            _LOGGER.debug("SSH connection validation successful")
            return True

        except Exception as err:
            _LOGGER.error("SSH connection validation failed: %s", err)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get options flow."""
        return TimekpraOptionsFlow(config_entry)


class TimekpraOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Linux Timekpra."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle options step."""
        if user_input is not None:
            return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL,
                        self.config_entry.data.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ),
                ): NumberSelector(
                    NumberSelectorConfig(min=5, max=3600, step=5)
                ),
                vol.Required(
                    CONF_COMMAND_PATH,
                    default=self.config_entry.options.get(
                        CONF_COMMAND_PATH,
                        self.config_entry.data.get(
                            CONF_COMMAND_PATH, DEFAULT_COMMAND_PATH
                        ),
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
            }),
        )
