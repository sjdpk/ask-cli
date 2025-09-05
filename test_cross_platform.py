#!/usr/bin/env python3
"""
Cross-platform test script for Ask CLI
Tests basic functionality across different platforms
"""

import os
import sys
import platform
import tempfile
import subprocess
from pathlib import Path

def test_platform_detection():
    """Test platform detection"""
    print("🧪 Testing platform detection...")
    
    # Add src to path for testing
    script_dir = Path(__file__).parent.resolve()
    src_dir = script_dir / "src"
    sys.path.insert(0, str(src_dir))
    
    try:
        from config import get_os_name, get_install_dir, get_executable_path
        
        os_name = get_os_name()
        install_dir = get_install_dir()
        exec_path = get_executable_path()
        
        print(f"   ✓ OS Name: {os_name}")
        print(f"   ✓ Install Dir: {install_dir}")
        print(f"   ✓ Executable Path: {exec_path}")
        
        # Verify paths make sense for platform
        system = platform.system().lower()
        if system == 'windows':
            assert 'AppData' in str(install_dir)
            assert 'ask.bat' in str(exec_path)
        else:
            assert '.local' in str(install_dir)
            assert 'ask' in str(exec_path)
        
        return True
    except Exception as e:
        print(f"   ❌ Platform detection failed: {e}")
        return False

def test_ai_prompt_generation():
    """Test AI prompt generation for different platforms"""
    print("🧪 Testing AI prompt generation...")
    
    try:
        from ai import CommandGenerator
        
        # Mock API key for testing
        generator = CommandGenerator("test-key")
        
        # Test prompt building
        prompt = generator._build_prompt("testuser", "list files")
        
        print(f"   ✓ Generated prompt for {generator.os_name}")
        
        # Check if platform-specific commands are included
        system = platform.system().lower()
        if system == 'windows':
            assert 'dir' in prompt
        else:
            assert 'ls -la' in prompt
        
        return True
    except Exception as e:
        print(f"   ❌ AI prompt generation failed: {e}")
        return False

def test_config_file_paths():
    """Test configuration file handling"""
    print("🧪 Testing configuration file paths...")
    
    try:
        from config import CONFIG_FILE, save_api_key, load_api_key
        
        print(f"   ✓ Config file path: {CONFIG_FILE}")
        
        # Test saving and loading (with temp key)
        test_key = "test-api-key-12345"
        save_api_key(test_key)
        loaded_key = load_api_key()
        
        if loaded_key == test_key:
            print("   ✓ Config save/load works")
            # Clean up
            CONFIG_FILE.unlink()
            return True
        else:
            print("   ❌ Config save/load mismatch")
            return False
            
    except Exception as e:
        print(f"   ❌ Config file test failed: {e}")
        return False

def test_python_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing Python imports...")
    
    required_modules = [
        'json', 'os', 'sys', 'platform', 'pathlib',
        'subprocess', 'tempfile', 'shutil', 'time',
        'threading', 'getpass'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✓ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"   ❌ Failed imports: {failed_imports}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Ask CLI Cross-Platform Test Suite")
    print("=" * 40)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    tests = [
        test_python_imports,
        test_platform_detection,
        test_ai_prompt_generation,
        test_config_file_paths,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Cross-platform support is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
