# Linux Timekpra

A Home Assistant custom integration for managing screen time on a Linux PC through the [Timekpr-Next](https://mjasnik.gitlab.io/timekpr-next/) command-line tool and an SSH connection.

## Features

- Monitor daily, weekly, and monthly screen-time usage
- Add screen time with a number entity or preset selector
- Block screen access with a button
- Configure the SSH connection through Home Assistant's UI
- Support Ed25519 and RSA SSH keys
- Reconnect automatically after a connection loss

## Requirements

- Home Assistant
- A Linux PC with the Timekpra CLI installed
- SSH key-based access from Home Assistant to that PC
- A dedicated remote user with permission to run the required Timekpra commands

## Installation

### HACS

1. Open **HACS** in Home Assistant.
2. Open **Integrations** and search for **Linux Timekpra**.
3. Install the integration and restart Home Assistant.

### Manual

Copy `custom_components/linux_timekpra` into the `custom_components` directory of your Home Assistant configuration, then restart Home Assistant.

## Configuration

After installation:

1. Go to **Settings > Devices & services**.
2. Select **Add integration**.
3. Search for **Linux Timekpra**.
4. Enter the Linux PC hostname or IP address, SSH username, private-key path, and SSH port.

The detailed SSH setup, entity reference, automation examples, and troubleshooting guide are in [the integration README](custom_components/linux_timekpra/README.md).

## Development

Install the development dependencies and run the tests from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest custom_components/linux_timekpra/tests/
```

The project uses pre-commit hooks for formatting, linting, and type checking.

## Project Structure

```text
custom_components/linux_timekpra/
├── __init__.py             # Integration setup
├── config_flow.py          # Home Assistant configuration flow
├── controller.py           # SSH connection and command handling
├── sensor.py               # Screen-time sensors
├── button.py               # Block action
├── number.py               # Add-time control
├── select.py               # Preset-time control
└── tests/                  # Automated tests
```

## Contributing

Bug reports and pull requests are welcome. Please add or update tests when changing behavior.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
