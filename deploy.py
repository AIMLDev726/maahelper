#!/usr/bin/env python3
"""
MaaHelper Deployment Script
Automates the process of building and deploying to PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    # Remove build directories
    for dir_name in ['build', 'dist', 'maahelper.egg-info']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)
    
    print("✅ Build artifacts cleaned")

def validate_package():
    """Validate package structure and dependencies"""
    print("🔍 Validating package...")
    
    # Check required files exist
    required_files = [
        'pyproject.toml',
        'README.md',
        'LICENSE',
        'maahelper/__init__.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing required file: {file_path}")
            sys.exit(1)
    
    # Check version consistency
    import toml
    with open('pyproject.toml', 'r') as f:
        pyproject_data = toml.load(f)
    
    pyproject_version = pyproject_data['project']['version']
    
    # Read version from __init__.py
    init_file = Path('maahelper/__init__.py')
    init_content = init_file.read_text()
    for line in init_content.split('\n'):
        if line.startswith('__version__'):
            init_version = line.split('=')[1].strip().strip('"\'')
            break
    else:
        print("❌ Could not find __version__ in maahelper/__init__.py")
        sys.exit(1)
    
    if pyproject_version != init_version:
        print(f"❌ Version mismatch: pyproject.toml={pyproject_version}, __init__.py={init_version}")
        sys.exit(1)
    
    print(f"✅ Package validation passed (version: {pyproject_version})")
    return pyproject_version

def build_package():
    """Build the package"""
    print("📦 Building package...")
    
    # Install build dependencies
    run_command("pip install --upgrade build twine")
    
    # Build the package
    run_command("python -m build")
    
    print("✅ Package built successfully")

def check_package():
    """Check the built package"""
    print("🔍 Checking built package...")
    
    # Check with twine
    run_command("twine check dist/*")
    
    print("✅ Package check passed")

def upload_to_testpypi():
    """Upload to Test PyPI"""
    print("🚀 Uploading to Test PyPI...")
    
    # Upload to Test PyPI
    run_command("twine upload --repository testpypi dist/*")
    
    print("✅ Uploaded to Test PyPI")

def upload_to_pypi():
    """Upload to PyPI"""
    print("🚀 Uploading to PyPI...")
    
    # Upload to PyPI
    run_command("twine upload dist/*")
    
    print("✅ Uploaded to PyPI")

def main():
    """Main deployment function"""
    print("🚀 MaaHelper Deployment Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('pyproject.toml'):
        print("❌ pyproject.toml not found. Run this script from the project root.")
        sys.exit(1)
    
    # Get deployment target
    target = input("Deploy to (test/prod/both): ").lower().strip()
    if target not in ['test', 'prod', 'both']:
        print("❌ Invalid target. Choose 'test', 'prod', or 'both'")
        sys.exit(1)
    
    try:
        # Step 1: Clean
        clean_build()
        
        # Step 2: Validate
        version = validate_package()
        
        # Step 3: Build
        build_package()
        
        # Step 4: Check
        check_package()
        
        # Step 5: Upload
        if target in ['test', 'both']:
            upload_to_testpypi()
            print(f"\n🎉 Test deployment complete!")
            print(f"Install with: pip install -i https://test.pypi.org/simple/ maahelper=={version}")
        
        if target in ['prod', 'both']:
            if target == 'both':
                confirm = input("\nProceed with production deployment? (y/N): ")
                if confirm.lower() != 'y':
                    print("Production deployment cancelled")
                    return
            
            upload_to_pypi()
            print(f"\n🎉 Production deployment complete!")
            print(f"Install with: pip install maahelper=={version}")
        
        print("\n✅ Deployment successful!")
        
    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
