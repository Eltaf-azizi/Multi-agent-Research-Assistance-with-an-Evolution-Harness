"""
DuckDuckGo web search tool (FREE, no API key needed)
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict


class WebSearchTool:
    """
    Free web search using DuckDuckGo's HTML interface.
    No API key required.
    """
    
    def __init__(self):
        self.cache = {}
        self.search_count = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        print("✅ WebSearch tool ready")
    
    def search(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo for a query.
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of dicts with 'title', 'url', 'snippet'
        """
        # Check cache
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            print(f"      📦 Cached: {query[:50]}...")
            return self.cache[cache_key][:num_results]
        
        self.search_count += 1
        print(f"      🔍 Searching: {query[:60]}...")
        
        try:
            url = "https://html.duckduckgo.com/html/"
            response = requests.post(
                url,
                data={'q': query},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"      ⚠️  Search returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for element in soup.find_all('div', class_='result')[:num_results]:
                title_elem = element.find('a', class_='result__a')
                snippet_elem = element.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    results.append({
                        'title': title_elem.text.strip(),
                        'url': title_elem.get('href', 'No URL'),
                        'snippet': snippet_elem.text.strip()
                    })
            
            # Cache results
            self.cache[cache_key] = results
            
            print(f"      ✅ Found {len(results)} results")
            
            # Rate limiting
            time.sleep(1)
            
            return results
            
        except Exception as e:
            print(f"      ❌ Search error: {e}")
            return []