"""Select platform for Linux Timekpra integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
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
    """Set up select entities."""
    controller: TimekpraController = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TimekpraPresetTimeSelect(controller, entry.entry_id),
    ]

    async_add_entities(entities)


class TimekpraPresetTimeSelect(TimekpraEntity, SelectEntity):
    """Select entity for preset time additions."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize select entity."""
        super().__init__(controller, entry_id)
        self._attr_name = "Preset Time"
        self._attr_icon = "mdi:clock-plus"
        self._attr_options = [
            "15 minutes",
            "30 minutes",
            "1 hour",
            "2 hours",
            "custom",
        ]
        self._attr_current_option = None

    async def async_select_option(self, option: str) -> None:
        """Handle selection of an option."""
        minutes_map = {
            "15 minutes": 15,
            "30 minutes": 30,
            "1 hour": 60,
            "2 hours": 120,
        }

        if option in minutes_map:
            minutes = minutes_map[option]
            success = await self.controller.async_add_time(minutes)
            if success:
                self._attr_current_option = option
                self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_preset_time"
