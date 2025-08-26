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
    """Run a shell command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result

def clean_build_artifacts():
    """Clean up build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = [
        "build",
        "dist", 
        "*.egg-info",
        "__pycache__"
    ]
    
    for artifact in artifacts:
        if "*" in artifact:
            # Use shell expansion for wildcards
            run_command(f"rm -rf {artifact}", check=False)
        else:
            if os.path.exists(artifact):
                if os.path.isdir(artifact):
                    shutil.rmtree(artifact)
                else:
                    os.remove(artifact)
                print(f"  Removed: {artifact}")

def validate_package():
    """Validate package structure and metadata"""
    print("✅ Validating package...")
    
    # Check required files
    required_files = [
        "README.md",
        "LICENSE", 
        "pyproject.toml",
        "requirements.txt",
        "CHANGELOG.md",
        "CONTRIBUTING.md"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            sys.exit(1)
        print(f"  ✓ {file}")
    
    # Check package structure
    if not os.path.exists("maahelper/__init__.py"):
        print("❌ Missing maahelper/__init__.py")
        sys.exit(1)
    
    print("✅ Package structure validated")

def build_package():
    """Build the package"""
    print("📦 Building package...")
    
    # Build source distribution and wheel
    run_command("python -m build")
    
    print("✅ Package built successfully")

def check_package():
    """Check package with twine"""
    print("🔍 Checking package with twine...")
    
    run_command("python -m twine check dist/*")
    
    print("✅ Package check passed")

def upload_to_test_pypi():
    """Upload to Test PyPI"""
    print("🚀 Uploading to Test PyPI...")
    
    run_command("python -m twine upload --repository testpypi dist/*")
    
    print("✅ Uploaded to Test PyPI")

def upload_to_pypi():
    """Upload to PyPI"""
    print("🚀 Uploading to PyPI...")
    
    confirm = input("Are you sure you want to upload to PyPI? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Upload cancelled")
        sys.exit(1)
    
    run_command("python -m twine upload dist/*")
    
    print("🎉 Successfully uploaded to PyPI!")

def main():
    """Main deployment function"""
    print("🚀 MaaHelper Deployment Script")
    print("=" * 40)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)
    
    # Check if we're in the right directory
    if not os.path.exists("maahelper"):
        print("❌ Not in the correct directory. Please run from the package root.")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        print("Available actions:")
        print("  clean    - Clean build artifacts")
        print("  build    - Build package")
        print("  check    - Check package")
        print("  test     - Upload to Test PyPI")
        print("  deploy   - Upload to PyPI")
        print("  all      - Run complete deployment pipeline")
        action = input("Choose action: ").strip()
    
    if action == "clean":
        clean_build_artifacts()
    elif action == "build":
        validate_package()
        clean_build_artifacts()
        build_package()
    elif action == "check":
        check_package()
    elif action == "test":
        upload_to_test_pypi()
    elif action == "deploy":
        upload_to_pypi()
    elif action == "all":
        validate_package()
        clean_build_artifacts()
        build_package()
        check_package()
        
        test_upload = input("Upload to Test PyPI first? (y/n): ")
        if test_upload.lower() == "y":
            upload_to_test_pypi()
            
            proceed = input("Test successful? Proceed to PyPI? (y/n): ")
            if proceed.lower() == "y":
                upload_to_pypi()
        else:
            upload_to_pypi()
    else:
        print(f"❌ Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
