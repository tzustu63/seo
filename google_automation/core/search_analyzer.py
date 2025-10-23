"""
Search Result Analysis System

Analyzes search results and provides statistics for SEO automation.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter


@dataclass
class SearchResult:
    """Individual search result data."""
    keyword: str
    target_url: str
    success: bool
    page_found: int
    execution_time: float
    timestamp: float = field(default_factory=time.time)
    error: Optional[str] = None


@dataclass
class KeywordStats:
    """Statistics for a specific keyword."""
    keyword: str
    total_searches: int = 0
    successful_searches: int = 0
    failed_searches: int = 0
    average_page_position: float = 0.0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    last_search_time: Optional[float] = None


@dataclass
class URLStats:
    """Statistics for a specific target URL."""
    url: str
    total_clicks: int = 0
    successful_clicks: int = 0
    failed_clicks: int = 0
    average_page_position: float = 0.0
    click_rate: float = 0.0
    last_click_time: Optional[float] = None


class SearchAnalyzer:
    """
    Analyzes search results and provides comprehensive statistics.
    
    Features:
    - Search result tracking and analysis
    - Keyword performance metrics
    - URL click-through statistics
    - Ranking position analysis
    - Performance trend analysis
    """
    
    def __init__(self):
        """Initialize Search Analyzer."""
        self.logger = logging.getLogger(__name__)
        self.search_results: List[SearchResult] = []
        self.keyword_stats: Dict[str, KeywordStats] = {}
        self.url_stats: Dict[str, URLStats] = {}
        
        # Performance tracking
        self.session_start_time = time.time()
        self.total_searches = 0
        self.total_successful_searches = 0
    
    def record_search_result(self, 
                           keyword: str, 
                           target_url: str, 
                           page_found: int, 
                           success: bool,
                           execution_time: float = 0.0,
                           error: Optional[str] = None) -> None:
        """
        Record a search result.
        
        Args:
            keyword: Search keyword used
            target_url: Target URL searched for
            page_found: Page number where URL was found (0 if not found)
            success: Whether search was successful
            execution_time: Time taken for search in seconds
            error: Error message if search failed
        """
        result = SearchResult(
            keyword=keyword,
            target_url=target_url,
            success=success,
            page_found=page_found,
            execution_time=execution_time,
            error=error
        )
        
        self.search_results.append(result)
        self._update_keyword_stats(result)
        self._update_url_stats(result)
        
        # Update global counters
        self.total_searches += 1
        if success:
            self.total_successful_searches += 1
        
        self.logger.info(f"Recorded search result: {keyword} -> {target_url} (success: {success})")
    
    def _update_keyword_stats(self, result: SearchResult) -> None:
        """Update keyword statistics."""
        keyword = result.keyword
        
        if keyword not in self.keyword_stats:
            self.keyword_stats[keyword] = KeywordStats(keyword=keyword)
        
        stats = self.keyword_stats[keyword]
        stats.total_searches += 1
        stats.last_search_time = result.timestamp
        
        if result.success:
            stats.successful_searches += 1
            if result.page_found > 0:
                # Update average page position
                if stats.average_page_position == 0:
                    stats.average_page_position = result.page_found
                else:
                    stats.average_page_position = (
                        (stats.average_page_position * (stats.successful_searches - 1) + result.page_found) 
                        / stats.successful_searches
                    )
        else:
            stats.failed_searches += 1
        
        # Update success rate
        stats.success_rate = stats.successful_searches / stats.total_searches
        
        # Update average execution time
        if stats.average_execution_time == 0:
            stats.average_execution_time = result.execution_time
        else:
            stats.average_execution_time = (
                (stats.average_execution_time * (stats.total_searches - 1) + result.execution_time)
                / stats.total_searches
            )
    
    def _update_url_stats(self, result: SearchResult) -> None:
        """Update URL statistics."""
        url = result.target_url
        
        if url not in self.url_stats:
            self.url_stats[url] = URLStats(url=url)
        
        stats = self.url_stats[url]
        stats.total_clicks += 1
        stats.last_click_time = result.timestamp
        
        if result.success:
            stats.successful_clicks += 1
            if result.page_found > 0:
                # Update average page position
                if stats.average_page_position == 0:
                    stats.average_page_position = result.page_found
                else:
                    stats.average_page_position = (
                        (stats.average_page_position * (stats.successful_clicks - 1) + result.page_found)
                        / stats.successful_clicks
                    )
        else:
            stats.failed_clicks += 1
        
        # Update click rate
        stats.click_rate = stats.successful_clicks / stats.total_clicks
    
    def get_keyword_performance(self, keyword: str) -> Optional[KeywordStats]:
        """
        Get performance statistics for a specific keyword.
        
        Args:
            keyword: Keyword to get stats for
            
        Returns:
            Optional[KeywordStats]: Keyword statistics or None if not found
        """
        return self.keyword_stats.get(keyword)
    
    def get_url_performance(self, url: str) -> Optional[URLStats]:
        """
        Get performance statistics for a specific URL.
        
        Args:
            url: URL to get stats for
            
        Returns:
            Optional[URLStats]: URL statistics or None if not found
        """
        return self.url_stats.get(url)
    
    def get_top_performing_keywords(self, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get top performing keywords by success rate.
        
        Args:
            limit: Maximum number of keywords to return
            
        Returns:
            List[Tuple[str, float]]: List of (keyword, success_rate) tuples
        """
        keyword_rates = [
            (keyword, stats.success_rate)
            for keyword, stats in self.keyword_stats.items()
            if stats.total_searches > 0
        ]
        
        return sorted(keyword_rates, key=lambda x: x[1], reverse=True)[:limit]
    
    def get_top_clicked_urls(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get top clicked URLs by successful clicks.
        
        Args:
            limit: Maximum number of URLs to return
            
        Returns:
            List[Tuple[str, int]]: List of (url, successful_clicks) tuples
        """
        url_clicks = [
            (url, stats.successful_clicks)
            for url, stats in self.url_stats.items()
        ]
        
        return sorted(url_clicks, key=lambda x: x[1], reverse=True)[:limit]
    
    def get_ranking_distribution(self) -> Dict[int, int]:
        """
        Get distribution of ranking positions.
        
        Returns:
            Dict[int, int]: Dictionary of {page_number: count}
        """
        positions = [result.page_found for result in self.search_results if result.success and result.page_found > 0]
        return dict(Counter(positions))
    
    def get_hourly_activity(self) -> Dict[int, int]:
        """
        Get hourly activity distribution.
        
        Returns:
            Dict[int, int]: Dictionary of {hour: search_count}
        """
        hourly_counts = defaultdict(int)
        
        for result in self.search_results:
            hour = time.localtime(result.timestamp).tm_hour
            hourly_counts[hour] += 1
        
        return dict(hourly_counts)
    
    def get_error_analysis(self) -> Dict[str, int]:
        """
        Get error analysis by error type.
        
        Returns:
            Dict[str, int]: Dictionary of {error_type: count}
        """
        errors = [result.error for result in self.search_results if result.error]
        return dict(Counter(errors))
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, List[float]]:
        """
        Get performance trends over time.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dict[str, List[float]]: Performance trends data
        """
        cutoff_time = time.time() - (hours * 3600)
        recent_results = [r for r in self.search_results if r.timestamp >= cutoff_time]
        
        # Group by hour
        hourly_data = defaultdict(list)
        for result in recent_results:
            hour = int((result.timestamp - cutoff_time) / 3600)
            hourly_data[hour].append(result)
        
        trends = {
            'success_rates': [],
            'avg_page_positions': [],
            'search_counts': []
        }
        
        for hour in sorted(hourly_data.keys()):
            results = hourly_data[hour]
            success_rate = sum(1 for r in results if r.success) / len(results) if results else 0
            avg_position = sum(r.page_found for r in results if r.success and r.page_found > 0) / max(1, sum(1 for r in results if r.success))
            
            trends['success_rates'].append(success_rate)
            trends['avg_page_positions'].append(avg_position)
            trends['search_counts'].append(len(results))
        
        return trends
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics.
        
        Returns:
            Dict: Complete statistics dictionary
        """
        session_duration = time.time() - self.session_start_time
        
        return {
            'session': {
                'duration_hours': session_duration / 3600,
                'total_searches': self.total_searches,
                'successful_searches': self.total_successful_searches,
                'overall_success_rate': self.total_successful_searches / max(1, self.total_searches),
                'searches_per_hour': self.total_searches / max(1, session_duration / 3600)
            },
            'keywords': {
                'total_unique': len(self.keyword_stats),
                'top_performers': self.get_top_performing_keywords(5),
                'stats': {k: {
                    'total_searches': v.total_searches,
                    'success_rate': v.success_rate,
                    'avg_page_position': v.average_page_position,
                    'avg_execution_time': v.average_execution_time
                } for k, v in self.keyword_stats.items()}
            },
            'urls': {
                'total_unique': len(self.url_stats),
                'top_clicked': self.get_top_clicked_urls(5),
                'stats': {u: {
                    'total_clicks': v.total_clicks,
                    'click_rate': v.click_rate,
                    'avg_page_position': v.average_page_position
                } for u, v in self.url_stats.items()}
            },
            'ranking': {
                'distribution': self.get_ranking_distribution(),
                'avg_position': sum(r.page_found for r in self.search_results if r.success and r.page_found > 0) / max(1, sum(1 for r in self.search_results if r.success))
            },
            'activity': {
                'hourly_distribution': self.get_hourly_activity(),
                'error_analysis': self.get_error_analysis()
            },
            'trends': self.get_performance_trends()
        }
    
    def export_results(self, format: str = 'json') -> Dict:
        """
        Export search results in specified format.
        
        Args:
            format: Export format ('json', 'csv')
            
        Returns:
            Dict: Exported data
        """
        if format == 'json':
            return {
                'search_results': [
                    {
                        'keyword': r.keyword,
                        'target_url': r.target_url,
                        'success': r.success,
                        'page_found': r.page_found,
                        'execution_time': r.execution_time,
                        'timestamp': r.timestamp,
                        'error': r.error
                    }
                    for r in self.search_results
                ],
                'statistics': self.get_statistics()
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_random_execution_stats(self) -> Dict:
        """
        Get statistics for random execution mode.
        
        Returns:
            Dict: Random execution statistics
        """
        if not self.search_results:
            return {}
        
        # 統計每個關鍵字被選中的次數
        keyword_counts = {}
        url_counts = {}
        
        for result in self.search_results:
            keyword = result.keyword
            url = result.target_url
            
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            url_counts[url] = url_counts.get(url, 0) + 1
        
        return {
            'total_executions': len(self.search_results),
            'keyword_distribution': keyword_counts,
            'url_distribution': url_counts,
            'most_used_keyword': max(keyword_counts.items(), key=lambda x: x[1]) if keyword_counts else None,
            'most_clicked_url': max(url_counts.items(), key=lambda x: x[1]) if url_counts else None,
            'unique_keywords_used': len(keyword_counts),
            'unique_urls_used': len(url_counts)
        }
    
    def clear_data(self) -> None:
        """Clear all stored data."""
        self.search_results.clear()
        self.keyword_stats.clear()
        self.url_stats.clear()
        self.total_searches = 0
        self.total_successful_searches = 0
        self.session_start_time = time.time()
        
        self.logger.info("Cleared all search analysis data")
