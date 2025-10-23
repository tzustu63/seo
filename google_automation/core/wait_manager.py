"""
Intelligent Waiting and Error Handling System

Provides smart waiting mechanisms and comprehensive error handling for automation.
"""

import time
import random
import logging
from typing import Optional, Callable, Any, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    WebDriverException
)


class WaitManager:
    """
    Manages intelligent waiting and error handling for automation.
    
    Features:
    - Dynamic wait times based on page load status
    - Retry mechanisms with exponential backoff
    - Comprehensive error handling and logging
    - Human-like behavior simulation
    """
    
    def __init__(self, driver: WebDriver, base_timeout: int = 10):
        """
        Initialize Wait Manager.
        
        Args:
            driver: Selenium WebDriver instance
            base_timeout: Base timeout in seconds
        """
        self.driver = driver
        self.base_timeout = base_timeout
        self.logger = logging.getLogger(__name__)
        
        # Wait configuration
        self.min_wait = 1
        self.max_wait = 30
        self.retry_attempts = 3
        self.backoff_factor = 2
    
    def wait_for_element(self, 
                        locator: Tuple[By, str], 
                        timeout: Optional[int] = None,
                        retry_on_stale: bool = True) -> bool:
        """
        Wait for element to be present and visible.
        
        Args:
            locator: Element locator tuple (By, value)
            timeout: Custom timeout in seconds
            retry_on_stale: Whether to retry on stale element reference
            
        Returns:
            bool: True if element found, False otherwise
        """
        timeout = timeout or self.base_timeout
        by, value = locator
        
        for attempt in range(self.retry_attempts):
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
                return True
                
            except StaleElementReferenceException:
                if retry_on_stale and attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Stale element reference, retrying... (attempt {attempt + 1})")
                    self._exponential_backoff(attempt)
                    continue
                else:
                    self.logger.error(f"Stale element reference after {self.retry_attempts} attempts")
                    return False
                    
            except TimeoutException:
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Element not found, retrying... (attempt {attempt + 1})")
                    self._exponential_backoff(attempt)
                else:
                    self.logger.error(f"Element not found after {self.retry_attempts} attempts: {by}={value}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Unexpected error waiting for element: {e}")
                return False
        
        return False
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for page to fully load.
        
        Args:
            timeout: Custom timeout in seconds
            
        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        timeout = timeout or self.base_timeout
        
        try:
            # Wait for document ready state
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for dynamic content
            time.sleep(random.uniform(0.5, 1.5))
            
            return True
            
        except TimeoutException:
            self.logger.error("Page load timeout")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {e}")
            return False
    
    def wait_for_clickable(self, 
                          locator: Tuple[By, str], 
                          timeout: Optional[int] = None) -> bool:
        """
        Wait for element to be clickable.
        
        Args:
            locator: Element locator tuple (By, value)
            timeout: Custom timeout in seconds
            
        Returns:
            bool: True if element is clickable, False otherwise
        """
        timeout = timeout or self.base_timeout
        by, value = locator
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return True
            
        except TimeoutException:
            self.logger.error(f"Element not clickable after timeout: {by}={value}")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for clickable element: {e}")
            return False
    
    def safe_click(self, 
                   locator: Tuple[By, str], 
                   timeout: Optional[int] = None) -> bool:
        """
        Safely click an element with error handling.
        
        Args:
            locator: Element locator tuple (By, value)
            timeout: Custom timeout in seconds
            
        Returns:
            bool: True if click successful, False otherwise
        """
        if not self.wait_for_clickable(locator, timeout):
            return False
        
        by, value = locator
        
        for attempt in range(self.retry_attempts):
            try:
                element = self.driver.find_element(by, value)
                element.click()
                self.logger.info(f"Successfully clicked element: {by}={value}")
                return True
                
            except StaleElementReferenceException:
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Stale element on click, retrying... (attempt {attempt + 1})")
                    self._exponential_backoff(attempt)
                    continue
                else:
                    self.logger.error(f"Stale element after {self.retry_attempts} click attempts")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error clicking element: {e}")
                return False
        
        return False
    
    def safe_send_keys(self, 
                      locator: Tuple[By, str], 
                      text: str,
                      clear_first: bool = True,
                      timeout: Optional[int] = None) -> bool:
        """
        Safely send keys to an element with error handling.
        
        Args:
            locator: Element locator tuple (By, value)
            text: Text to send
            clear_first: Whether to clear field first
            timeout: Custom timeout in seconds
            
        Returns:
            bool: True if send keys successful, False otherwise
        """
        if not self.wait_for_element(locator, timeout):
            return False
        
        by, value = locator
        
        for attempt in range(self.retry_attempts):
            try:
                element = self.driver.find_element(by, value)
                
                if clear_first:
                    element.clear()
                
                # Simulate human typing
                for char in text:
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.logger.info(f"Successfully sent keys to element: {by}={value}")
                return True
                
            except StaleElementReferenceException:
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Stale element on send keys, retrying... (attempt {attempt + 1})")
                    self._exponential_backoff(attempt)
                    continue
                else:
                    self.logger.error(f"Stale element after {self.retry_attempts} send keys attempts")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error sending keys to element: {e}")
                return False
        
        return False
    
    def wait_for_url_change(self, 
                           current_url: str, 
                           timeout: Optional[int] = None) -> bool:
        """
        Wait for URL to change from current URL.
        
        Args:
            current_url: Current URL to wait for change from
            timeout: Custom timeout in seconds
            
        Returns:
            bool: True if URL changed, False otherwise
        """
        timeout = timeout or self.base_timeout
        
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.current_url != current_url
            )
            return True
            
        except TimeoutException:
            self.logger.warning(f"URL did not change within timeout: {current_url}")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for URL change: {e}")
            return False
    
    def human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> None:
        """
        Add human-like random delay.
        
        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _exponential_backoff(self, attempt: int) -> None:
        """
        Apply exponential backoff delay.
        
        Args:
            attempt: Current attempt number (0-based)
        """
        delay = self.min_wait * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_wait)
        time.sleep(delay)
    
    def retry_operation(self, 
                       operation: Callable[[], Any], 
                       max_attempts: Optional[int] = None) -> Tuple[bool, Any]:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Function to retry
            max_attempts: Maximum number of attempts
            
        Returns:
            Tuple[bool, Any]: (success, result)
        """
        max_attempts = max_attempts or self.retry_attempts
        
        for attempt in range(max_attempts):
            try:
                result = operation()
                return True, result
                
            except Exception as e:
                if attempt < max_attempts - 1:
                    self.logger.warning(f"Operation failed, retrying... (attempt {attempt + 1}): {e}")
                    self._exponential_backoff(attempt)
                else:
                    self.logger.error(f"Operation failed after {max_attempts} attempts: {e}")
                    return False, None
        
        return False, None
    
    def handle_webdriver_exception(self, e: WebDriverException) -> bool:
        """
        Handle WebDriver exceptions with appropriate responses.
        
        Args:
            e: WebDriver exception
            
        Returns:
            bool: True if exception was handled, False otherwise
        """
        if isinstance(e, TimeoutException):
            self.logger.warning("Timeout exception occurred")
            return True
        elif isinstance(e, NoSuchElementException):
            self.logger.warning("Element not found exception occurred")
            return True
        elif isinstance(e, StaleElementReferenceException):
            self.logger.warning("Stale element reference exception occurred")
            return True
        else:
            self.logger.error(f"Unhandled WebDriver exception: {e}")
            return False
