"""
News scraper for multiple financial news sources.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote

import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger('scraper')


class NewsAggregator(BaseScraper):
    """Aggregates news from multiple financial sources."""

    def __init__(self):
        super().__init__('News Aggregator')
        self.sources = {
            'cnbc': CNBCScraper(),
            'reuters': ReutersScraper(),
            'marketwatch': MarketWatchScraper(),
            'seeking_alpha': SeekingAlphaScraper(),
            'benzinga': BenzingaScraper(),
        }

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Scrape news from all sources for a symbol."""
        all_news = []
        for source_name, scraper in self.sources.items():
            try:
                news = scraper.get_stock_news(symbol)
                all_news.extend(news)
            except Exception as e:
                logger.error(f"Error scraping {source_name} for {symbol}: {e}")

        # Sort by date, most recent first
        all_news.sort(key=lambda x: x.get('published_at') or datetime.min, reverse=True)

        return {
            'symbol': symbol,
            'news_count': len(all_news),
            'news': all_news[:20],  # Limit to 20 most recent
        }

    def get_market_news(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get general market news from all sources."""
        all_news = []
        for source_name, scraper in self.sources.items():
            try:
                news = scraper.get_market_news()
                all_news.extend(news)
            except Exception as e:
                logger.error(f"Error scraping market news from {source_name}: {e}")

        # Sort by date, most recent first
        all_news.sort(key=lambda x: x.get('published_at') or datetime.min, reverse=True)

        return all_news[:limit]


class CNBCScraper(BaseScraper):
    """Scraper for CNBC news."""

    def __init__(self):
        super().__init__('CNBC')
        self.base_url = 'https://www.cnbc.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        return {'news': self.get_stock_news(symbol)}

    def get_stock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news for a specific stock from CNBC."""
        url = f"{self.base_url}/quotes/{symbol}"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            # Find news articles
            articles = soup.find_all('a', class_=re.compile(r'Card-title|LatestNews'))
            for article in articles[:10]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'CNBC',
                        'published_at': datetime.now(),  # Would need to extract actual date
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing CNBC for {symbol}: {e}")
            return []

    def get_market_news(self) -> List[Dict[str, Any]]:
        """Get general market news from CNBC."""
        url = f"{self.base_url}/markets/"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all(['a', 'div'], class_=re.compile(r'Card|RiverHeadline|LatestNews'))
            for article in articles[:15]:
                title_elem = article.find('a') if article.name == 'div' else article
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = urljoin(self.base_url, link)

                    if title and len(title) > 10:
                        news_items.append({
                            'headline': title,
                            'url': link,
                            'source': 'CNBC',
                            'category': 'market',
                            'published_at': datetime.now(),
                        })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing CNBC market news: {e}")
            return []


class ReutersScraper(BaseScraper):
    """Scraper for Reuters news."""

    def __init__(self):
        super().__init__('Reuters')
        self.base_url = 'https://www.reuters.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        return {'news': self.get_stock_news(symbol)}

    def get_stock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news for a specific stock from Reuters."""
        url = f"{self.base_url}/markets/companies/{symbol}.O"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', {'data-testid': re.compile(r'Heading|Title')})
            for article in articles[:10]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'Reuters',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Reuters for {symbol}: {e}")
            return []

    def get_market_news(self) -> List[Dict[str, Any]]:
        """Get general market news from Reuters."""
        url = f"{self.base_url}/markets/"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', {'data-testid': re.compile(r'Heading|Title')})
            for article in articles[:15]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title and len(title) > 10:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'Reuters',
                        'category': 'market',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Reuters market news: {e}")
            return []


class MarketWatchScraper(BaseScraper):
    """Scraper for MarketWatch news."""

    def __init__(self):
        super().__init__('MarketWatch')
        self.base_url = 'https://www.marketwatch.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        return {'news': self.get_stock_news(symbol)}

    def get_stock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news for a specific stock from MarketWatch."""
        url = f"{self.base_url}/investing/stock/{symbol}"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', class_=re.compile(r'link|headline'))
            for article in articles[:10]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title and len(title) > 10:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'MarketWatch',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing MarketWatch for {symbol}: {e}")
            return []

    def get_market_news(self) -> List[Dict[str, Any]]:
        """Get general market news from MarketWatch."""
        url = f"{self.base_url}/latest-news"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', class_=re.compile(r'link|headline'))
            for article in articles[:15]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title and len(title) > 10:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'MarketWatch',
                        'category': 'market',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing MarketWatch news: {e}")
            return []


class SeekingAlphaScraper(BaseScraper):
    """Scraper for Seeking Alpha news."""

    def __init__(self):
        super().__init__('Seeking Alpha')
        self.base_url = 'https://seekingalpha.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        return {'news': self.get_stock_news(symbol)}

    def get_stock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news for a specific stock from Seeking Alpha."""
        url = f"{self.base_url}/symbol/{symbol}/news"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', {'data-test-id': 'post-list-item-title'})
            for article in articles[:10]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'Seeking Alpha',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Seeking Alpha for {symbol}: {e}")
            return []

    def get_market_news(self) -> List[Dict[str, Any]]:
        """Get general market news from Seeking Alpha."""
        url = f"{self.base_url}/market-news"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', {'data-test-id': 'post-list-item-title'})
            for article in articles[:15]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'Seeking Alpha',
                        'category': 'market',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Seeking Alpha market news: {e}")
            return []


class BenzingaScraper(BaseScraper):
    """Scraper for Benzinga news."""

    def __init__(self):
        super().__init__('Benzinga')
        self.base_url = 'https://www.benzinga.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        return {'news': self.get_stock_news(symbol)}

    def get_stock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news for a specific stock from Benzinga."""
        url = f"{self.base_url}/stock/{symbol}"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', class_=re.compile(r'title|headline'))
            for article in articles[:10]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title and len(title) > 10:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'Benzinga',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Benzinga for {symbol}: {e}")
            return []

    def get_market_news(self) -> List[Dict[str, Any]]:
        """Get general market news from Benzinga."""
        url = f"{self.base_url}/markets"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('a', class_=re.compile(r'title|headline'))
            for article in articles[:15]:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)

                if title and len(title) > 10:
                    news_items.append({
                        'headline': title,
                        'url': link,
                        'source': 'Benzinga',
                        'category': 'market',
                        'published_at': datetime.now(),
                    })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Benzinga market news: {e}")
            return []
