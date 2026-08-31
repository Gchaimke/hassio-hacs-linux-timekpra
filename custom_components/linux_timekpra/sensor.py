"""Sensor platform for Linux Timekpra integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_TIME_LEFT_DAY,
    ATTR_TIME_SPENT_DAY,
    ATTR_TIME_SPENT_MONTH,
    ATTR_TIME_SPENT_WEEK,
    ATTR_USER,
    DOMAIN,
)
from .controller import TimekpraController
from .entity import TimekpraEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    controller: TimekpraController = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TimekpraUserSensor(controller, entry.entry_id),
        TimekpraTimeSpentDaySensor(controller, entry.entry_id),
        TimekpraTimeLeftDaySensor(controller, entry.entry_id),
        TimekpraTimeSpentWeekSensor(controller, entry.entry_id),
        TimekpraTimeSpentMonthSensor(controller, entry.entry_id),
    ]

    async_add_entities(entities)


class TimekpraUserSensor(TimekpraEntity, SensorEntity):
    """Sensor for screen time user."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize sensor."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra User"
        self._attr_icon = "mdi:account"
        self._attr_device_class = SensorDeviceClass.ENUM

    @property
    def state(self) -> str | None:
        """Return state."""
        return self.controller.data.get(ATTR_USER)

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_user"


class TimekpraTimeSpentDaySensor(TimekpraEntity, SensorEntity):
    """Sensor for time spent today."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize sensor."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra Time Spent Today"
        self._attr_icon = "mdi:clock"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return duration in minutes."""
        return self.controller.data.get(ATTR_TIME_SPENT_DAY)

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_time_spent_day"


class TimekpraTimeLeftDaySensor(TimekpraEntity, SensorEntity):
    """Sensor for time left today."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize sensor."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra Time Left Today"
        self._attr_icon = "mdi:clock-outline"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return duration in minutes."""
        return self.controller.data.get(ATTR_TIME_LEFT_DAY)

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_time_left_day"


class TimekpraTimeSpentWeekSensor(TimekpraEntity, SensorEntity):
    """Sensor for time spent this week."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize sensor."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra Time Spent This Week"
        self._attr_icon = "mdi:calendar-week"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return duration in minutes."""
        return self.controller.data.get(ATTR_TIME_SPENT_WEEK)

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_time_spent_week"


class TimekpraTimeSpentMonthSensor(TimekpraEntity, SensorEntity):
    """Sensor for time spent this month."""

    def __init__(self, controller: TimekpraController, entry_id: str) -> None:
        """Initialize sensor."""
        super().__init__(controller, entry_id)
        self._attr_name = "Timekpra Time Spent This Month"
        self._attr_icon = "mdi:calendar-month"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return duration in minutes."""
        return self.controller.data.get(ATTR_TIME_SPENT_MONTH)

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._entry_id}_time_spent_month"
