"""
Base scraper class with common functionality.
"""
import logging
import time
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger('scraper')


class BaseScraper(ABC):
    """Base class for all scrapers."""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.session = self._create_session()
        self.last_request_time = None
        self.min_request_interval = 1.0  # seconds between requests

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

        session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        return session

    def _rate_limit(self):
        """Implement rate limiting between requests."""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                sleep_time = self.min_request_interval - elapsed + random.uniform(0.1, 0.5)
                time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Optional[Dict] = None,
                      headers: Optional[Dict] = None, timeout: int = 30) -> Optional[requests.Response]:
        """Make an HTTP request with rate limiting and error handling."""
        self._rate_limit()

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None

    @abstractmethod
    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Scrape data for a given symbol. To be implemented by subclasses."""
        pass

    def scrape_multiple(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Scrape data for multiple symbols."""
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.scrape(symbol)
            except Exception as e:
                logger.error(f"Error scraping {symbol} from {self.source_name}: {e}")
                results[symbol] = {'error': str(e)}
        return results
