"""
Keyword Management System

Manages search keywords and search strategies for Google automation.
"""

import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass


@dataclass
class KeywordConfig:
    """Configuration for a single keyword."""
    keyword: str
    enabled: bool = True
    priority: int = 1
    max_pages: Optional[int] = None
    search_modifiers: List[str] = None
    
    def __post_init__(self):
        if self.search_modifiers is None:
            self.search_modifiers = []


class KeywordManager:
    """
    Manages search keywords and search strategies.
    
    Supports:
    - Single keyword management
    - Keyword combinations
    - Search modifiers and exclusions
    - Priority-based execution
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Keyword Manager.
        
        Args:
            config: Configuration dictionary containing keyword settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.keywords: List[KeywordConfig] = []
        
        # Load keywords from configuration
        self._load_keywords()
    
    def _load_keywords(self) -> None:
        """Load keywords from configuration."""
        try:
            # Load single keywords
            single_keywords = self.config.get('single_keywords', [])
            for keyword_data in single_keywords:
                if isinstance(keyword_data, str):
                    keyword = KeywordConfig(keyword=keyword_data)
                else:
                    keyword = KeywordConfig(**keyword_data)
                self.keywords.append(keyword)
            
            # Load keyword combinations
            combinations = self.config.get('combinations', [])
            for combo_data in combinations:
                if isinstance(combo_data, str):
                    keyword = KeywordConfig(keyword=combo_data)
                else:
                    keyword = KeywordConfig(**combo_data)
                self.keywords.append(keyword)
            
            # Sort by priority
            self.keywords.sort(key=lambda x: x.priority)
            
            self.logger.info(f"Loaded {len(self.keywords)} keywords")
            
        except Exception as e:
            self.logger.error(f"Error loading keywords: {e}")
            raise
    
    def get_all_keywords(self) -> List[str]:
        """
        Get all enabled keywords as strings.
        
        Returns:
            List[str]: List of enabled keywords
        """
        return [kw.keyword for kw in self.keywords if kw.enabled]
    
    def get_keyword_config(self, keyword: str) -> Optional[KeywordConfig]:
        """
        Get configuration for a specific keyword.
        
        Args:
            keyword: Keyword to get configuration for
            
        Returns:
            Optional[KeywordConfig]: Keyword configuration or None if not found
        """
        for kw in self.keywords:
            if kw.keyword == keyword:
                return kw
        return None
    
    def add_keyword(self, keyword: str, **kwargs) -> None:
        """
        Add a new keyword.
        
        Args:
            keyword: Keyword to add
            **kwargs: Additional keyword configuration
        """
        keyword_config = KeywordConfig(keyword=keyword, **kwargs)
        self.keywords.append(keyword_config)
        self.keywords.sort(key=lambda x: x.priority)
        
        self.logger.info(f"Added keyword: {keyword}")
    
    def remove_keyword(self, keyword: str) -> bool:
        """
        Remove a keyword.
        
        Args:
            keyword: Keyword to remove
            
        Returns:
            bool: True if keyword was removed, False if not found
        """
        for i, kw in enumerate(self.keywords):
            if kw.keyword == keyword:
                del self.keywords[i]
                self.logger.info(f"Removed keyword: {keyword}")
                return True
        return False
    
    def enable_keyword(self, keyword: str) -> bool:
        """
        Enable a keyword.
        
        Args:
            keyword: Keyword to enable
            
        Returns:
            bool: True if keyword was enabled, False if not found
        """
        for kw in self.keywords:
            if kw.keyword == keyword:
                kw.enabled = True
                self.logger.info(f"Enabled keyword: {keyword}")
                return True
        return False
    
    def disable_keyword(self, keyword: str) -> bool:
        """
        Disable a keyword.
        
        Args:
            keyword: Keyword to disable
            
        Returns:
            bool: True if keyword was disabled, False if not found
        """
        for kw in self.keywords:
            if kw.keyword == keyword:
                kw.enabled = False
                self.logger.info(f"Disabled keyword: {keyword}")
                return True
        return False
    
    def get_keywords_by_priority(self, priority: int) -> List[str]:
        """
        Get keywords by priority level.
        
        Args:
            priority: Priority level
            
        Returns:
            List[str]: Keywords with specified priority
        """
        return [kw.keyword for kw in self.keywords if kw.priority == priority and kw.enabled]
    
    def get_high_priority_keywords(self) -> List[str]:
        """
        Get high priority keywords (priority 1).
        
        Returns:
            List[str]: High priority keywords
        """
        return self.get_keywords_by_priority(1)
    
    def create_keyword_combination(self, keywords: List[str], operator: str = " ") -> str:
        """
        Create a keyword combination.
        
        Args:
            keywords: List of keywords to combine
            operator: Operator to use for combination (default: space)
            
        Returns:
            str: Combined keyword string
        """
        return operator.join(keywords)
    
    def add_exclusion_keyword(self, base_keyword: str, exclusion: str) -> str:
        """
        Add exclusion keyword using minus operator.
        
        Args:
            base_keyword: Base keyword
            exclusion: Keyword to exclude
            
        Returns:
            str: Keyword with exclusion
        """
        return f"{base_keyword} -{exclusion}"
    
    def get_keyword_statistics(self) -> Dict:
        """
        Get keyword statistics.
        
        Returns:
            Dict: Keyword statistics
        """
        total_keywords = len(self.keywords)
        enabled_keywords = len([kw for kw in self.keywords if kw.enabled])
        disabled_keywords = total_keywords - enabled_keywords
        
        priority_distribution = {}
        for kw in self.keywords:
            priority = kw.priority
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        return {
            'total_keywords': total_keywords,
            'enabled_keywords': enabled_keywords,
            'disabled_keywords': disabled_keywords,
            'priority_distribution': priority_distribution
        }
    
    def export_keywords(self) -> Dict:
        """
        Export keywords configuration.
        
        Returns:
            Dict: Keywords configuration
        """
        return {
            'single_keywords': [
                {
                    'keyword': kw.keyword,
                    'enabled': kw.enabled,
                    'priority': kw.priority,
                    'max_pages': kw.max_pages,
                    'search_modifiers': kw.search_modifiers
                }
                for kw in self.keywords
            ]
        }
