# MaaHelper Deployment Guide

This guide covers the complete deployment process for MaaHelper to PyPI and GitHub.

## 📋 Pre-Deployment Checklist

### ✅ Repository Structure
- [x] Clean repository structure (no `__pycache__`, `.egg-info`)
- [x] Proper `.gitignore` file
- [x] All required documentation files
- [x] Package structure validation passed

### ✅ Documentation
- [x] `README.md` - Comprehensive project documentation
- [x] `CHANGELOG.md` - Version history and release notes
- [x] `CONTRIBUTING.md` - Contribution guidelines
- [x] `LICENSE` - MIT license file

### ✅ Packaging Files
- [x] `pyproject.toml` - Modern Python packaging configuration
- [x] `setup.py` - Legacy packaging support
- [x] `requirements.txt` - Dependencies list
- [x] `MANIFEST.in` - Package manifest

### ✅ Code Quality
- [x] All import issues fixed
- [x] Entry points properly configured
- [x] Version centralized in `__init__.py`
- [x] No duplicate code or redundant files

## 🚀 Deployment Steps

### 1. Final Validation
```bash
# Validate package structure
python scripts/validate_structure.py

# Run tests
python -m pytest tests/

# Check for any remaining issues
python -m flake8 maahelper/ --max-line-length=100
```

### 2. Build Package
```bash
# Install build tools
pip install build twine

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build package
python -m build
```

### 3. Check Package
```bash
# Validate package
python -m twine check dist/*

# Test installation locally
pip install dist/maahelper-0.0.5-py3-none-any.whl
```

### 4. Test PyPI Upload (Optional)
```bash
# Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ maahelper
```

### 5. Production PyPI Upload
```bash
# Upload to PyPI
python -m twine upload dist/*
```

### 6. GitHub Release
1. Create a new release on GitHub
2. Tag version: `v0.0.5`
3. Upload built packages as release assets
4. Include changelog in release notes

## 🛠️ Automated Deployment

Use the provided deployment script for automated deployment:

```bash
# Complete deployment pipeline
python scripts/deploy.py all

# Individual steps
python scripts/deploy.py clean    # Clean artifacts
python scripts/deploy.py build    # Build package
python scripts/deploy.py check    # Validate package
python scripts/deploy.py test     # Upload to Test PyPI
python scripts/deploy.py deploy   # Upload to PyPI
```

## 📦 Package Information

### Current Version: 0.0.5

### Key Features:
- **Custom Agent Prompts (Vibecoding)**: Specialized AI workflows
- **Dynamic Model Discovery**: Auto-fetch latest models
- **Real-time Code Analysis**: Live error detection
- **Smart Git Integration**: AI-powered commits
- **Enhanced CLI Experience**: Better help and feedback

### Entry Points:
- `maahelper` - Main CLI entry point
- `maahelper-keys` - API key management
- Multiple specialized entry points for different workflows

### Dependencies:
- `openai>=1.0.0` - AI provider client
- `rich>=13.0.0` - Terminal UI
- `structlog>=23.0.0` - Logging
- `cryptography>=3.4.0` - Security
- `aiohttp>=3.8.0` - Async HTTP
- `watchdog>=3.0.0` - File watching
- `gitpython>=3.1.0` - Git integration

## 🔍 Post-Deployment Verification

### 1. PyPI Package
- [ ] Package appears on PyPI: https://pypi.org/project/maahelper/
- [ ] Installation works: `pip install maahelper`
- [ ] Entry points work: `maahelper --help`

### 2. GitHub Repository
- [ ] Repository is clean and organized
- [ ] Release is tagged and documented
- [ ] Issues and discussions are enabled
- [ ] README displays correctly

### 3. Functionality Tests
```bash
# Test main functionality
maahelper --version
maahelper --help

# Test new features
maahelper
> prompts
> code-review
> discover-models
```

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Check all relative imports are correct
2. **Entry Point Issues**: Verify `pyproject.toml` and `setup.py` consistency
3. **Missing Dependencies**: Ensure all dependencies are in `requirements.txt`
4. **Build Failures**: Clean artifacts and rebuild

### Support:
- GitHub Issues: https://github.com/AIMLDev726/maahelper/issues
- Documentation: https://github.com/AIMLDev726/maahelper#readme

## 📈 Future Releases

### Version Management:
1. Update version in `maahelper/__init__.py`
2. Update `CHANGELOG.md` with new features
3. Update `pyproject.toml` version
4. Follow semantic versioning (MAJOR.MINOR.PATCH)

### Release Process:
1. Feature development and testing
2. Documentation updates
3. Version bump and changelog
4. Package build and validation
5. PyPI deployment
6. GitHub release creation

---

**MaaHelper v0.0.5 is ready for deployment! 🚀**
