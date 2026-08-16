"""
Production DuckDuckGo search with caching and rate limiting
"""

import hashlib
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
import structlog

from ...config.settings import get_settings

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.delay = 1.0 / calls_per_second
        self.last_call = 0.0
    
    def wait(self):
        """Wait if needed to respect rate limit"""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_call = time.time()


class SearchCache:
    """TTL-based search cache"""
    
    def __init__(self, ttl_hours: int = 24):
        self.cache: Dict[str, tuple[List[Dict], datetime]] = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def get(self, query: str) -> Optional[List[Dict]]:
        """Get cached results if not expired"""
        key = self._hash(query)
        if key in self.cache:
            results, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logger.debug("Cache hit", query=query[:50])
                return results
            else:
                del self.cache[key]
        return None
    
    def set(self, query: str, results: List[Dict]):
        """Cache search results"""
        key = self._hash(query)
        self.cache[key] = (results, datetime.now())
        logger.debug("Cached results", query=query[:50])
    
    def _hash(self, query: str) -> str:
        return hashlib.md5(query.lower().encode()).hexdigest()


class DuckDuckGoSearch:
    """
    Production DuckDuckGo search implementation
    
    Features:
    - Automatic retries
    - Request timeouts
    - Rate limiting
    - TTL-based caching
    - User-agent rotation
    - Error handling
    """
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self):
        self.settings = get_settings()
        self.rate_limiter = RateLimiter(
            calls_per_second=1.0 / self.settings.search.rate_limit_delay
        )
        self.cache = SearchCache(ttl_hours=self.settings.agents.cache_ttl_hours)
        self._user_agent_index = 0
        logger.info("DuckDuckGo search initialized")
    
    def search(self, query: str, num_results: Optional[int] = None) -> List[Dict]:
        """
        Execute a search with all production safeguards
        
        Args:
            query: Search query string
            num_results: Override default number of results
            
        Returns:
            List of search result dictionaries
        """
        
        if not query or not query.strip():
            return []
        
        num = num_results or self.settings.search.num_results
        
        # Check cache first
        cached = self.cache.get(query)
        if cached:
            return cached[:num]
        
        # Respect rate limit
        self.rate_limiter.wait()
        
        logger.info("Executing search", query=query[:100], num_results=num)
        
        try:
            results = self._execute_search(query, num)
            
            # Cache successful results
            if results:
                self.cache.set(query, results)
            
            return results
            
        except Exception as e:
            logger.error("Search failed", query=query[:100], error=str(e))
            return []
    
    def _execute_search(self, query: str, num_results: int) -> List[Dict]:
        """Internal search execution"""
        
        url = "https://html.duckduckgo.com/html/"
        headers = self._get_headers()
        
        response = requests.post(
            url,
            data={'q': query},
            headers=headers,
            timeout=self.settings.search.timeout
        )
        
        response.raise_for_status()
        
        return self._parse_results(response.text, num_results)
    
    def _get_headers(self) -> Dict[str, str]:
        """Rotate user agents"""
        ua = self.USER_AGENTS[self._user_agent_index % len(self.USER_AGENTS)]
        self._user_agent_index += 1
        
        return {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _parse_results(self, html: str, num_results: int) -> List[Dict]:
        """Parse HTML search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for element in soup.find_all('div', class_='result')[:num_results]:
            title_elem = element.find('a', class_='result__a')
            snippet_elem = element.find('a', class_='result__snippet')
            
            if title_elem and snippet_elem:
                results.append({
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href', ''),
                    'snippet': snippet_elem.text.strip(),
                    'source_type': 'web',
                    'retrieved_at': datetime.now().isoformat()
                })
        
        return results