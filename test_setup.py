#!/usr/bin/env python3
"""
Test script to verify the Flask + React setup is working correctly.
"""

import os
import sys
import subprocess
import requests
import time

def test_python_dependencies():
    """Test if all Python dependencies can be imported."""
    print("🔍 Testing Python dependencies...")
    
    required_modules = [
        'flask', 'flask_cors', 'openai', 'dotenv', 
        'PyPDF2', 'docx', 'pandas', 'werkzeug'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'flask_cors':
                __import__('flask_cors')
            elif module == 'dotenv':
                __import__('dotenv')
            elif module == 'PyPDF2':
                __import__('PyPDF2')
            elif module == 'docx':
                __import__('docx')
            else:
                __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("Run: pip install -r backend/requirements.txt")
        return False
    
    print("✅ All Python dependencies are available!")
    return True

def test_custom_modules():
    """Test if custom modules can be imported."""
    print("\n🔍 Testing custom modules...")
    
    try:
        from jd_analyzer import analyze_job_description
        print("  ✅ jd_analyzer")
    except ImportError as e:
        print(f"  ❌ jd_analyzer: {e}")
        return False
    
    try:
        from resume_analyzer import analyze_resume
        print("  ✅ resume_analyzer")
    except ImportError as e:
        print(f"  ❌ resume_analyzer: {e}")
        return False
    
    print("✅ All custom modules are available!")
    return True

def test_backend_startup():
    """Test if the backend can start (without actually starting it)."""
    print("\n🔍 Testing backend configuration...")
    
    backend_path = os.path.join(os.getcwd(), 'backend', 'app.py')
    if not os.path.exists(backend_path):
        print(f"❌ Backend file not found: {backend_path}")
        return False
    
    print(f"  ✅ Backend file exists: {backend_path}")
    
    # Test syntax by trying to compile
    try:
        with open(backend_path, 'r') as f:
            code = f.read()
        compile(code, backend_path, 'exec')
        print("  ✅ Backend syntax is valid")
    except SyntaxError as e:
        print(f"  ❌ Backend syntax error: {e}")
        return False
    
    print("✅ Backend configuration looks good!")
    return True

def test_frontend_setup():
    """Test if frontend setup exists."""
    print("\n🔍 Testing frontend setup...")
    
    frontend_path = os.path.join(os.getcwd(), 'frontend')
    if not os.path.exists(frontend_path):
        print(f"❌ Frontend directory not found: {frontend_path}")
        return False
    
    package_json = os.path.join(frontend_path, 'package.json')
    if not os.path.exists(package_json):
        print(f"❌ package.json not found: {package_json}")
        return False
    
    print(f"  ✅ Frontend directory exists: {frontend_path}")
    print(f"  ✅ package.json exists: {package_json}")
    
    # Check if Node.js is available
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Node.js version: {result.stdout.strip()}")
        else:
            print("  ❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("  ❌ Node.js not found")
        return False
    
    print("✅ Frontend setup looks good!")
    return True

def test_env_file():
    """Test if .env file exists and has API key."""
    print("\n🔍 Testing .env configuration...")
    
    env_file = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_file):
        print(f"  ❌ .env file not found: {env_file}")
        print(f"  💡 Copy env.example to .env and add your API key")
        return False
    
    print(f"  ✅ .env file exists: {env_file}")
    
    # Check if .env has OPENAI_API_KEY
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'OPENAI_API_KEY=' in content and 'your_openai_api_key_here' not in content:
            print("  ✅ OPENAI_API_KEY found in .env")
        elif 'OPENAI_API_KEY=' in content:
            print("  ⚠️  OPENAI_API_KEY found but appears to be placeholder")
            print("  💡 Please replace with your actual OpenAI API key")
            return False
        else:
            print("  ❌ OPENAI_API_KEY not found in .env")
            return False
    except Exception as e:
        print(f"  ❌ Error reading .env file: {e}")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def main():
    """Run all tests."""
    print("🧪 Resume Analyzer Setup Test\n")
    print("="*50)
    
    tests = [
        test_python_dependencies,
        test_custom_modules,
        test_backend_startup,
        test_frontend_setup,
        test_env_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application:")
        print("   ./start.sh")
        print("\n🌐 Application will run on:")
        print("   http://localhost:8008")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        if not os.path.exists('.env'):
            print("\n💡 Quick fix: Copy env.example to .env and add your API key")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 