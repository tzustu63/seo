"""
Google Search Automation Core Class

Main automation class that orchestrates Google search and web page clicking.
"""

import time
import random
import logging
from typing import List, Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .keyword_manager import KeywordManager
from .url_manager import URLManager
from .search_analyzer import SearchAnalyzer


class GoogleSearchAutomation:
    """
    Core class for Google search automation.
    
    Provides functionality to:
    - Execute automated Google searches
    - Click on target URLs in search results
    - Handle multi-page search navigation
    - Manage search strategies and configurations
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Google Search Automation.
        
        Args:
            config: Configuration dictionary containing automation settings
        """
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.keyword_manager = KeywordManager(config.get('keywords', {}))
        self.url_manager = URLManager(config.get('target_urls', []))
        self.search_analyzer = SearchAnalyzer()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.max_pages = config.get('max_pages', 10)
        self.wait_timeout = config.get('wait_timeout', 10)
        self.min_delay = config.get('min_delay', 2)
        self.max_delay = config.get('max_delay', 5)
        self.page_delay = config.get('page_delay', (20, 30))
        
    def start_browser(self) -> None:
        """Initialize and start Chrome browser."""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Browser started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise
    
    def close_browser(self) -> None:
        """Close browser and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
    
    def search_keyword(self, keyword: str) -> bool:
        """
        Execute Google search for a specific keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            bool: True if search executed successfully, False otherwise
        """
        try:
            self.logger.info(f"Starting search for keyword: {keyword}")
            
            # Navigate to Google
            self.driver.get("https://www.google.com.tw")
            
            # Wait for search box and enter keyword
            search_box = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.submit()
            
            # Wait for search results
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.logger.info(f"Search completed for keyword: {keyword}")
            return True
            
        except TimeoutException:
            self.logger.error(f"Timeout during search for keyword: {keyword}")
            return False
        except Exception as e:
            self.logger.error(f"Error during search for keyword {keyword}: {e}")
            return False
    
    def find_and_click_target_url(self, target_url: str) -> Tuple[bool, int]:
        """
        Find and click target URL in search results.
        
        Args:
            target_url: Target URL to find and click
            
        Returns:
            Tuple[bool, int]: (success, page_number)
        """
        import re
        
        for page in range(self.max_pages):
            try:
                # Wait for page to load
                WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get all links on the page
                links = self.driver.find_elements(By.TAG_NAME, "a")
                
                # Check each link against target URL using URL manager's matching logic
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and self.url_manager.match_url(href, target_url):
                            # Click the matching link
                            link.click()
                            self.logger.info(f"Successfully clicked target URL on page {page + 1}: {href}")
                            return True, page + 1
                    except Exception as e:
                        self.logger.debug(f"Error checking link: {e}")
                        continue
                
                # Try to go to next page if not found
                if page < self.max_pages - 1:
                    try:
                        next_button = self.driver.find_element(By.LINK_TEXT, "下一頁")
                        next_button.click()
                        self._random_delay()
                    except NoSuchElementException:
                        self.logger.warning(f"No 'next page' button found on page {page + 1}")
                        break
                        
            except Exception as e:
                self.logger.error(f"Error on page {page + 1}: {e}")
                break
        
        self.logger.warning(f"Target URL not found in {self.max_pages} pages")
        return False, 0
    
    def execute_search_task(self, keyword: str, target_url: str) -> Dict:
        """
        Execute complete search task for a keyword and target URL.
        
        Args:
            keyword: Search keyword
            target_url: Target URL to find and click
            
        Returns:
            Dict: Task execution result with statistics
        """
        start_time = time.time()
        result = {
            'keyword': keyword,
            'target_url': target_url,
            'success': False,
            'page_found': 0,
            'execution_time': 0,
            'error': None
        }
        
        try:
            # Execute search
            if not self.search_keyword(keyword):
                result['error'] = 'Search failed'
                return result
            
            # Find and click target URL
            success, page_found = self.find_and_click_target_url(target_url)
            result['success'] = success
            result['page_found'] = page_found
            
            if success:
                # Wait on target page
                self._random_delay(self.page_delay[0], self.page_delay[1])
                
                # Record search result
                self.search_analyzer.record_search_result(keyword, target_url, page_found, True)
            else:
                self.search_analyzer.record_search_result(keyword, target_url, 0, False)
                
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error in search task for {keyword}: {e}")
            
        finally:
            result['execution_time'] = time.time() - start_time
            
        return result
    
    def run_automation_cycle(self) -> List[Dict]:
        """
        Run complete automation cycle with optional random keyword selection.
        
        Returns:
            List[Dict]: Results for all search tasks
        """
        import random
        
        results = []
        
        try:
            self.start_browser()
            
            keywords = self.keyword_manager.get_all_keywords()
            target_urls = self.url_manager.get_all_urls()
            
            # 檢查是否啟用隨機執行
            random_config = self.config.get('general', {}).get('random_execution', {})
            if random_config.get('enabled', False):
                total_iterations = random_config.get('total_iterations', 500)
                random_keyword = random_config.get('random_keyword_selection', True)
                random_url = random_config.get('random_url_selection', True)
                min_delay = random_config.get('min_delay_between_iterations', 5)
                max_delay = random_config.get('max_delay_between_iterations', 15)
                
                self.logger.info(f"Starting random execution: {total_iterations} iterations")
                
                for i in range(total_iterations):
                    # 隨機選擇關鍵字
                    if random_keyword and keywords:
                        keyword = random.choice(keywords)
                    else:
                        keyword = keywords[i % len(keywords)] if keywords else None
                    
                    # 隨機選擇目標網址
                    if random_url and target_urls:
                        target_url = random.choice(target_urls)
                    else:
                        target_url = target_urls[i % len(target_urls)] if target_urls else None
                    
                    if keyword and target_url:
                        self.logger.info(f"Executing task {i+1}/{total_iterations}: {keyword} -> {target_url}")
                        
                        result = self.execute_search_task(keyword, target_url)
                        results.append(result)
                        
                        # 隨機延遲
                        if i < total_iterations - 1:  # 最後一次不需要延遲
                            delay = random.uniform(min_delay, max_delay)
                            self.logger.info(f"Waiting {delay:.1f} seconds before next iteration...")
                            time.sleep(delay)
            else:
                # 原有的順序執行邏輯
                self.logger.info("Running sequential execution mode")
                for keyword in keywords:
                    for target_url in target_urls:
                        self.logger.info(f"Executing task: {keyword} -> {target_url}")
                        
                        result = self.execute_search_task(keyword, target_url)
                        results.append(result)
                        
                        # Random delay between tasks
                        self._random_delay()
                        
        except Exception as e:
            self.logger.error(f"Error in automation cycle: {e}")
            
        finally:
            self.close_browser()
            
        return results
    
    def _random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None) -> None:
        """
        Add random delay to simulate human behavior.
        
        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        min_delay = min_delay or self.min_delay
        max_delay = max_delay or self.max_delay
        
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def get_search_statistics(self) -> Dict:
        """
        Get search execution statistics.
        
        Returns:
            Dict: Search statistics
        """
        return self.search_analyzer.get_statistics()
