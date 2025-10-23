#!/usr/bin/env python3
"""
Google Search Automation Main Script

Main entry point for the Google Search Automation system.
"""

import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from google_automation import GoogleSearchAutomation
from google_automation.utils import ConfigLoader, setup_logging


def main():
    """Main execution function."""
    try:
        # Load configuration
        config_loader = ConfigLoader("config.yaml")
        config = config_loader.load_config()
        
        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Google Search Automation")
        
        # Initialize automation system
        automation = GoogleSearchAutomation(config)
        
        # Run automation cycle
        logger.info("Running automation cycle...")
        results = automation.run_automation_cycle()
        
        # Log results
        successful_searches = sum(1 for r in results if r['success'])
        total_searches = len(results)
        
        logger.info(f"Automation cycle completed: {successful_searches}/{total_searches} successful")
        
        # Get and log statistics
        stats = automation.get_search_statistics()
        logger.info(f"Session statistics: {stats}")
        
        # Print summary
        print("\n" + "="*50)
        print("GOOGLE SEARCH AUTOMATION SUMMARY")
        print("="*50)
        print(f"Total searches: {total_searches}")
        print(f"Successful searches: {successful_searches}")
        print(f"Success rate: {successful_searches/total_searches*100:.1f}%" if total_searches > 0 else "N/A")
        
        if results:
            print("\nDetailed Results:")
            for i, result in enumerate(results, 1):
                status = "✓" if result['success'] else "✗"
                page_info = f" (page {result['page_found']})" if result['success'] and result['page_found'] > 0 else ""
                print(f"  {i}. {status} {result['keyword']} -> {result['target_url']}{page_info}")
        
        print("="*50)
        
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        print("\nAutomation interrupted by user")
        
    except Exception as e:
        logger.error(f"Automation failed: {e}", exc_info=True)
        print(f"\nAutomation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
