# Contributing to ClipVault 📋

Thank you for your interest in contributing to ClipVault! This guide will help you get started.

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- No external dependencies required!

### Setup
```bash
# Clone the repository
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/ -v

# Or run tests directly
python tests/test_clipvault.py
```

## 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to all public functions and classes
- Keep functions focused and small (single responsibility)
- Use meaningful variable and function names

## 🐛 Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/gitstq/ClipVault/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Your OS and Python version
   - Clipboard tool detected (`clipvault config show`)

## 💡 Feature Requests

1. Check existing [Issues](https://github.com/gitstq/ClipVault/issues) first
2. Create a new issue with the `enhancement` label
3. Describe the use case and expected behavior

## 🔀 Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python -m pytest tests/ -v`
6. Commit with [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `feat: add new feature`
   - `fix: resolve bug`
   - `docs: update documentation`
   - `refactor: code refactoring`
   - `test: add/update tests`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## 📂 Project Structure

```
ClipVault/
├── src/clipvault/
│   ├── __init__.py          # Package init
│   ├── __main__.py          # CLI entry point
│   ├── core/
│   │   ├── engine.py        # Main engine
│   │   ├── clipboard.py     # Clipboard manager
│   │   ├── storage.py       # SQLite storage
│   │   ├── categorizer.py   # Content categorization
│   │   └── search.py        # Search engine
│   ├── ui/
│   │   └── tui.py           # Terminal UI
│   └── utils/
│       └── helpers.py       # Utility functions
├── tests/
│   └── test_clipvault.py    # Unit tests
├── pyproject.toml           # Package config
└── README.md                # Documentation
```

## 🌍 Translations

ClipVault supports multiple languages. Contributions to translations are welcome!

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
