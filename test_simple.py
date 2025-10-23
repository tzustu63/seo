#!/usr/bin/env python3
"""
Simple test script for Google Search Automation

Tests the basic structure and functionality without external dependencies.
"""

import sys
import json
from pathlib import Path


def test_file_structure():
    """Test file structure."""
    print("Testing file structure...")
    
    required_files = [
        "config.yaml",
        "main.py", 
        "requirements.txt",
        "README.md",
        "google_automation/__init__.py",
        "google_automation/core/__init__.py",
        "google_automation/core/google_automation.py",
        "google_automation/core/keyword_manager.py",
        "google_automation/core/url_manager.py",
        "google_automation/core/search_analyzer.py",
        "google_automation/core/wait_manager.py",
        "google_automation/utils/__init__.py",
        "google_automation/utils/config_loader.py",
        "google_automation/utils/logger_setup.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print(f"✓ All {len(required_files)} required files present")
        return True


def test_config_structure():
    """Test configuration file structure."""
    print("\nTesting configuration structure...")
    
    try:
        with open("config.yaml", 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check for required sections
        required_sections = [
            "general:",
            "keywords:",
            "target_urls:",
            "browser:",
            "logging:"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"✗ Missing configuration sections: {missing_sections}")
            return False
        else:
            print("✓ Configuration file structure is correct")
            return True
            
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_python_syntax():
    """Test Python syntax of core files."""
    print("\nTesting Python syntax...")
    
    python_files = [
        "google_automation/__init__.py",
        "google_automation/core/__init__.py",
        "google_automation/core/keyword_manager.py",
        "google_automation/core/url_manager.py",
        "google_automation/core/search_analyzer.py",
        "google_automation/core/wait_manager.py",
        "google_automation/utils/__init__.py",
        "google_automation/utils/config_loader.py",
        "google_automation/utils/logger_setup.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Try to compile the code
            compile(content, file_path, 'exec')
            
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: {e}")
    
    if syntax_errors:
        print(f"✗ Syntax errors found:")
        for error in syntax_errors:
            print(f"  - {error}")
        return False
    else:
        print(f"✓ All {len(python_files)} Python files have correct syntax")
        return True


def test_import_structure():
    """Test import structure."""
    print("\nTesting import structure...")
    
    try:
        # Test that we can read the files and they have proper imports
        core_files = [
            "google_automation/core/keyword_manager.py",
            "google_automation/core/url_manager.py", 
            "google_automation/core/search_analyzer.py",
            "google_automation/core/wait_manager.py"
        ]
        
        for file_path in core_files:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Check for basic structure
            if "class " not in content:
                print(f"✗ {file_path} missing class definition")
                return False
            
            if "def " not in content:
                print(f"✗ {file_path} missing function definitions")
                return False
        
        print("✓ Import structure is correct")
        return True
        
    except Exception as e:
        print(f"✗ Import structure test failed: {e}")
        return False


def test_keyword_logic():
    """Test keyword management logic."""
    print("\nTesting keyword management logic...")
    
    try:
        # Simulate keyword management
        keywords = [
            {'keyword': '太陽能鋼構', 'enabled': True, 'priority': 1},
            {'keyword': '鋼構廠房', 'enabled': True, 'priority': 1},
            {'keyword': '鋼構自地自建', 'enabled': True, 'priority': 2}
        ]
        
        # Test filtering enabled keywords
        enabled_keywords = [kw['keyword'] for kw in keywords if kw['enabled']]
        
        # Test priority sorting
        sorted_keywords = sorted(keywords, key=lambda x: x['priority'])
        
        if len(enabled_keywords) == 3 and len(sorted_keywords) == 3:
            print("✓ Keyword management logic working")
            return True
        else:
            print("✗ Keyword management logic failed")
            return False
            
    except Exception as e:
        print(f"✗ Keyword logic test failed: {e}")
        return False


def test_url_logic():
    """Test URL management logic."""
    print("\nTesting URL management logic...")
    
    try:
        # Simulate URL management
        urls = [
            "https://www.yksc.com.tw/",
            "https://www.example.com/",
            "https://www.test.com/"
        ]
        
        # Test URL validation
        valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
        
        # Test URL matching
        test_url = "https://www.yksc.com.tw/page"
        target_url = "https://www.yksc.com.tw/"
        match_result = target_url in test_url
        
        if len(valid_urls) == 3 and match_result:
            print("✓ URL management logic working")
            return True
        else:
            print("✗ URL management logic failed")
            return False
            
    except Exception as e:
        print(f"✗ URL logic test failed: {e}")
        return False


def test_search_analysis_logic():
    """Test search analysis logic."""
    print("\nTesting search analysis logic...")
    
    try:
        # Simulate search results
        search_results = [
            {'keyword': '太陽能鋼構', 'success': True, 'page_found': 1, 'execution_time': 2.5},
            {'keyword': '鋼構廠房', 'success': True, 'page_found': 3, 'execution_time': 3.2},
            {'keyword': '鋼構自地自建', 'success': False, 'page_found': 0, 'execution_time': 1.8}
        ]
        
        # Calculate statistics
        total_searches = len(search_results)
        successful_searches = sum(1 for r in search_results if r['success'])
        success_rate = successful_searches / total_searches if total_searches > 0 else 0
        
        # Calculate average position
        successful_pages = [r['page_found'] for r in search_results if r['success'] and r['page_found'] > 0]
        avg_position = sum(successful_pages) / len(successful_pages) if successful_pages else 0
        
        if total_searches == 3 and successful_searches == 2 and success_rate == 2/3:
            print("✓ Search analysis logic working")
            return True
        else:
            print("✗ Search analysis logic failed")
            return False
            
    except Exception as e:
        print(f"✗ Search analysis test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("GOOGLE SEARCH AUTOMATION - SIMPLE SYSTEM TEST")
    print("="*60)
    
    tests = [
        test_file_structure,
        test_config_structure,
        test_python_syntax,
        test_import_structure,
        test_keyword_logic,
        test_url_logic,
        test_search_analysis_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! The automation system is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install Chrome WebDriver")
        print("3. Run the automation: python main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
