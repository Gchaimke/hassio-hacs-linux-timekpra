"""Button platform for Linux Timekpra integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up button entities."""
    controller: TimekpraController = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TimekpraBlockButton(controller, entry.entry_id),
    ]

    async_add_entities(entities)


class TimekpraBlockButton(TimekpraEntity, ButtonEntity):
    """Button to block screen access."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize button."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra Block Screen"
        self._attr_icon = "mdi:lock"

    async def async_press(self) -> None:
        """Handle button press."""
        success = await self.controller.async_block_screen()
        if success:
            self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_block_button"
