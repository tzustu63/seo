"""
Configuration Loader Utility

Loads and validates configuration from YAML files.
"""

import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """
    Loads and validates configuration for Google Search Automation.
    
    Features:
    - YAML configuration loading
    - Configuration validation
    - Default value handling
    - Environment variable substitution
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize Config Loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.config: Dict[str, Any] = {}
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        try:
            if not self.config_path.exists():
                self.logger.error(f"Configuration file not found: {self.config_path}")
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            # Validate configuration
            self._validate_config()
            
            # Apply defaults
            self._apply_defaults()
            
            self.logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config
            
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise
    
    def _validate_config(self) -> None:
        """Validate configuration structure and values."""
        required_sections = ['general', 'keywords', 'target_urls']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required configuration section: {section}")
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate general section
        general = self.config['general']
        if not isinstance(general.get('max_pages', 0), int) or general.get('max_pages', 0) <= 0:
            raise ValueError("max_pages must be a positive integer")
        
        if not isinstance(general.get('wait_timeout', 0), (int, float)) or general.get('wait_timeout', 0) <= 0:
            raise ValueError("wait_timeout must be a positive number")
        
        # Validate keywords section
        keywords = self.config['keywords']
        if not isinstance(keywords.get('single_keywords', []), list):
            raise ValueError("single_keywords must be a list")
        
        # Validate target_urls section
        target_urls = self.config['target_urls']
        if not isinstance(target_urls, list):
            raise ValueError("target_urls must be a list")
        
        for i, url_config in enumerate(target_urls):
            if not isinstance(url_config, dict):
                raise ValueError(f"target_urls[{i}] must be a dictionary")
            
            if 'url' not in url_config:
                raise ValueError(f"target_urls[{i}] missing required 'url' field")
    
    def _apply_defaults(self) -> None:
        """Apply default values for missing configuration options."""
        # General defaults
        general_defaults = {
            'max_pages': 10,
            'wait_timeout': 10,
            'min_delay': 2,
            'max_delay': 5,
            'page_delay': {'min': 20, 'max': 30},
            'retry_attempts': 3,
            'max_concurrent_searches': 1
        }
        
        general = self.config.setdefault('general', {})
        for key, default_value in general_defaults.items():
            general.setdefault(key, default_value)
        
        # Browser defaults
        browser_defaults = {
            'options': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ],
            'window_size': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        browser = self.config.setdefault('browser', {})
        for key, default_value in browser_defaults.items():
            browser.setdefault(key, default_value)
        
        # Logging defaults
        logging_defaults = {
            'level': 'INFO',
            'file': 'logs/automation.log',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'max_file_size': 10,
            'backup_count': 5,
            'console_output': True
        }
        
        logging_config = self.config.setdefault('logging', {})
        for key, default_value in logging_defaults.items():
            logging_config.setdefault(key, default_value)
        
        # Monitoring defaults
        monitoring_defaults = {
            'collection_interval': 60,
            'report_interval': 300,
            'stats_file': 'logs/statistics.json',
            'detailed_stats': True
        }
        
        monitoring = self.config.setdefault('monitoring', {})
        for key, default_value in monitoring_defaults.items():
            monitoring.setdefault(key, default_value)
        
        # Error handling defaults
        error_handling_defaults = {
            'max_retries': 3,
            'retry_delay': 5,
            'error_reporting': True,
            'error_file': 'logs/errors.log',
            'stop_on_critical_error': False
        }
        
        error_handling = self.config.setdefault('error_handling', {})
        for key, default_value in error_handling_defaults.items():
            error_handling.setdefault(key, default_value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get a specific configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Dict[str, Any]: Section configuration
        """
        return self.config.get(section, {})
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path (e.g., 'general.max_pages')
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path (e.g., 'general.max_pages')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_config(self, output_path: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            output_path: Output file path (defaults to original config path)
        """
        save_path = Path(output_path) if output_path else self.config_path
        
        try:
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            raise
    
    def reload_config(self) -> Dict[str, Any]:
        """
        Reload configuration from file.
        
        Returns:
            Dict[str, Any]: Reloaded configuration
        """
        self.logger.info("Reloading configuration...")
        return self.load_config()
    
    def get_keywords_config(self) -> Dict[str, Any]:
        """
        Get keywords configuration.
        
        Returns:
            Dict[str, Any]: Keywords configuration
        """
        return self.get_section('keywords')
    
    def get_target_urls_config(self) -> list:
        """
        Get target URLs configuration.
        
        Returns:
            list: Target URLs configuration
        """
        return self.get_section('target_urls')
    
    def get_general_config(self) -> Dict[str, Any]:
        """
        Get general configuration.
        
        Returns:
            Dict[str, Any]: General configuration
        """
        return self.get_section('general')
    
    def get_browser_config(self) -> Dict[str, Any]:
        """
        Get browser configuration.
        
        Returns:
            Dict[str, Any]: Browser configuration
        """
        return self.get_section('browser')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Dict[str, Any]: Logging configuration
        """
        return self.get_section('logging')
    
    def validate_keywords(self) -> bool:
        """
        Validate keywords configuration.
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            keywords = self.get_keywords_config()
            single_keywords = keywords.get('single_keywords', [])
            
            if not isinstance(single_keywords, list):
                return False
            
            for keyword_config in single_keywords:
                if isinstance(keyword_config, dict):
                    if 'keyword' not in keyword_config:
                        return False
                elif not isinstance(keyword_config, str):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def validate_target_urls(self) -> bool:
        """
        Validate target URLs configuration.
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            target_urls = self.get_target_urls_config()
            
            if not isinstance(target_urls, list):
                return False
            
            for url_config in target_urls:
                if not isinstance(url_config, dict):
                    return False
                
                if 'url' not in url_config:
                    return False
                
                # Basic URL validation
                url = url_config['url']
                if not url.startswith(('http://', 'https://')):
                    return False
            
            return True
            
        except Exception:
            return False
