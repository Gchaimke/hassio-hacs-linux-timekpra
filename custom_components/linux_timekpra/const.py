"""Constants for the Linux Timekpra integration."""

from __future__ import annotations

DOMAIN = "linux_timekpra"

# Configuration keys
CONF_SSH_HOST = "ssh_host"
CONF_SSH_USER = "ssh_user"
CONF_SSH_KEY_PATH = "ssh_key_path"
CONF_SSH_PORT = "ssh_port"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_COMMAND_PATH = "command_path"

# Defaults
DEFAULT_SSH_PORT = 22
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_COMMAND_PATH = "/usr/local/bin/ha_timekpra"

# Service names and actions
SERVICE_ADD_TIME = "add_time"
SERVICE_BLOCK = "block"

# Attributes
ATTR_MINUTES = "minutes"
ATTR_TIME_LEFT_DAY = "time_left_day"
ATTR_TIME_SPENT_DAY = "time_spent_day"
ATTR_TIME_SPENT_WEEK = "time_spent_week"
ATTR_TIME_SPENT_MONTH = "time_spent_month"
ATTR_USER = "user"

# Status fields from JSON response
RESPONSE_TIME_LEFT_DAY = "time_left_day"
RESPONSE_TIME_SPENT_DAY = "time_spent_day"
RESPONSE_TIME_SPENT_WEEK = "time_spent_week"
RESPONSE_TIME_SPENT_MONTH = "time_spent_month"
RESPONSE_USER = "user"

# Commands
CMD_STATUS = "child-status"
CMD_JSON = "child-json"
CMD_ADD_TIME = "child-add-time"
CMD_BLOCK = "child-block"

# Controller state
ACTIVE_CONTROLLER = "active_controller"


def signal_device_update(entry_id: str) -> str:
    """Return dispatcher signal for a device update."""
    return f"{DOMAIN}_{entry_id}_update"
