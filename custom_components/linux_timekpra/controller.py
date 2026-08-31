"""Controller for Linux Timekpra integration."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import paramiko
from paramiko import RSAKey, Ed25519Key

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    ACTIVE_CONTROLLER,
    ATTR_TIME_LEFT_DAY,
    ATTR_TIME_SPENT_DAY,
    ATTR_TIME_SPENT_MONTH,
    ATTR_TIME_SPENT_WEEK,
    ATTR_USER,
    CMD_ADD_TIME,
    CMD_BLOCK,
    CMD_JSON,
    CMD_STATUS,
    CONF_COMMAND_PATH,
    CONF_SSH_HOST,
    CONF_SSH_KEY_PATH,
    CONF_SSH_PORT,
    CONF_SSH_USER,
    DEFAULT_COMMAND_PATH,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    signal_device_update,
)

_LOGGER = logging.getLogger(__name__)


class TimekpraController:
    """Controller for managing Timekpra via SSH."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict[str, Any],
    ) -> None:
        """Initialize the controller."""
        self.hass = hass
        self.config = config
        self._ssh_client: paramiko.SSHClient | None = None
        self._task: asyncio.Task[None] | None = None
        self.is_connected = False
        self.data: dict[str, Any] = {
            ATTR_USER: None,
            ATTR_TIME_SPENT_DAY: 0,
            ATTR_TIME_LEFT_DAY: 0,
            ATTR_TIME_SPENT_WEEK: 0,
            ATTR_TIME_SPENT_MONTH: 0,
        }

    @property
    def ssh_host(self) -> str:
        """Get SSH host."""
        return self.config.get(CONF_SSH_HOST)

    @property
    def ssh_user(self) -> str:
        """Get SSH user."""
        return self.config.get(CONF_SSH_USER)

    @property
    def ssh_port(self) -> int:
        """Get SSH port."""
        return self.config.get(CONF_SSH_PORT, 22)

    @property
    def ssh_key_path(self) -> str:
        """Get SSH key path."""
        return self.config.get(CONF_SSH_KEY_PATH)

    @property
    def scan_interval(self) -> int:
        """Get scan interval."""
        return self.config.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    @property
    def command_path(self) -> str:
        """Get command path."""
        return self.config.get(CONF_COMMAND_PATH, DEFAULT_COMMAND_PATH)

    async def async_connect(self) -> bool:
        """Connect to SSH server."""
        try:
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Load key
            key_path = Path(self.ssh_key_path)
            if not key_path.exists():
                _LOGGER.error("SSH key file not found: %s", self.ssh_key_path)
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
            self._ssh_client.connect(
                hostname=self.ssh_host,
                port=self.ssh_port,
                username=self.ssh_user,
                pkey=key,
                timeout=10,
            )

            self.is_connected = True
            _LOGGER.debug("Connected to SSH server %s@%s", self.ssh_user, self.ssh_host)
            return True

        except Exception as err:
            _LOGGER.error("Failed to connect to SSH server: %s", err)
            self.is_connected = False
            return False

    async def async_disconnect(self) -> None:
        """Disconnect from SSH server."""
        if self._ssh_client:
            self._ssh_client.close()
        self.is_connected = False

    async def execute_command(self, command: str) -> str | None:
        """Execute a command on the remote host."""
        if not self._ssh_client or not self.is_connected:
            _LOGGER.error("Not connected to SSH server")
            return None

        try:
            stdin, stdout, stderr = self._ssh_client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if error:
                _LOGGER.error("Command error: %s", error)
                return None

            return output

        except Exception as err:
            _LOGGER.error("Failed to execute command: %s", err)
            self.is_connected = False
            return None

    async def async_get_status(self) -> bool:
        """Get screen time status from remote host."""
        command = f"sudo {self.command_path}/{CMD_JSON}"

        result = await self.execute_command(command)
        if not result:
            return False

        try:
            data = json.loads(result)
            self.data = {
                ATTR_USER: data.get(ATTR_USER),
                ATTR_TIME_SPENT_DAY: data.get(ATTR_TIME_SPENT_DAY, 0),
                ATTR_TIME_LEFT_DAY: data.get(ATTR_TIME_LEFT_DAY, 0),
                ATTR_TIME_SPENT_WEEK: data.get(ATTR_TIME_SPENT_WEEK, 0),
                ATTR_TIME_SPENT_MONTH: data.get(ATTR_TIME_SPENT_MONTH, 0),
            }
            return True
        except json.JSONDecodeError as err:
            _LOGGER.error("Failed to parse JSON response: %s", err)
            return False

    async def async_add_time(self, minutes: int) -> bool:
        """Add screen time."""
        command = f"sudo {self.command_path}/{CMD_ADD_TIME} '{minutes}'"
        result = await self.execute_command(command)
        if result is None:
            return False

        # Update status after adding time
        await self.async_get_status()
        return True

    async def async_block_screen(self) -> bool:
        """Block screen access."""
        command = f"sudo {self.command_path}/{CMD_BLOCK}"
        result = await self.execute_command(command)
        if result is None:
            return False

        # Update status after blocking
        await self.async_get_status()
        return True

    async def async_start(self) -> None:
        """Start the polling loop."""
        if self not in self.hass.data.setdefault(DOMAIN, {}).values():
            self.hass.data[DOMAIN][ACTIVE_CONTROLLER] = self

        # Initial connection
        if not await self.async_connect():
            _LOGGER.warning("Failed to establish initial connection")

        # Start polling task
        self._task = asyncio.create_task(self._async_poll_loop())

    async def async_stop(self) -> None:
        """Stop the polling loop."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        await self.async_disconnect()

    async def _async_poll_loop(self) -> None:
        """Polling loop to update status."""
        while True:
            try:
                # Reconnect if needed
                if not self.is_connected:
                    if not await self.async_connect():
                        _LOGGER.warning("Reconnection attempt failed")
                        await asyncio.sleep(10)
                        continue

                # Get status
                if await self.async_get_status():
                    # Signal update to all entities
                    async_dispatcher_send(
                        self.hass, signal_device_update(self.config["entry_id"])
                    )

                await asyncio.sleep(self.scan_interval)

            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error("Error in polling loop: %s", err)
                self.is_connected = False
                await asyncio.sleep(self.scan_interval)
