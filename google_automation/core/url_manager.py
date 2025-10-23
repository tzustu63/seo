"""
URL Management System

Manages target URLs and URL matching strategies for Google automation.
"""

import logging
import re
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class URLConfig:
    """Configuration for a target URL."""
    url: str
    enabled: bool = True
    priority: int = 1
    match_type: str = "contains"  # contains, exact, domain, regex
    keywords: List[str] = None
    max_attempts: int = 3
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class URLManager:
    """
    Manages target URLs and URL matching strategies.
    
    Supports:
    - Multiple target URL management
    - Different URL matching strategies
    - Priority-based URL selection
    - URL validation and normalization
    """
    
    def __init__(self, config: Union[List[str], List[Dict]]):
        """
        Initialize URL Manager.
        
        Args:
            config: List of URLs or URL configurations
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.urls: List[URLConfig] = []
        
        # Load URLs from configuration
        self._load_urls()
    
    def _load_urls(self) -> None:
        """Load URLs from configuration."""
        try:
            for url_data in self.config:
                if isinstance(url_data, str):
                    url_config = URLConfig(url=url_data)
                else:
                    url_config = URLConfig(**url_data)
                
                # Validate URL
                if self._validate_url(url_config.url):
                    self.urls.append(url_config)
                else:
                    self.logger.warning(f"Invalid URL skipped: {url_config.url}")
            
            # Sort by priority
            self.urls.sort(key=lambda x: x.priority)
            
            self.logger.info(f"Loaded {len(self.urls)} target URLs")
            
        except Exception as e:
            self.logger.error(f"Error loading URLs: {e}")
            raise
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        try:
            # Check if it's a regex pattern (contains special regex characters)
            if any(char in url for char in ['*', '+', '?', '(', ')', '[', ']', '{', '}', '|', '\\', '^', '$']):
                # Try to compile as regex to validate
                re.compile(url)
                return True
            
            # Standard URL validation
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for consistent matching.
        
        Args:
            url: URL to normalize
            
        Returns:
            str: Normalized URL
        """
        # Remove trailing slash and normalize
        url = url.rstrip('/')
        
        # Ensure https protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    def get_all_urls(self) -> List[str]:
        """
        Get all enabled URLs as strings.
        
        Returns:
            List[str]: List of enabled URLs
        """
        return [url.url for url in self.urls if url.enabled]
    
    def get_url_config(self, url: str) -> Optional[URLConfig]:
        """
        Get configuration for a specific URL.
        
        Args:
            url: URL to get configuration for
            
        Returns:
            Optional[URLConfig]: URL configuration or None if not found
        """
        for url_config in self.urls:
            if url_config.url == url:
                return url_config
        return None
    
    def add_url(self, url: str, **kwargs) -> bool:
        """
        Add a new target URL.
        
        Args:
            url: URL to add
            **kwargs: Additional URL configuration
            
        Returns:
            bool: True if URL was added, False if invalid
        """
        if not self._validate_url(url):
            self.logger.error(f"Invalid URL: {url}")
            return False
        
        normalized_url = self._normalize_url(url)
        url_config = URLConfig(url=normalized_url, **kwargs)
        self.urls.append(url_config)
        self.urls.sort(key=lambda x: x.priority)
        
        self.logger.info(f"Added target URL: {normalized_url}")
        return True
    
    def remove_url(self, url: str) -> bool:
        """
        Remove a target URL.
        
        Args:
            url: URL to remove
            
        Returns:
            bool: True if URL was removed, False if not found
        """
        normalized_url = self._normalize_url(url)
        for i, url_config in enumerate(self.urls):
            if url_config.url == normalized_url:
                del self.urls[i]
                self.logger.info(f"Removed target URL: {normalized_url}")
                return True
        return False
    
    def enable_url(self, url: str) -> bool:
        """
        Enable a target URL.
        
        Args:
            url: URL to enable
            
        Returns:
            bool: True if URL was enabled, False if not found
        """
        normalized_url = self._normalize_url(url)
        for url_config in self.urls:
            if url_config.url == normalized_url:
                url_config.enabled = True
                self.logger.info(f"Enabled target URL: {normalized_url}")
                return True
        return False
    
    def disable_url(self, url: str) -> bool:
        """
        Disable a target URL.
        
        Args:
            url: URL to disable
            
        Returns:
            bool: True if URL was disabled, False if not found
        """
        normalized_url = self._normalize_url(url)
        for url_config in self.urls:
            if url_config.url == normalized_url:
                url_config.enabled = False
                self.logger.info(f"Disabled target URL: {normalized_url}")
                return True
        return False
    
    def match_url(self, found_url: str, target_url: str) -> bool:
        """
        Check if found URL matches target URL based on match type.
        
        Args:
            found_url: URL found in search results
            target_url: Target URL to match against
            
        Returns:
            bool: True if URLs match, False otherwise
        """
        target_config = self.get_url_config(target_url)
        if not target_config:
            return False
        
        match_type = target_config.match_type
        found_url = self._normalize_url(found_url)
        target_url = self._normalize_url(target_url)
        
        if match_type == "exact":
            return found_url == target_url
        elif match_type == "contains":
            return target_url in found_url
        elif match_type == "domain":
            found_domain = urlparse(found_url).netloc
            target_domain = urlparse(target_url).netloc
            return found_domain == target_domain
        elif match_type == "regex":
            try:
                pattern = re.compile(target_url)
                return bool(pattern.search(found_url))
            except re.error:
                self.logger.error(f"Invalid regex pattern: {target_url}")
                return False
        else:
            # Default to contains
            return target_url in found_url
    
    def get_urls_by_priority(self, priority: int) -> List[str]:
        """
        Get URLs by priority level.
        
        Args:
            priority: Priority level
            
        Returns:
            List[str]: URLs with specified priority
        """
        return [url.url for url in self.urls if url.priority == priority and url.enabled]
    
    def get_high_priority_urls(self) -> List[str]:
        """
        Get high priority URLs (priority 1).
        
        Returns:
            List[str]: High priority URLs
        """
        return self.get_urls_by_priority(1)
    
    def get_urls_for_keyword(self, keyword: str) -> List[str]:
        """
        Get URLs that are associated with a specific keyword.
        
        Args:
            keyword: Keyword to get URLs for
            
        Returns:
            List[str]: URLs associated with the keyword
        """
        associated_urls = []
        for url_config in self.urls:
            if url_config.enabled and (not url_config.keywords or keyword in url_config.keywords):
                associated_urls.append(url_config.url)
        return associated_urls
    
    def get_url_statistics(self) -> Dict:
        """
        Get URL statistics.
        
        Returns:
            Dict: URL statistics
        """
        total_urls = len(self.urls)
        enabled_urls = len([url for url in self.urls if url.enabled])
        disabled_urls = total_urls - enabled_urls
        
        priority_distribution = {}
        match_type_distribution = {}
        
        for url in self.urls:
            priority = url.priority
            match_type = url.match_type
            
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            match_type_distribution[match_type] = match_type_distribution.get(match_type, 0) + 1
        
        return {
            'total_urls': total_urls,
            'enabled_urls': enabled_urls,
            'disabled_urls': disabled_urls,
            'priority_distribution': priority_distribution,
            'match_type_distribution': match_type_distribution
        }
    
    def export_urls(self) -> Dict:
        """
        Export URLs configuration.
        
        Returns:
            Dict: URLs configuration
        """
        return {
            'target_urls': [
                {
                    'url': url.url,
                    'enabled': url.enabled,
                    'priority': url.priority,
                    'match_type': url.match_type,
                    'keywords': url.keywords,
                    'max_attempts': url.max_attempts
                }
                for url in self.urls
            ]
        }
