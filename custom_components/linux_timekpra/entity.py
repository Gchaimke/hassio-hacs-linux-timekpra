"""Base entity for Linux Timekpra integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, signal_device_update


class TimekpraEntity(Entity):
    """Base class for Timekpra entities."""

    def __init__(self, controller: Any, entry_id: str) -> None:
        """Initialize the entity."""
        self.controller = controller
        self._entry_id = entry_id
        self._attr_attribution = "Timekpra"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Linux Timekpra",
            manufacturer="Timekpra",
            model="Screen Time Manager",
            entry_type="service",
        )

    @property
    def unique_id(self) -> str:
        """Return unique ID for the entity."""
        return f"{DOMAIN}_{self._entry_id}"

    async def async_added_to_hass(self) -> None:
        """Connect to update signal when entity is added to Home Assistant."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_device_update(self._entry_id),
                self._on_update,
            )
        )

    @callback
    def _on_update(self) -> None:
        """Handle update from controller."""
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.controller.is_connected
