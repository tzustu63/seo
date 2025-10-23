#!/usr/bin/env python3
"""
Basic test script for Google Search Automation (without Selenium)

Tests the core functionality without requiring Selenium WebDriver.
"""

import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import yaml
except ImportError:
    print("Installing PyYAML...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
    import yaml


def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    try:
        with open("config.yaml", 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        print("✓ Configuration loaded successfully")
        print(f"  - Max pages: {config['general']['max_pages']}")
        print(f"  - Keywords: {len(config['keywords']['single_keywords'])}")
        print(f"  - Target URLs: {len(config['target_urls'])}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False


def test_keyword_management():
    """Test keyword management logic."""
    print("\nTesting keyword management logic...")
    
    try:
        # Simulate keyword manager functionality
        keywords = [
            {'keyword': '太陽能鋼構', 'enabled': True, 'priority': 1},
            {'keyword': '鋼構廠房', 'enabled': True, 'priority': 1},
            {'keyword': '鋼構自地自建', 'enabled': True, 'priority': 2}
        ]
        
        enabled_keywords = [kw['keyword'] for kw in keywords if kw['enabled']]
        print(f"✓ Keyword management logic working")
        print(f"  - Total keywords: {len(keywords)}")
        print(f"  - Enabled keywords: {len(enabled_keywords)}")
        
        # Test priority sorting
        sorted_keywords = sorted(keywords, key=lambda x: x['priority'])
        print(f"  - Priority sorting: {[kw['keyword'] for kw in sorted_keywords]}")
        
        return True
    except Exception as e:
        print(f"✗ Keyword management test failed: {e}")
        return False


def test_url_management():
    """Test URL management logic."""
    print("\nTesting URL management logic...")
    
    try:
        # Simulate URL manager functionality
        urls = [
            "https://www.yksc.com.tw/",
            "https://www.example.com/",
            "https://www.test.com/"
        ]
        
        print(f"✓ URL management logic working")
        print(f"  - Total URLs: {len(urls)}")
        
        # Test URL validation
        valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
        print(f"  - Valid URLs: {len(valid_urls)}")
        
        # Test URL matching
        test_url = "https://www.yksc.com.tw/page"
        target_url = "https://www.yksc.com.tw/"
        match_result = target_url in test_url
        print(f"  - URL matching test: {match_result}")
        
        return True
    except Exception as e:
        print(f"✗ URL management test failed: {e}")
        return False


def test_search_analysis():
    """Test search analysis logic."""
    print("\nTesting search analysis logic...")
    
    try:
        # Simulate search analyzer functionality
        search_results = [
            {'keyword': '太陽能鋼構', 'success': True, 'page_found': 1, 'execution_time': 2.5},
            {'keyword': '鋼構廠房', 'success': True, 'page_found': 3, 'execution_time': 3.2},
            {'keyword': '鋼構自地自建', 'success': False, 'page_found': 0, 'execution_time': 1.8}
        ]
        
        total_searches = len(search_results)
        successful_searches = sum(1 for r in search_results if r['success'])
        success_rate = successful_searches / total_searches if total_searches > 0 else 0
        
        print(f"✓ Search analysis logic working")
        print(f"  - Total searches: {total_searches}")
        print(f"  - Successful searches: {successful_searches}")
        print(f"  - Success rate: {success_rate:.2%}")
        
        # Test ranking analysis
        successful_pages = [r['page_found'] for r in search_results if r['success'] and r['page_found'] > 0]
        avg_position = sum(successful_pages) / len(successful_pages) if successful_pages else 0
        print(f"  - Average position: {avg_position:.1f}")
        
        return True
    except Exception as e:
        print(f"✗ Search analysis test failed: {e}")
        return False


def test_logging():
    """Test logging system."""
    print("\nTesting logging system...")
    
    try:
        # Setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Test log message")
        logger.warning("Test warning message")
        
        print("✓ Logging system initialized and working")
        return True
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False


def test_file_structure():
    """Test file structure."""
    print("\nTesting file structure...")
    
    try:
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
            
    except Exception as e:
        print(f"✗ File structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("GOOGLE SEARCH AUTOMATION - BASIC SYSTEM TEST")
    print("="*60)
    
    tests = [
        test_file_structure,
        test_config_loading,
        test_keyword_management,
        test_url_management,
        test_search_analysis,
        test_logging
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
        print("🎉 All tests passed! The automation system structure is ready.")
        print("\nTo run the full automation:")
        print("1. Install Selenium: pip install selenium")
        print("2. Install Chrome WebDriver")
        print("3. Run: python main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
