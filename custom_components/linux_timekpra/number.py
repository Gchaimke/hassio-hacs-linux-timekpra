"""Number platform for Linux Timekpra integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
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
    """Set up number entities."""
    controller: TimekpraController = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TimekpraAddTimeNumber(controller, entry.entry_id),
    ]

    async_add_entities(entities)


class TimekpraAddTimeNumber(TimekpraEntity, NumberEntity):
    """Number entity for adding screen time."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize number entity."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra Minutes to Add"
        self._attr_icon = "mdi:clock-plus"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 480  # 8 hours
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_mode = NumberMode.BOX

    async def async_set_native_value(self, value: float) -> None:
        """Store the number of minutes for the add button."""
        self.controller.pending_add_minutes = int(value)
        self._attr_native_value = self.controller.pending_add_minutes
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return the selected number of minutes."""
        return self.controller.pending_add_minutes

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_add_time"
