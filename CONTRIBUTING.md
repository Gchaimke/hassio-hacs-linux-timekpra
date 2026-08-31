# Contributing to Linux Timekpra Integration

Thank you for your interest in contributing to the Linux Timekpra integration! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Assume good intentions
- Focus on code and ideas, not on individuals

## Getting Started

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/Gchaimke/hassio-hacs-linux-timekpra.git
   cd hassio-hacs-linux-timekpra
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Setup pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Code Style

This project follows these conventions:

- **Python**: PEP 8 with Black formatter (line length: 100)
- **Imports**: Organized with isort (Black profile)
- **Type Hints**: Full type hints required (checked with MyPy)
- **Docstrings**: Google-style docstrings with type information

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest custom_components/linux_timekpra/tests/test_config_flow.py

# Run with coverage
pytest --cov=custom_components/linux_timekpra

# Run with verbose output
pytest -v
```

### Linting and Formatting

```bash
# Format code with Black
black custom_components/linux_timekpra

# Sort imports with isort
isort custom_components/linux_timekpra

# Check with Flake8
flake8 custom_components/linux_timekpra

# Type check with MyPy
mypy custom_components/linux_timekpra

# Lint with Pylint
pylint custom_components/linux_timekpra
```

Or run all checks at once:

```bash
pre-commit run --all-files
```

## Adding New Features

### 1. Write Tests First (TDD)

```python
# tests/test_new_feature.py
import pytest
from ..module import new_function

@pytest.mark.asyncio
async def test_new_feature():
    """Test new feature."""
    result = await new_function()
    assert result == expected_value
```

### 2. Implement the Feature

```python
# module.py
async def new_function() -> str:
    """Implementation of new feature."""
    return "result"
```

### 3. Add Strings (UI Text)

Update `strings.json` with any new configuration options or entity names:

```json
{
  "config": {
    "step": {
      "step_name": {
        "data": {
          "new_option": "Display name for option"
        }
      }
    }
  }
}
```

### 4. Update Documentation

- Add feature description to README.md
- Include usage examples
- Document any new configuration options
- Add to the appropriate section in this file

## Bug Reports and Features

### Reporting Bugs

When reporting a bug, include:
- Home Assistant version
- Integration version
- Python version
- Detailed error description
- Steps to reproduce
- Relevant logs (use code blocks)

Example:
```
**Describe the bug**
SSH connection fails intermittently when...

**To Reproduce**
1. Configure with...
2. Wait for...
3. Observe error...

**Logs**
```
Error message from logs
```

**Environment**
- Home Assistant: 2024.1.0
- Integration version: 1.0.0
- Python: 3.11
```

### Feature Requests

Describe:
- The use case
- Expected behavior
- Why it would be useful
- Any implementation suggestions

## Pull Request Process

### Before Submitting

1. **Update from main branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run full test suite**
   ```bash
   pytest
   pre-commit run --all-files
   ```

3. **Update documentation** if needed

4. **Create clear commit messages**
   ```
   feat: Add new entity type
   
   - Implement XYZ entity
   - Add unit tests
   - Update documentation
   ```

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
Describe testing performed:
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] No breaking changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Project Structure

```
linux_timekpra/
├── __init__.py              # Main integration setup
├── config_flow.py           # Configuration UI
├── const.py                 # Constants
├── controller.py            # Core business logic (SSH)
├── entity.py                # Base entity class
├── manifest.json            # Integration metadata
│
├── sensor.py                # Platform: Sensors
├── button.py                # Platform: Buttons
├── number.py                # Platform: Numbers
├── select.py                # Platform: Selects
├── switch.py                # Platform: Switches
│
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_config_flow.py
│   └── test_controller.py
│
└── README.md                # User documentation
```

## Areas Where Help Is Needed

- **Documentation**: Expand examples, clarify complex sections
- **Testing**: Add more comprehensive tests
- **Features**: SSH key management improvements, additional entity types
- **Translations**: Provide translations for other languages
- **Bug Fixes**: Help identify and fix edge cases

## Questions?

- Check existing [GitHub Issues](https://github.com/Gchaimke/hassio-hacs-linux-timekpra/issues)
- Create a [Discussion](https://github.com/Gchaimke/hassio-hacs-linux-timekpra/discussions)
- Review Home Assistant [Developer Docs](https://developers.home-assistant.io/)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md (if created)
- Release notes
- GitHub contributors page

---

Thank you for contributing to Linux Timekpra! 🎉
