# Copilot instructions for Linux Timekpra

## Repository overview

This repository is a Home Assistant custom integration for Timekpr-Next. The integration talks to a remote Linux host over SSH, runs adapter scripts installed under `/usr/local/bin/ha_timekpra`, and exposes screen-time data as Home Assistant entities.

The important project boundary is:

- `custom_components/linux_timekpra/` contains the actual Home Assistant integration and tests
- `custom_components/linux_timekpra/ha_timekpra/` contains the remote adapter scripts that bridge Timekpr-Next CLI output into the format the integration expects
- `README.md` and `custom_components/linux_timekpra/README.md` document the SSH setup, remote-host commands, and entity behavior

## Build, test, and lint commands

Set up the repo from the project root:

```bash
python -m pip install -r requirements-dev.txt
pre-commit install
```

Run the project tests:

```bash
python -m pytest custom_components/linux_timekpra/tests/
```

Run a single test file or single test case:

```bash
python -m pytest custom_components/linux_timekpra/tests/test_config_flow.py -q
python -m pytest custom_components/linux_timekpra/tests/test_controller.py -q
python -m pytest custom_components/linux_timekpra/tests/test_sensor.py -q
python -m pytest custom_components/linux_timekpra/tests/test_controller.py -k discovers_and_persists_changed_host -q
```

Run the lint and formatting checks used by this repo:

```bash
black custom_components/linux_timekpra
isort custom_components/linux_timekpra
flake8 custom_components/linux_timekpra
mypy custom_components/linux_timekpra
pylint custom_components/linux_timekpra
pre-commit run --all-files
```

## High-level architecture

### Config entry lifecycle

`custom_components/linux_timekpra/__init__.py` owns the config entry setup and teardown. It:

- loads the relevant HA platforms (`sensor`, `binary_sensor`, `number`, `button`, `select`)
- creates a `TimekpraController`
- stores the controller on `hass.data[DOMAIN][entry_id]`
- starts the controller polling loop and reloads on option updates

### Config flow and options flow

`config_flow.py` is the user-facing setup path. It validates:

- SSH host, user, key path, port
- optional MAC address format
- SSH connectivity before creating the entry

The options flow exposes the same settings for reconfiguration and supports the automatic LAN rediscovery toggle.

### Central controller

`controller.py` is the main integration hub and the most important file to understand for behavior changes. It:

- establishes and maintains the `paramiko.SSHClient`
- runs commands against the remote `ha_timekpra` adapter scripts
- parses the JSON payload returned by the remote CLI into `controller.data`
- polls the remote host on a configured interval
- reconnects automatically when the SSH session drops
- optionally rediscovery the host by MAC address if the configured IP changes

This is the place where command strings, SSH operations, polling, and reconnect logic are coordinated.

### Entity layer

The platform modules are thin wrappers around the controller:

- `sensor.py` exposes online/offline state and screen-time values
- `binary_sensor.py` exposes connection status or boolean sensor state
- `number.py` provides the “minutes to add” value entity
- `button.py` triggers screen blocking and add-time actions
- `select.py` handles preset choices for quick time additions

These entity modules generally read from `controller.data` and call controller methods such as `async_add_time()` or `async_block_screen()` rather than managing SSH logic directly.

### Remote scripts and contract

The integration expects a Linux PC with the Timekpr-Next CLI installed and adapter scripts copied to `/usr/local/bin/ha_timekpra/`. The remote scripts are not part of this repo’s Python package layout, but they are a critical integration contract.

The scripts are expected to return a JSON payload containing fields such as:

- `user`
- `time_spent_day`
- `time_left_day`
- `time_spent_week`
- `time_spent_month`

The integration converts values to minute-based fields for display in Home Assistant.

## Key conventions for this codebase

- Prefer `async_add_executor_job` for blocking Paramiko and filesystem work. Do not block the event loop with SSH calls or file checks.
- Keep SSH/remote-command behavior in `controller.py`; avoid duplicating command execution or connection logic in entity modules.
- Use constants from `const.py` instead of hard-coded strings for config keys, entity attributes, and remote command names.
- Treat the remote-time values as minute-based data in the integration layer even when the remote CLI reports seconds.
- Use Home Assistant config-entry patterns consistently: validate during setup, update options through the options flow, and reload on config changes.
- When changing behavior, add or update tests under `custom_components/linux_timekpra/tests/`; this repo’s tests are written around mocked Paramiko clients and HA pytest fixtures.
- The integration is designed around a single config entry, but it still uses `entry_id`-scoped dispatcher updates to keep platform/entity updates targetable.
- `strings.json` is part of the UI contract for config forms and entity labels; if you change user-visible config text, update the strings as well as any relevant documentation.

## Working style notes

- This is a Home Assistant custom integration, so changes should align with Home Assistant config-entry patterns and entity semantics.
- Prefer surgical edits in the existing integration structure rather than creating a parallel abstraction layer unless the change genuinely requires it.
- If a change touches remote shell behavior, inspect the adapter script expectations in `custom_components/linux_timekpra/ha_timekpra/` alongside the Python code.
