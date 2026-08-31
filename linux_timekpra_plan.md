# Linux Timekpra Integration Build Plan

## Current State
- YAML-based automation using SSH commands to call Linux scripts
- Shell commands for: mac_status, mac_add_time, mac_block
- Command-line sensors for screen time data
- Input helpers for configuration

## Target State
- Full Python Home Assistant integration (like hisense_aircon)
- Type-safe configuration flow
- Proper entity management and lifecycle
- Better error handling and state management

## Core Features to Implement
1. SSH connection management ✅
2. Screen time status sensor (read-only) ✅
3. Screen time tracking (multiple time windows) ✅
4. Add time service ✅
5. Block screen service ✅
6. Configuration flow for SSH setup ✅

## Files Implemented (Phase 1-4)

### Phase 1: Core Infrastructure ✅
- ✅ manifest.json - Integration metadata with Paramiko SSH dependency
- ✅ const.py - Configuration constants and signal definitions
- ✅ __init__.py - Platform registration and async_setup_entry

### Phase 2: Core Controller ✅
- ✅ controller.py - SSH management with Paramiko, async polling loop
- ✅ entity.py - Base entity class with device info and dispatcher signals

### Phase 3: Platforms ✅
- ✅ sensor.py - 5 read-only sensors (user, time_spent_day/week/month, time_left_day)
- ✅ button.py - Block screen action button
- ✅ number.py - Add time number input (1-480 minutes)

### Phase 4: Configuration ✅
- ✅ config_flow.py - SSH connection config flow with validation
- ✅ strings.json - User-facing text and translations

## Additional Files Created

### Phase 5: Additional Platforms ✅
- ✅ select.py - Select entity with preset time options (15min, 30min, 1hr, 2hrs, custom)

### Phase 6: Testing & Development ✅
- ✅ tests/__init__.py - Test package marker
- ✅ tests/conftest.py - Pytest fixtures (mock SSH, config data, etc.)
- ✅ tests/test_config_flow.py - Config flow tests (connection validation, setup flow)
- ✅ tests/test_controller.py - Controller tests (SSH, status updates, commands)

### Phase 7: Documentation & Development Setup ✅
- ✅ README.md - Comprehensive user documentation (22KB)
  - Features, installation, configuration with examples
  - SSH setup walkthrough
  - Entity descriptions
  - Automation examples
  - Troubleshooting guide
  - Development info

- ✅ CONTRIBUTING.md - Contribution guidelines
  - Development setup
  - Code style (PEP 8, Black, isort, MyPy)
  - Testing workflow
  - Feature addition process
  - PR process
  - Project structure

- ✅ pytest.ini - Test configuration
  - Test discovery settings
  - Coverage reporting
  - Logging configuration

- ✅ requirements-dev.txt - Development dependencies
  - Testing: pytest, pytest-asyncio, pytest-cov, pytest-mock
  - Code quality: black, flake8, isort, mypy, pylint
  - Home Assistant dev environment

- ✅ .pre-commit-config.yaml - Pre-commit hooks
  - Auto-formatting (black, isort)
  - Linting (flake8, pylint)
  - Type checking (mypy)
  - File checks (trailing whitespace, JSON, YAML)


## Complete Integration File List

```
custom_components/linux_timekpra/
├── __init__.py                  ✅ Integration setup & platform registration
├── config_flow.py               ✅ SSH configuration & validation
├── const.py                     ✅ Constants & signals
├── controller.py                ✅ SSH client & command execution
├── entity.py                    ✅ Base entity class
├── manifest.json                ✅ Integration metadata
├── strings.json                 ✅ UI text
├── sensor.py                    ✅ 5 read-only sensors
├── button.py                    ✅ Block button
├── number.py                    ✅ Add time input
├── select.py                    ✅ Preset time select
├── README.md                    ✅ User documentation
└── tests/
    ├── __init__.py              ✅ Test package
    ├── conftest.py              ✅ Pytest fixtures
    ├── test_config_flow.py       ✅ Config flow tests
    └── test_controller.py        ✅ Controller tests

Root-level files:
├── pytest.ini                   ✅ Test configuration
├── requirements-dev.txt         ✅ Dev dependencies
├── .pre-commit-config.yaml      ✅ Pre-commit hooks
├── CONTRIBUTING.md              ✅ Contribution guidelines
```

## Implementation Complete! 🎉

All 4 optional components have been implemented:
1. ✅ Select entity for preset time options
3. ✅ Complete test fixtures and test suite
4. ✅ Comprehensive README and documentation
