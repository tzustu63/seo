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
        """Initialize and start Chrome browser with anti-detection features."""
        try:
            chrome_options = webdriver.ChromeOptions()
            
            # 基本設定
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # 反自動化檢測
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 模擬真實瀏覽器
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-notifications')
            
            # 設定真實的 User-Agent
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            ]
            chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # 設定語言
            chrome_options.add_argument('--lang=zh-TW')
            
            # 初始化瀏覽器
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 執行反檢測腳本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 設定更多反檢測屬性
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self.driver.execute_script("return navigator.userAgent").replace('HeadlessChrome', 'Chrome')
            })
            
            # 移除 webdriver 痕跡
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-TW', 'zh', 'en-US', 'en']
                });
            """)
            
            self.logger.info("Browser started successfully with anti-detection features")
            
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
        Execute Google search for a specific keyword with human-like behavior.
        
        Args:
            keyword: Search keyword
            
        Returns:
            bool: True if search executed successfully, False otherwise
        """
        try:
            self.logger.info(f"Starting search for keyword: {keyword}")
            
            # Navigate to Google
            self.driver.get("https://www.google.com.tw")
            
            # 隨機短暫延遲（模擬頁面加載後的思考時間）
            time.sleep(random.uniform(0.5, 1.5))
            
            # Wait for search box
            search_box = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # 模擬人類滑鼠移動到搜尋框
            time.sleep(random.uniform(0.3, 0.8))
            
            # 清空搜尋框
            search_box.clear()
            
            # 模擬人類打字（逐字輸入，而非一次性貼上）
            for char in keyword:
                search_box.send_keys(char)
                # 每個字元間隔隨機延遲（模擬打字速度）
                time.sleep(random.uniform(0.05, 0.15))
            
            # 輸入完成後的短暫停頓（模擬思考）
            time.sleep(random.uniform(0.3, 0.8))
            
            # 提交搜尋
            search_box.submit()
            
            # Wait for search results
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 模擬查看搜尋結果的時間
            time.sleep(random.uniform(1.0, 2.5))
            
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
        Find and click target URL in search results with human-like behavior.
        
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
                
                # 模擬人類瀏覽行為：隨機滾動頁面查看結果
                scroll_amount = random.randint(200, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 1.5))
                
                # 有時候會向上滾動一點（模擬重新查看）
                if random.random() < 0.3:
                    scroll_back = random.randint(50, 150)
                    self.driver.execute_script(f"window.scrollBy(0, -{scroll_back});")
                    time.sleep(random.uniform(0.3, 0.8))
                
                # Get all links on the page
                links = self.driver.find_elements(By.TAG_NAME, "a")
                
                # Check each link against target URL using URL manager's matching logic
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and self.url_manager.match_url(href, target_url):
                            # 模擬滾動到目標連結位置
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
                            time.sleep(random.uniform(0.5, 1.2))
                            
                            # 模擬滑鼠懸停（查看連結）
                            time.sleep(random.uniform(0.3, 0.8))
                            
                            # Click the matching link
                            link.click()
                            self.logger.info(f"Successfully clicked target URL on page {page + 1}: {href}")
                            
                            # 等待新頁面加載
                            time.sleep(random.uniform(1.0, 2.0))
                            
                            return True, page + 1
                    except Exception as e:
                        self.logger.debug(f"Error checking link: {e}")
                        continue
                
                # Try to go to next page if not found
                if page < self.max_pages - 1:
                    try:
                        # 滾動到頁面底部（尋找下一頁按鈕）
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(random.uniform(0.5, 1.0))
                        
                        next_button = self.driver.find_element(By.LINK_TEXT, "下一頁")
                        
                        # 滾動到下一頁按鈕
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                        time.sleep(random.uniform(0.5, 1.0))
                        
                        # 點擊下一頁
                        next_button.click()
                        
                        # 等待頁面加載
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
                # 模擬在目標頁面上的真實瀏覽行為
                self._simulate_page_browsing()
                
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
    
    def _simulate_page_browsing(self) -> None:
        """
        模擬真實的頁面瀏覽行為，避免被偵測為機器人。
        """
        try:
            # 模擬閱讀頁面：隨機滾動
            num_scrolls = random.randint(2, 5)
            
            for _ in range(num_scrolls):
                # 隨機向下滾動
                scroll_amount = random.randint(300, 700)
                self.driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
                
                # 停留一段時間（模擬閱讀）
                time.sleep(random.uniform(1.5, 3.5))
                
                # 有時候會向上滾動（模擬重新閱讀某段內容）
                if random.random() < 0.4:
                    scroll_back = random.randint(100, 300)
                    self.driver.execute_script(f"window.scrollBy({{top: -{scroll_back}, behavior: 'smooth'}});")
                    time.sleep(random.uniform(0.8, 1.5))
            
            # 模擬滾動到頁面頂部或底部
            if random.random() < 0.5:
                # 滾動到底部
                self.driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
                time.sleep(random.uniform(1.0, 2.0))
            else:
                # 滾動到頂部
                self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
                time.sleep(random.uniform(1.0, 2.0))
            
            # 隨機在中間位置停留
            middle_position = random.randint(200, 800)
            self.driver.execute_script(f"window.scrollTo({{top: {middle_position}, behavior: 'smooth'}});")
            time.sleep(random.uniform(1.0, 2.5))
            
            self.logger.debug("Page browsing simulation completed")
            
        except Exception as e:
            self.logger.warning(f"Error during page browsing simulation: {e}")
    
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
