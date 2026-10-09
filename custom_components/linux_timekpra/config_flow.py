"""Config flow for Linux Timekpra integration."""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Any

import paramiko
import voluptuous as vol
from paramiko import Ed25519Key, RSAKey

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_AUTO_SEARCH_IP,
    CONF_COMMAND_PATH,
    CONF_MAC_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_SSH_HOST,
    CONF_SSH_KEY_PATH,
    CONF_SSH_PORT,
    CONF_SSH_USER,
    DEFAULT_COMMAND_PATH,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SSH_KEY_PATH,
    DEFAULT_SSH_PORT,
    DOMAIN,
    normalize_mac_address,
)

_LOGGER = logging.getLogger(__name__)


class TimekpraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Linux Timekpra."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle user step."""
        errors = {}

        if user_input is not None:
            mac_address = str(user_input.get(CONF_MAC_ADDRESS, ""))
            if mac_address and not re.fullmatch(
                r"[0-9a-f]{12}", normalize_mac_address(mac_address)
            ):
                errors["base"] = "invalid_mac"
            elif await self._async_validate_connection(user_input):
                return self.async_create_entry(
                    title="Timekpra",
                    data=user_input,
                )
            else:
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
                vol.Required(
                    CONF_SSH_KEY_PATH, default=DEFAULT_SSH_KEY_PATH
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(CONF_SSH_PORT, default=22): NumberSelector(
                    NumberSelectorConfig(min=1, max=65535, step=1)
                ),
                vol.Optional(CONF_MAC_ADDRESS, default=""): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Optional(CONF_AUTO_SEARCH_IP, default=True): BooleanSelector(),
            }),
            errors=errors,
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
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

    async def _async_validate_connection(self, config: dict[str, Any]) -> bool:
        """Validate SSH connection without blocking the event loop."""
        return await self.hass.async_add_executor_job(
            _validate_connection, config
        )

    def is_matching(self, other_flow: TimekpraConfigFlow) -> bool:
        """Return True if other_flow is matching this flow."""
        return (
            isinstance(other_flow, TimekpraConfigFlow)
            and other_flow.handler == self.handler
            and other_flow.context.get("source") == self.context.get("source")
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get options flow."""
        return TimekpraOptionsFlow()


def _validate_connection(config: dict[str, Any]) -> bool:
    """Validate an SSH connection in a worker thread."""
    ssh_client = paramiko.SSHClient()
    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        key_path = Path(str(config[CONF_SSH_KEY_PATH])).expanduser()
        if not key_path.exists():
            _LOGGER.error("SSH key file not found: %s", key_path)
            return False

        try:
            key = Ed25519Key.from_private_key_file(str(key_path))
        except (OSError, TypeError, ValueError, paramiko.SSHException):
            try:
                key = RSAKey.from_private_key_file(str(key_path))
            except (OSError, TypeError, ValueError, paramiko.SSHException) as err:
                _LOGGER.error("Failed to load SSH key: %s", err)
                return False

        ssh_client.connect(
            hostname=str(config[CONF_SSH_HOST]),
            port=int(config.get(CONF_SSH_PORT) or 22),
            username=str(config[CONF_SSH_USER]),
            pkey=key,
            timeout=10,
        )
        _LOGGER.debug("SSH connection validation successful")
        return True
    except (OSError, TypeError, ValueError, paramiko.SSHException) as err:
        _LOGGER.error("SSH connection validation failed: %s", err)
        return False
    finally:
        ssh_client.close()


class TimekpraOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Linux Timekpra."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.OptionsFlowResult:
        """Handle options step."""
        errors = {}
        if user_input is not None:
            mac_address = str(user_input.get(CONF_MAC_ADDRESS, ""))
            if mac_address and not re.fullmatch(
                r"[0-9a-f]{12}", normalize_mac_address(mac_address)
            ):
                errors["base"] = "invalid_mac"
            else:
                return self.async_create_entry(title="", data=user_input)

        config_entry = self.config_entry
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SSH_HOST,
                    default=config_entry.options.get(
                        CONF_SSH_HOST, config_entry.data[CONF_SSH_HOST]
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(
                    CONF_SSH_USER,
                    default=config_entry.options.get(
                        CONF_SSH_USER, config_entry.data[CONF_SSH_USER]
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(
                    CONF_SSH_KEY_PATH,
                    default=config_entry.options.get(
                        CONF_SSH_KEY_PATH,
                        config_entry.data.get(
                            CONF_SSH_KEY_PATH, DEFAULT_SSH_KEY_PATH
                        ),
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(
                    CONF_SSH_PORT,
                    default=config_entry.options.get(
                        CONF_SSH_PORT,
                        config_entry.data.get(CONF_SSH_PORT, DEFAULT_SSH_PORT),
                    ),
                ): NumberSelector(
                    NumberSelectorConfig(min=1, max=65535, step=1)
                ),
                vol.Optional(
                    CONF_MAC_ADDRESS,
                    default=config_entry.options.get(
                        CONF_MAC_ADDRESS, config_entry.data.get(CONF_MAC_ADDRESS, "")
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Optional(
                    CONF_AUTO_SEARCH_IP,
                    default=config_entry.options.get(
                        CONF_AUTO_SEARCH_IP,
                        config_entry.data.get(CONF_AUTO_SEARCH_IP, False),
                    ),
                ): BooleanSelector(),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=config_entry.options.get(
                        CONF_SCAN_INTERVAL,
                        config_entry.data.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ),
                ): NumberSelector(
                    NumberSelectorConfig(min=5, max=3600, step=5)
                ),
                vol.Required(
                    CONF_COMMAND_PATH,
                    default=config_entry.options.get(
                        CONF_COMMAND_PATH,
                        config_entry.data.get(
                            CONF_COMMAND_PATH, DEFAULT_COMMAND_PATH
                        ),
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
            }),
            errors=errors,
        )
