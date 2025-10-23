"""
Logging Setup Utility

Configures comprehensive logging for Google Search Automation.
"""

import os
import logging
import logging.handlers
from typing import Dict, Optional
from pathlib import Path


def setup_logging(config: Dict) -> None:
    """
    Setup comprehensive logging system.
    
    Args:
        config: Logging configuration dictionary
    """
    # Get logging configuration
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', 'logs/automation.log')
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    max_file_size = log_config.get('max_file_size', 10) * 1024 * 1024  # Convert to bytes
    backup_count = log_config.get('backup_count', 5)
    console_output = log_config.get('console_output', True)
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    _configure_module_loggers(log_config)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized successfully")


def _configure_module_loggers(log_config: Dict) -> None:
    """
    Configure specific module loggers.
    
    Args:
        log_config: Logging configuration
    """
    # Selenium logger - reduce noise
    selenium_logger = logging.getLogger('selenium')
    selenium_logger.setLevel(logging.WARNING)
    
    # WebDriver logger - reduce noise
    webdriver_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
    webdriver_logger.setLevel(logging.WARNING)
    
    # urllib3 logger - reduce noise
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.WARNING)
    
    # Our automation loggers - more verbose
    automation_logger = logging.getLogger('google_automation')
    automation_logger.setLevel(logging.DEBUG)
    
    # Search analyzer logger
    analyzer_logger = logging.getLogger('google_automation.core.search_analyzer')
    analyzer_logger.setLevel(logging.INFO)
    
    # Wait manager logger
    wait_logger = logging.getLogger('google_automation.core.wait_manager')
    wait_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def log_search_result(logger: logging.Logger, 
                     keyword: str, 
                     target_url: str, 
                     success: bool, 
                     page_found: int = 0,
                     execution_time: float = 0.0) -> None:
    """
    Log search result in a structured format.
    
    Args:
        logger: Logger instance
        keyword: Search keyword
        target_url: Target URL
        success: Whether search was successful
        page_found: Page number where URL was found
        execution_time: Execution time in seconds
    """
    status = "SUCCESS" if success else "FAILED"
    page_info = f" (page {page_found})" if success and page_found > 0 else ""
    
    logger.info(
        f"SEARCH_RESULT: {status} | "
        f"Keyword: {keyword} | "
        f"URL: {target_url} | "
        f"Time: {execution_time:.2f}s{page_info}"
    )


def log_error(logger: logging.Logger, 
              error: Exception, 
              context: str = "",
              **kwargs) -> None:
    """
    Log error with context information.
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
        **kwargs: Additional context data
    """
    context_info = f" | Context: {context}" if context else ""
    additional_info = " | ".join([f"{k}: {v}" for k, v in kwargs.items()]) if kwargs else ""
    
    logger.error(
        f"ERROR: {type(error).__name__}: {str(error)}{context_info} | {additional_info}",
        exc_info=True
    )


def log_performance(logger: logging.Logger, 
                   operation: str, 
                   duration: float,
                   **metrics) -> None:
    """
    Log performance metrics.
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **metrics: Additional metrics
    """
    metrics_str = " | ".join([f"{k}: {v}" for k, v in metrics.items()]) if metrics else ""
    
    logger.info(
        f"PERFORMANCE: {operation} | "
        f"Duration: {duration:.2f}s | "
        f"{metrics_str}"
    )


def log_statistics(logger: logging.Logger, 
                  stats: Dict) -> None:
    """
    Log statistics summary.
    
    Args:
        logger: Logger instance
        stats: Statistics dictionary
    """
    session = stats.get('session', {})
    keywords = stats.get('keywords', {})
    urls = stats.get('urls', {})
    
    logger.info(
        f"STATISTICS: "
        f"Total Searches: {session.get('total_searches', 0)} | "
        f"Success Rate: {session.get('overall_success_rate', 0):.2%} | "
        f"Unique Keywords: {keywords.get('total_unique', 0)} | "
        f"Unique URLs: {urls.get('total_unique', 0)}"
    )
