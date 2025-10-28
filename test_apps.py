#!/usr/bin/env python3
"""
Test script to verify desktop apps are working correctly
"""

import sys

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import streamlit
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import PyQt5
        print("✅ PyQt5 imported successfully")
    except ImportError as e:
        print(f"❌ PyQt5 import failed: {e}")
        return False
    
    try:
        import flask_socketio
        print("✅ flask-socketio imported successfully")
    except ImportError as e:
        print(f"❌ flask-socketio import failed: {e}")
        return False
    
    try:
        import flask_cors
        print("✅ flask-cors imported successfully")
    except ImportError as e:
        print(f"❌ flask-cors import failed: {e}")
        return False
    
    try:
        import nltk
        print("✅ nltk imported successfully")
    except ImportError as e:
        print(f"❌ nltk import failed: {e}")
        return False
    
    return True

def test_app_imports():
    """Test that desktop apps can be imported"""
    print("\nTesting desktop app imports...")
    
    try:
        import desktop_app_pyqt5
        print("✅ desktop_app_pyqt5.py imported successfully")
        
        # Verify main components exist
        assert hasattr(desktop_app_pyqt5, 'JarvisMainWindow'), "JarvisMainWindow class not found"
        assert hasattr(desktop_app_pyqt5, 'main'), "main function not found"
        print("  ✓ JarvisMainWindow class found")
        print("  ✓ main function found")
    except Exception as e:
        print(f"❌ desktop_app_pyqt5.py import failed: {e}")
        return False
    
    try:
        import desktop_app_streamlit
        print("✅ desktop_app_streamlit.py imported successfully")
    except Exception as e:
        print(f"❌ desktop_app_streamlit.py import failed: {e}")
        return False
    
    return True

def test_syntax():
    """Test for syntax errors"""
    print("\nTesting for syntax errors...")
    
    import py_compile
    
    try:
        py_compile.compile('desktop_app_pyqt5.py', doraise=True)
        print("✅ desktop_app_pyqt5.py has no syntax errors")
    except py_compile.PyCompileError as e:
        print(f"❌ desktop_app_pyqt5.py has syntax errors: {e}")
        return False
    
    try:
        py_compile.compile('desktop_app_streamlit.py', doraise=True)
        print("✅ desktop_app_streamlit.py has no syntax errors")
    except py_compile.PyCompileError as e:
        print(f"❌ desktop_app_streamlit.py has syntax errors: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("JARVIS AI Agent v1.4 - Desktop Apps Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("Syntax Check", test_syntax()))
    results.append(("App Imports", test_app_imports()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All tests passed! Desktop apps are ready to use.")
        print("\nTo run the apps:")
        print("  Streamlit: streamlit run desktop_app_streamlit.py")
        print("  PyQt5:     python3 desktop_app_pyqt5.py")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
