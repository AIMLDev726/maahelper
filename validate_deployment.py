#!/usr/bin/env python3
"""
MaaHelper Deployment Validation Script
Validates that the package is ready for PyPI deployment
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a required file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False

def check_version_consistency():
    """Check that versions are consistent across files"""
    print("\n🔍 Checking version consistency...")
    
    # Read version from pyproject.toml
    try:
        import toml
        with open('pyproject.toml', 'r') as f:
            pyproject_data = toml.load(f)
        pyproject_version = pyproject_data['project']['version']
        print(f"  pyproject.toml: {pyproject_version}")
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return False
    
    # Read version from __init__.py
    try:
        init_file = Path('maahelper/__init__.py')
        init_content = init_file.read_text()
        for line in init_content.split('\n'):
            if line.startswith('__version__'):
                init_version = line.split('=')[1].strip().strip('"\'')
                print(f"  __init__.py: {init_version}")
                break
        else:
            print("❌ Could not find __version__ in maahelper/__init__.py")
            return False
    except Exception as e:
        print(f"❌ Error reading __init__.py: {e}")
        return False
    
    # Read version from README.md
    try:
        readme_content = Path('README.md').read_text(encoding='utf-8', errors='ignore')
        if f"MaaHelper v{pyproject_version}" in readme_content:
            print(f"  README.md: {pyproject_version} (found)")
        else:
            print(f"⚠️  README.md: version reference may be outdated")
    except Exception as e:
        print(f"❌ Error reading README.md: {e}")
        return False
    
    if pyproject_version == init_version:
        print("✅ Version consistency check passed")
        return True
    else:
        print(f"❌ Version mismatch: pyproject.toml={pyproject_version}, __init__.py={init_version}")
        return False

def check_package_structure():
    """Check package structure"""
    print("\n🔍 Checking package structure...")
    
    required_files = [
        ('pyproject.toml', 'Build configuration'),
        ('README.md', 'Package description'),
        ('LICENSE', 'License file'),
        ('CHANGELOG.md', 'Change log'),
        ('MANIFEST.in', 'Package manifest'),
        ('maahelper/__init__.py', 'Package init'),
        ('.gitignore', 'Git ignore file'),
    ]
    
    all_good = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_imports():
    """Check that main imports work"""
    print("\n🔍 Checking imports...")
    
    try:
        # Test main package import
        spec = importlib.util.spec_from_file_location("maahelper", "maahelper/__init__.py")
        maahelper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(maahelper)
        
        print(f"✅ Package imports successfully")
        print(f"  Version: {maahelper.__version__}")
        print(f"  Author: {maahelper.__author__}")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def check_entry_points():
    """Check that entry points are properly defined"""
    print("\n🔍 Checking entry points...")
    
    try:
        import toml
        with open('pyproject.toml', 'r') as f:
            pyproject_data = toml.load(f)
        
        scripts = pyproject_data.get('project', {}).get('scripts', {})
        
        if not scripts:
            print("❌ No entry points defined")
            return False
        
        print(f"✅ Found {len(scripts)} entry points:")
        for name, target in scripts.items():
            print(f"  {name} -> {target}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking entry points: {e}")
        return False

def check_dependencies():
    """Check dependencies are properly specified"""
    print("\n🔍 Checking dependencies...")
    
    try:
        import toml
        with open('pyproject.toml', 'r') as f:
            pyproject_data = toml.load(f)
        
        deps = pyproject_data.get('project', {}).get('dependencies', [])
        optional_deps = pyproject_data.get('project', {}).get('optional-dependencies', {})
        
        print(f"✅ Core dependencies: {len(deps)}")
        print(f"✅ Optional dependency groups: {len(optional_deps)}")
        
        for group, group_deps in optional_deps.items():
            print(f"  {group}: {len(group_deps)} packages")
        
        return True
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def check_no_dev_files():
    """Check that development files are not included"""
    print("\n🔍 Checking for development files...")
    
    dev_files = [
        'fix_critical_issues.py',
        'run_comprehensive_tests.py',
        'maahelper_test_results.json',
        'FINAL_ISSUE_SUMMARY.md',
        'MAAHELPER_COMPREHENSIVE_ISSUE_REPORT.md',
        '__pycache__',
        'htmlcov',
        '.pytest_cache',
        'build',
        '*.egg-info'
    ]
    
    found_dev_files = []
    for pattern in dev_files:
        if '*' in pattern:
            # Handle glob patterns
            import glob
            matches = glob.glob(pattern)
            found_dev_files.extend(matches)
        else:
            if os.path.exists(pattern):
                found_dev_files.append(pattern)
    
    if found_dev_files:
        print("⚠️  Found development files (should be cleaned):")
        for file in found_dev_files:
            print(f"  {file}")
        return False
    else:
        print("✅ No development files found")
        return True

def main():
    """Main validation function"""
    print("🔍 MaaHelper Deployment Validation")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('pyproject.toml'):
        print("❌ pyproject.toml not found. Run this script from the project root.")
        sys.exit(1)
    
    checks = [
        ("Package Structure", check_package_structure),
        ("Version Consistency", check_version_consistency),
        ("Package Imports", check_imports),
        ("Entry Points", check_entry_points),
        ("Dependencies", check_dependencies),
        ("Development Files", check_no_dev_files),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 All validation checks passed!")
        print("✅ Package is ready for deployment to PyPI")
        print("\nNext steps:")
        print("1. Run: python deploy.py")
        print("2. Choose deployment target (test/prod)")
        return True
    else:
        print(f"\n❌ {len(results) - passed} validation checks failed")
        print("Please fix the issues above before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
