#!/usr/bin/env python3
"""
Package Structure Validation Script
Ensures MaaHelper follows Python packaging best practices
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description=""):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"  ✅ {filepath} {description}")
        return True
    else:
        print(f"  ❌ {filepath} {description} - MISSING")
        return False

def check_directory_exists(dirpath, description=""):
    """Check if a directory exists and report status"""
    if os.path.isdir(dirpath):
        print(f"  ✅ {dirpath}/ {description}")
        return True
    else:
        print(f"  ❌ {dirpath}/ {description} - MISSING")
        return False

def validate_package_structure():
    """Validate the complete package structure"""
    print("🔍 Validating MaaHelper Package Structure")
    print("=" * 50)
    
    errors = 0
    
    # Root files
    print("\n📄 Root Files:")
    required_files = [
        ("README.md", "- Project documentation"),
        ("LICENSE", "- MIT license file"),
        ("CHANGELOG.md", "- Version history"),
        ("CONTRIBUTING.md", "- Contribution guidelines"),
        ("pyproject.toml", "- Modern Python packaging"),
        ("setup.py", "- Legacy packaging support"),
        ("requirements.txt", "- Dependencies"),
        ("MANIFEST.in", "- Package manifest"),
        (".gitignore", "- Git ignore rules")
    ]
    
    for filepath, desc in required_files:
        if not check_file_exists(filepath, desc):
            errors += 1
    
    # Package structure
    print("\n📦 Package Structure:")
    package_dirs = [
        ("maahelper", "- Main package"),
        ("maahelper/cli", "- CLI interface"),
        ("maahelper/core", "- Core functionality"),
        ("maahelper/features", "- Feature modules"),
        ("maahelper/managers", "- Management utilities"),
        ("maahelper/utils", "- Utility functions"),
        ("maahelper/vibecoding", "- Custom prompts"),
        ("tests", "- Test suite"),
        ("scripts", "- Deployment scripts")
    ]
    
    for dirpath, desc in package_dirs:
        if not check_directory_exists(dirpath, desc):
            errors += 1
    
    # Essential Python files
    print("\n🐍 Essential Python Files:")
    python_files = [
        ("maahelper/__init__.py", "- Package initialization"),
        ("maahelper/__main__.py", "- Main entry point"),
        ("maahelper/cli_entry.py", "- CLI entry handler"),
        ("maahelper/cli/__init__.py", "- CLI package init"),
        ("maahelper/core/__init__.py", "- Core package init"),
        ("tests/__init__.py", "- Tests package init")
    ]
    
    for filepath, desc in python_files:
        if not check_file_exists(filepath, desc):
            errors += 1
    
    # Check for unwanted files
    print("\n🧹 Checking for Unwanted Files:")
    unwanted_patterns = [
        "__pycache__",
        "*.egg-info",
        "*.pyc",
        "build",
        "dist",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    found_unwanted = False
    for pattern in unwanted_patterns:
        if "*" in pattern:
            # Check for pattern matches
            import glob
            matches = glob.glob(f"**/{pattern}", recursive=True)
            if matches:
                print(f"  ⚠️  Found unwanted files: {matches}")
                found_unwanted = True
        else:
            if os.path.exists(pattern):
                print(f"  ⚠️  Found unwanted: {pattern}")
                found_unwanted = True
    
    if not found_unwanted:
        print("  ✅ No unwanted files found")
    
    # Validate entry points
    print("\n🚀 Entry Points Validation:")
    try:
        import configparser
        
        # Check setup.py entry points
        if os.path.exists("setup.py"):
            with open("setup.py", "r") as f:
                setup_content = f.read()
                if "maahelper = " in setup_content:
                    print("  ✅ Entry points found in setup.py")
                else:
                    print("  ❌ Entry points missing in setup.py")
                    errors += 1
        
        # Check pyproject.toml entry points
        if os.path.exists("pyproject.toml"):
            with open("pyproject.toml", "r") as f:
                toml_content = f.read()
                if "[project.scripts]" in toml_content and "maahelper =" in toml_content:
                    print("  ✅ Entry points found in pyproject.toml")
                else:
                    print("  ❌ Entry points missing in pyproject.toml")
                    errors += 1
    
    except Exception as e:
        print(f"  ⚠️  Could not validate entry points: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    if errors == 0:
        print("🎉 VALIDATION PASSED - Package structure is ready for deployment!")
        print("\n📋 Next Steps:")
        print("  1. Run tests: python -m pytest tests/")
        print("  2. Build package: python -m build")
        print("  3. Check package: python -m twine check dist/*")
        print("  4. Deploy: python scripts/deploy.py")
        return True
    else:
        print(f"❌ VALIDATION FAILED - {errors} issues found")
        print("\n🔧 Please fix the issues above before deployment")
        return False

def main():
    """Main validation function"""
    # Change to package root
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)
    
    success = validate_package_structure()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
