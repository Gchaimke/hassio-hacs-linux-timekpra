"""Tests for Linux Timekpra sensors."""

from __future__ import annotations

from unittest.mock import MagicMock

from ..sensor import TimekpraCurrentIpSensor


def test_current_ip_sensor_tracks_controller_host():
    """Test the sensor exposes host changes discovered by the controller."""
    controller = MagicMock()
    controller.ssh_host = "192.0.2.10"
    sensor = TimekpraCurrentIpSensor(controller, "test_entry")

    assert sensor.native_value == "192.0.2.10"
    assert sensor.available is True
    assert sensor.unique_id == "linux_timekpra_test_entry_current_ip"

    controller.ssh_host = "192.0.2.25"
    assert sensor.native_value == "192.0.2.25"


def test_current_ip_sensor_is_empty_when_host_is_missing():
    """Test an unset SSH host produces no sensor value."""
    controller = MagicMock()
    controller.ssh_host = ""
    sensor = TimekpraCurrentIpSensor(controller, "test_entry")

    assert sensor.native_value is None
