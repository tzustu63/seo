#!/usr/bin/env python3
"""
Test script for Google Search Automation

Simple test to verify the automation system works correctly.
"""

import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from google_automation.utils import ConfigLoader, setup_logging
from google_automation.core import KeywordManager, URLManager, SearchAnalyzer


def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    try:
        config_loader = ConfigLoader("config.yaml")
        config = config_loader.load_config()
        
        print("✓ Configuration loaded successfully")
        print(f"  - Max pages: {config['general']['max_pages']}")
        print(f"  - Keywords: {len(config['keywords']['single_keywords'])}")
        print(f"  - Target URLs: {len(config['target_urls'])}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False


def test_keyword_manager():
    """Test keyword manager."""
    print("\nTesting keyword manager...")
    
    try:
        # Create test configuration
        test_config = {
            'keywords': {
                'single_keywords': [
                    {'keyword': 'test keyword 1', 'enabled': True, 'priority': 1},
                    {'keyword': 'test keyword 2', 'enabled': True, 'priority': 2}
                ]
            }
        }
        
        keyword_manager = KeywordManager(test_config['keywords'])
        
        # Test getting keywords
        keywords = keyword_manager.get_all_keywords()
        print(f"✓ Keyword manager initialized with {len(keywords)} keywords")
        
        # Test adding keyword
        keyword_manager.add_keyword("test keyword 3", priority=3)
        keywords = keyword_manager.get_all_keywords()
        print(f"✓ Added keyword, now have {len(keywords)} keywords")
        
        # Test statistics
        stats = keyword_manager.get_keyword_statistics()
        print(f"✓ Keyword statistics: {stats['total_keywords']} total, {stats['enabled_keywords']} enabled")
        
        return True
    except Exception as e:
        print(f"✗ Keyword manager test failed: {e}")
        return False


def test_url_manager():
    """Test URL manager."""
    print("\nTesting URL manager...")
    
    try:
        # Create test configuration
        test_urls = [
            "https://www.example1.com/",
            "https://www.example2.com/",
            {
                'url': 'https://www.example3.com/',
                'enabled': True,
                'priority': 1,
                'match_type': 'contains'
            }
        ]
        
        url_manager = URLManager(test_urls)
        
        # Test getting URLs
        urls = url_manager.get_all_urls()
        print(f"✓ URL manager initialized with {len(urls)} URLs")
        
        # Test adding URL
        url_manager.add_url("https://www.example4.com/", priority=2)
        urls = url_manager.get_all_urls()
        print(f"✓ Added URL, now have {len(urls)} URLs")
        
        # Test URL matching
        match_result = url_manager.match_url("https://www.example1.com/page", "https://www.example1.com/")
        print(f"✓ URL matching test: {match_result}")
        
        # Test statistics
        stats = url_manager.get_url_statistics()
        print(f"✓ URL statistics: {stats['total_urls']} total, {stats['enabled_urls']} enabled")
        
        return True
    except Exception as e:
        print(f"✗ URL manager test failed: {e}")
        return False


def test_search_analyzer():
    """Test search analyzer."""
    print("\nTesting search analyzer...")
    
    try:
        analyzer = SearchAnalyzer()
        
        # Test recording search results
        analyzer.record_search_result("test keyword", "https://www.example.com/", 1, True, 2.5)
        analyzer.record_search_result("test keyword", "https://www.example.com/", 0, False, 1.0, "Not found")
        
        # Test getting statistics
        stats = analyzer.get_statistics()
        print(f"✓ Search analyzer initialized")
        print(f"  - Total searches: {stats['session']['total_searches']}")
        print(f"  - Success rate: {stats['session']['overall_success_rate']:.2%}")
        
        # Test keyword performance
        keyword_stats = analyzer.get_keyword_performance("test keyword")
        if keyword_stats:
            print(f"  - Keyword success rate: {keyword_stats.success_rate:.2%}")
        
        return True
    except Exception as e:
        print(f"✗ Search analyzer test failed: {e}")
        return False


def test_logging():
    """Test logging system."""
    print("\nTesting logging system...")
    
    try:
        # Create test configuration
        test_config = {
            'logging': {
                'level': 'INFO',
                'file': 'logs/test.log',
                'console_output': True
            }
        }
        
        setup_logging(test_config)
        logger = logging.getLogger(__name__)
        
        logger.info("Test log message")
        logger.warning("Test warning message")
        
        print("✓ Logging system initialized and working")
        return True
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*50)
    print("GOOGLE SEARCH AUTOMATION - SYSTEM TEST")
    print("="*50)
    
    tests = [
        test_config_loading,
        test_keyword_manager,
        test_url_manager,
        test_search_analyzer,
        test_logging
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("="*50)
    
    if passed == total:
        print("🎉 All tests passed! The automation system is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
