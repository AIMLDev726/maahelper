# Contributing to MaaHelper

Thank you for your interest in contributing to MaaHelper! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/maahelper.git
   cd maahelper
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

## 📝 How to Contribute

### Reporting Bugs
- Use the GitHub issue tracker
- Include detailed reproduction steps
- Provide system information (OS, Python version, etc.)
- Include error messages and logs

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its use case
- Explain why it would be valuable to users

### Code Contributions

#### 1. Choose an Issue
- Look for issues labeled "good first issue" for beginners
- Comment on the issue to indicate you're working on it

#### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

#### 3. Make Changes
- Follow the coding standards (see below)
- Write tests for new functionality
- Update documentation as needed

#### 4. Test Your Changes
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_specific.py

# Test CLI functionality
python -m maahelper.cli.modern_enhanced_cli
```

#### 5. Submit Pull Request
- Push your branch to your fork
- Create a pull request with a clear description
- Link to any related issues

## 🎯 Coding Standards

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

### Code Structure
```python
"""Module docstring describing purpose."""

import standard_library
import third_party_packages
import local_modules

class ExampleClass:
    """Class docstring."""
    
    def __init__(self, param: str) -> None:
        """Initialize with parameter."""
        self.param = param
    
    def public_method(self, arg: int) -> str:
        """Public method with clear docstring."""
        return f"{self.param}: {arg}"
    
    def _private_method(self) -> None:
        """Private method for internal use."""
        pass
```

### Documentation
- Use clear, concise docstrings
- Include parameter types and return types
- Provide usage examples for complex functions
- Update README.md for user-facing changes

### Testing
- Write unit tests for all new functionality
- Use descriptive test names
- Test both success and failure cases
- Aim for high test coverage

## 🏗️ Project Structure

```
maahelper/
├── maahelper/              # Main package
│   ├── cli/               # CLI interface
│   ├── core/              # Core functionality
│   ├── features/          # Feature modules
│   ├── managers/          # Management utilities
│   ├── utils/             # Utility functions
│   └── vibecoding/        # Custom prompts system
├── tests/                 # Test suite
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python packaging
└── README.md             # Project documentation
```

## 🧪 Testing Guidelines

### Writing Tests
```python
import pytest
from maahelper.core.llm_client import UnifiedLLMClient

def test_llm_client_initialization():
    """Test LLM client initializes correctly."""
    config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key="test-key"
    )
    client = UnifiedLLMClient(config)
    assert client.config.provider == "openai"

@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functions."""
    result = await some_async_function()
    assert result is not None
```

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=maahelper

# Specific module
pytest tests/test_llm_client.py

# Verbose output
pytest -v
```

## 📚 Documentation

### Code Documentation
- Use Google-style docstrings
- Include examples in docstrings
- Document all parameters and return values

### User Documentation
- Update README.md for user-facing changes
- Add examples to demonstrate new features
- Update help text and CLI documentation

## 🔄 Release Process

### Version Numbering
- Follow Semantic Versioning (semver.org)
- Format: MAJOR.MINOR.PATCH
- Update version in `maahelper/__init__.py`

### Creating a Release
1. Update version number
2. Update CHANGELOG.md
3. Create release branch
4. Test thoroughly
5. Create GitHub release
6. Publish to PyPI

## 💬 Community

### Communication
- GitHub Issues for bugs and features
- GitHub Discussions for questions and ideas
- Be respectful and constructive

### Code of Conduct
- Be welcoming and inclusive
- Respect different viewpoints
- Focus on constructive feedback
- Help others learn and grow

## 🙏 Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- GitHub contributors list
- Special thanks for significant contributions

Thank you for contributing to MaaHelper! 🚀
