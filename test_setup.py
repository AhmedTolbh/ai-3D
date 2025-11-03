"""
Test script for Virtual Receptionist Avatar
============================================
This script tests the basic setup without requiring API keys
"""

import sys
import os

def test_python_version():
    """Test if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version OK:", sys.version.split()[0])
        return True
    else:
        print("✗ Python version too old. Need 3.8+, got:", sys.version.split()[0])
        return False

def test_imports():
    """Test if all required modules can be imported"""
    modules = [
        'flask',
        'flask_cors',
        'dotenv',
        'google.cloud.speech',
        'google.cloud.texttospeech',
        'google.generativeai',
        'requests'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError:
            print(f"✗ {module} not found")
            all_ok = False
    
    return all_ok

def test_file_structure():
    """Test if all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'static/index.html',
        'static/app.js'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            all_ok = False
    
    return all_ok

def test_directories():
    """Test if required directories exist"""
    required_dirs = [
        'static',
        'static/audio',
        'static/video'
    ]
    
    all_ok = True
    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"✓ {dir}/ exists")
        else:
            print(f"✗ {dir}/ missing")
            all_ok = False
    
    return all_ok

def test_env_file():
    """Test if .env file is configured"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found - you need to create it from .env.example")
        return False
    
    print("✓ .env file exists")
    
    # Check if it has required variables (not empty)
    with open('.env', 'r') as f:
        content = f.read()
        
    required_vars = [
        'GEMINI_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'DID_API_KEY'
    ]
    
    for var in required_vars:
        if var in content and not f'{var}=your_' in content:
            print(f"✓ {var} appears to be configured")
        else:
            print(f"⚠️  {var} needs to be configured in .env")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Virtual Receptionist Avatar - Setup Test")
    print("=" * 60)
    print()
    
    tests = [
        ("Python Version", test_python_version),
        ("File Structure", test_file_structure),
        ("Directories", test_directories),
    ]
    
    # Run basic tests first
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 40)
        result = test_func()
        results.append(result)
    
    # Test imports (requires dependencies installed)
    print(f"\nPython Imports:")
    print("-" * 40)
    try:
        import_result = test_imports()
        results.append(import_result)
    except Exception as e:
        print(f"⚠️  Could not test imports: {e}")
        print("   Run: pip install -r requirements.txt")
    
    # Test env file
    print(f"\nEnvironment Configuration:")
    print("-" * 40)
    test_env_file()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    if all(results):
        print("✓ All tests passed!")
        print("\nYou can start the server with:")
        print("  python app.py")
        print("\nOr use the quick start script:")
        print("  ./start.sh (Linux/Mac)")
        print("  start.bat (Windows)")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
