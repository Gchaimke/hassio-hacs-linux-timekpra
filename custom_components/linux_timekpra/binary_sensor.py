"""Binary sensor platform for Linux Timekpra integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import TimekpraController
from .entity import TimekpraEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PC connectivity sensor."""
    controller: TimekpraController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TimekpraPcOnlineSensor(controller, entry.entry_id)])


class TimekpraPcOnlineSensor(TimekpraEntity, BinarySensorEntity):
    """Show whether the Linux PC SSH connection is active."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize the connectivity sensor."""
        super().__init__(controller, entry_id)
        self._attr_name = "PC Online"
        self._attr_icon = "mdi:desktop-tower"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool:
        """Return true when the SSH connection is active."""
        return self.controller.is_connected

    @property
    def available(self) -> bool:
        """Keep the sensor available so off is distinguishable from unavailable."""
        return True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_pc_online"
