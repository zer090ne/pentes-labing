#!/usr/bin/env python3
"""
Script untuk check Python version dan recommend requirements file
"""

import sys
import platform

def check_python_version():
    """Check Python version and recommend requirements file"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    
    if version.major == 3 and version.minor == 13:
        print("⚠️  Python 3.13 detected - using SQLite database")
        print("📦 Recommended requirements: requirements-python313.txt")
        return "requirements-python313.txt"
    elif version.major == 3 and version.minor >= 11:
        print("✅ Python 3.11+ detected - full features available")
        print("📦 Recommended requirements: requirements.txt")
        return "requirements.txt"
    else:
        print("⚠️  Older Python version detected - using minimal setup")
        print("📦 Recommended requirements: requirements-minimal.txt")
        return "requirements-minimal.txt"

def main():
    """Main function"""
    print("🔍 Checking Python environment...")
    recommended_file = check_python_version()
    
    print(f"\n🚀 To install dependencies, run:")
    print(f"pip install -r {recommended_file}")
    
    if recommended_file == "requirements-python313.txt":
        print("\n💡 Note: Using SQLite database for Python 3.13 compatibility")
        print("   You can switch to PostgreSQL later if needed")

if __name__ == "__main__":
    main()