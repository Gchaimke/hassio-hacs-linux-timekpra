# Linux Timekpra Integration

A Home Assistant custom integration for managing screen time on Linux PCs using the [Timekpr-Next](https://mjasnik.gitlab.io/timekpr-next/) CLI tool via SSH.

## Features

- 📊 **Real-time Screen Time Monitoring** - Track daily, weekly, and monthly screen time usage
- ⏱️ **Time Management** - Add screen time through multiple interfaces (number input, presets, services)
- 🔒 **Screen Blocking** - Immediately block screen access with a button or switch
- 🔐 **Secure SSH Connection** - Supports Ed25519 and RSA private keys
- 🔄 **Auto-reconnection** - Automatically reconnects on connection loss
- 📱 **Flexible UI** - Multiple entity types for different automation scenarios

## Installation

### Prerequisites

1. Home Assistant instance running
2. Linux PC with Timekpra CLI installed at `/usr/local/bin/ha_timekpra/`
3. SSH access to the Linux PC with key-based authentication
4. SSH key file accessible from Home Assistant config directory

### Installation Steps

1. Clone this repository into your `custom_components` directory:
   ```bash
  git clone https://github.com/Gchaimke/hassio-hacs-linux-timekpra.git \
     ~/.homeassistant/custom_components/linux_timekpra
   ```

2. Or add via HACS (when published):
   - Open HACS
   - Go to Integrations
   - Click "Explore & Download Repositories"
   - Search for "Linux Timekpra"
   - Click "Install"

3. Restart Home Assistant

## Configuration

### Web UI Configuration Flow

1. Go to **Settings → Devices & Services → Create Integration**
2. Search for "Linux Timekpra"
3. Fill in the SSH connection details:
  - **SSH Host Address**: IP or hostname of your Linux PC (e.g., `192.0.2.10` or `pc.local`)
   - **SSH Username**: User account for SSH connection (e.g., `ha-control`)
   - **SSH Private Key Path**: Path to your private key in Home Assistant (e.g., `/config/.ssh/id_ed25519`)
   - **SSH Port**: Usually `22` (default)

4. (Optional) Configure advanced settings:
   - **Polling Interval**: How often to check status (default: 30 seconds)
   - **Command Path**: Path to timekpra commands on remote host (default: `/usr/local/bin/ha_timekpra`)

### SSH Setup Example

```bash
# On your Linux PC, create a dedicated SSH user
sudo useradd -m -s /bin/bash ha-control

# Add Home Assistant's SSH key to authorized_keys
# (transfer your public key to the Linux PC first)
sudo mkdir -p /home/ha-control/.ssh
sudo cat /path/to/id_ed25519.pub >> /home/ha-control/.ssh/authorized_keys
sudo chown ha-control:ha-control /home/ha-control/.ssh
sudo chmod 700 /home/ha-control/.ssh
sudo chmod 600 /home/ha-control/.ssh/authorized_keys

# Allow sudo without password for timekpra commands
echo "ha-control ALL=(ALL) NOPASSWD: /usr/local/bin/ha_timekpra/*" | sudo tee /etc/sudoers.d/ha-timekpra
```

### Install the command adapter scripts

This integration calls four small adapter scripts on the Linux PC. They bridge
the integration to the installed Timekpr-Next CLI:

| Script | Required behavior |
| --- | --- |
| `child-json` | Print one valid JSON object containing the screen-time values listed below |
| `child-add-time` | Accept the number of minutes as its first argument and add that time |
| `child-block` | Block the monitored user's screen |
| `child-status` | Print a short status message; optional for the integration |

Copy the bundled adapter scripts to the remote PC and make them executable.
Run this command from the repository root on a machine that can reach the
Linux PC:

```bash
ssh user@host 'mkdir -p /tmp/ha_timekpra'
scp custom_components/linux_timekpra/ha_timekpra/* user@host:/tmp/ha_timekpra/
ssh user@host 'sudo install -d -o root -g root -m 0755 /usr/local/bin/ha_timekpra && sudo install -o root -g root -m 0755 /tmp/ha_timekpra/* /usr/local/bin/ha_timekpra/'
```

The scripts use the `TIMEKPR_USER` environment variable to select the monitored
Linux account. The default is `child`; replace it with the actual account name
when testing or configure it in each script on the Linux PC:

```bash
sudo sed -i 's/TIMEKPR_USER:-child/TIMEKPR_USER:-your-linux-user/g' /usr/local/bin/ha_timekpra/child-*
```

The scripts use the installed Timekpr-Next CLI. Check the official
[Timekpr-Next documentation](https://mjasnik.gitlab.io/timekpr-next/) and run
`sudo timekpra --help` on the Linux PC before using them.

Test the required scripts locally on the Linux PC before configuring Home
Assistant:

```bash
sudo /usr/local/bin/ha_timekpra/child-json
sudo /usr/local/bin/ha_timekpra/child-add-time 15
sudo /usr/local/bin/ha_timekpra/child-block
sudo /usr/local/bin/ha_timekpra/child-status
```

`child-json` must return these fields. Time values are measured in seconds:

```json
{
  "user": "username",
  "time_spent_day": 3600,
  "time_left_day": 7200,
  "time_spent_week": 25200,
  "time_spent_month": 108000
}
```

## Entities

### Sensors (Read-only)

- **Timekpra User** - Currently monitored user
- **Timekpra Time Left Today** - Remaining screen time for today (in seconds)
- **Timekpra Time Spent Today** - Screen time used today (in seconds)
- **Timekpra Time Spent This Week** - Total screen time this week (in seconds)
- **Timekpra Time Spent This Month** - Total screen time this month (in seconds)

### Controls

- **Timekpra Add Time** (Number) - Add screen time in minutes (1-480 range)
  - Set the value and confirm to add that amount of time
  - Resets to 15 minutes after successful addition

- **Timekpra Preset Time** (Select) - Quick preset options
  - 15 minutes
  - 30 minutes
  - 1 hour
  - 2 hours
  - Custom option for manual entry

- **Timekpra Block Screen** (Button) - Immediately block screen access
  - Press to activate screen block

- **Timekpra Screen Block** (Switch) - Toggle screen block state
  - Turn on to block, turn off to unblock (if supported by Timekpra)

## Services

### `linux_timekpra.add_time`

Add screen time programmatically.

```yaml
service: linux_timekpra.add_time
data:
  minutes: 30
```

### `linux_timekpra.block`

Block screen access.

```yaml
service: linux_timekpra.block
```

## Automation Examples

### Add Time on School Day

```yaml
automation:
  - alias: "Add screen time on school days"
    trigger:
      platform: time
      at: "15:30"
    condition:
      condition: state
      entity_id: input_boolean.school_day
      state: "on"
    action:
      service: linux_timekpra.add_time
      data:
        minutes: 60
```

### Automatic Block at Bedtime

```yaml
automation:
  - alias: "Block screen at bedtime"
    trigger:
      platform: time
      at: "21:00"
    action:
      service: linux_timekpra.block
```

### Send Notification on Low Screen Time

```yaml
automation:
  - alias: "Notify when screen time is low"
    trigger:
      platform: numeric_state
      entity_id: sensor.timekpra_time_left_today
      below: 600  # Less than 10 minutes
    action:
      service: notify.notify
      data:
        message: "Only 10 minutes of screen time remaining today!"
```

## Troubleshooting

### Connection Issues

1. **Cannot connect to SSH host**
   - Verify SSH host address and port
   - Check SSH key file exists and is readable by Home Assistant
   - Ensure SSH server is running on the Linux PC
   - Test connection manually: `ssh -i /path/to/key ha-control@host`

2. **Permission denied**
   - Verify SSH key is in `authorized_keys`
   - Check file permissions: `authorized_keys` should be `600`, `.ssh` should be `700`
   - Ensure `ha-control` user can run sudo commands without password

### Command Failures

1. **Failed to execute timekpra command**
   - Verify timekpra installation: `sudo /usr/local/bin/ha_timekpra/child-json`
   - Check `/usr/local/bin/ha_timekpra/` directory exists and contains scripts
   - Verify sudo permissions are correctly configured

### Data Not Updating

1. **Sensors not updating**
   - Check polling interval setting (default 30 seconds)
   - Verify SSH connection is maintained (check Home Assistant logs)
   - Ensure Timekpra CLI is responding: `ssh ha-control@host 'sudo /usr/local/bin/ha_timekpra/child-json'`

## Required Adapter Commands

See [Install the command adapter scripts](#install-the-command-adapter-scripts)
above for the required filenames, installation commands, and JSON response
format.

## Development

### Running Tests

```bash
pytest custom_components/linux_timekpra/tests/
```

### Project Structure

```
linux_timekpra/
├── __init__.py              # Integration setup
├── config_flow.py           # Configuration flow
├── const.py                 # Constants
├── controller.py            # SSH controller
├── entity.py                # Base entity
├── manifest.json            # Integration manifest
├── strings.json             # UI strings
│
├── sensor.py                # Sensor entities
├── button.py                # Button entity
├── number.py                # Number entity
├── select.py                # Select entity
├── switch.py                # Switch entity
│
└── tests/                   # Test suite
    ├── conftest.py          # Test fixtures
    ├── test_config_flow.py   # Config flow tests
    └── test_controller.py    # Controller tests
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the [Hisense Air Conditioner integration](https://github.com/Gchaimke/hassio-hacs-hisense-aircon)
- Timekpra CLI tool for Linux screen time management
- Home Assistant community

## Support

- **Issues**: Report bugs on GitHub Issues
- **Questions**: Check existing issues or create a new discussion
- **Documentation**: See this README and Home Assistant documentation

---

Made with ❤️ for Home Assistant users
