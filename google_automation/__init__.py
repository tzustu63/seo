"""
Google Search Automation Package

A modular system for automated Google search and web page clicking
to enhance SEO through intelligent search automation.
"""

__version__ = "1.0.0"
__author__ = "SEO Automation Team"

from .core.google_automation import GoogleSearchAutomation
from .core.keyword_manager import KeywordManager
from .core.url_manager import URLManager
from .core.search_analyzer import SearchAnalyzer
from .core.wait_manager import WaitManager

__all__ = [
    "GoogleSearchAutomation",
    "KeywordManager", 
    "URLManager",
    "SearchAnalyzer",
    "WaitManager"
]
