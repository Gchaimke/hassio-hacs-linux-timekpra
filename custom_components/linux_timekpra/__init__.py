"""Linux Timekpra integration for Home Assistant."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import Platform
    from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _get_platforms() -> list[Platform]:
    """Load Home Assistant platforms only when setting up the integration."""
    from homeassistant.const import Platform

    return [
        Platform.SENSOR,
        Platform.BINARY_SENSOR,
        Platform.NUMBER,
        Platform.BUTTON,
        Platform.SELECT,
    ]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Linux Timekpra from a config entry."""
    from .controller import TimekpraController

    platforms = _get_platforms()
    # Prepare config data
    config = dict(entry.data)
    config["entry_id"] = entry.entry_id

    # Merge options if they exist
    if entry.options:
        config.update(entry.options)

    # Create controller
    controller = TimekpraController(hass, config)

    # Store controller
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller

    # Start controller
    await controller.async_start()

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    # Add listener for options changes
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entries to use a stable title without the host address."""
    if entry.version == 1:
        hass.config_entries.async_update_entry(
            entry,
            title="Timekpra",
            version=2,
        )
        return True

    _LOGGER.error(
        "Cannot migrate config entry %s from version %s",
        entry.entry_id,
        entry.version,
    )
    return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, _get_platforms()
    )

    if unload_ok:
        controller = hass.data[DOMAIN].pop(entry.entry_id)
        await controller.async_stop()

    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
