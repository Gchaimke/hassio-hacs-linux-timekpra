"""Switch platform for Linux Timekpra integration."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
    """Set up switch entities."""
    controller: TimekpraController = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TimekpraScreenBlockSwitch(controller, entry.entry_id),
    ]

    async_add_entities(entities)


class TimekpraScreenBlockSwitch(TimekpraEntity, SwitchEntity):
    """Switch to control screen blocking state."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize switch."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra Screen Block"
        self._attr_icon = "mdi:lock"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch (block screen)."""
        success = await self.controller.async_block_screen()
        if success:
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch (unblock screen)."""
        # This would require an unblock command on the remote end
        # For now, we'll just toggle the state locally
        # In a real implementation, you'd add an async_unblock_screen method to controller
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_screen_block"
