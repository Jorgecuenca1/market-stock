"""
News scraper for multiple financial news sources.
Uses Yahoo Finance as primary source for reliable news with real dates.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote

import requests
from bs4 import BeautifulSoup
import yfinance as yf

from .base_scraper import BaseScraper

logger = logging.getLogger('scraper')


class NewsAggregator(BaseScraper):
    """Aggregates news from Yahoo Finance (primary) and web sources."""

    def __init__(self):
        super().__init__('News Aggregator')

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Scrape news primarily from Yahoo Finance for reliable data."""
        all_news = []

        # Primary source: Yahoo Finance (has real dates and working URLs)
        try:
            ticker = yf.Ticker(symbol)
            yahoo_news = ticker.news or []

            for article in yahoo_news[:15]:
                published_time = article.get('providerPublishTime')
                if published_time:
                    published_at = datetime.fromtimestamp(published_time)
                else:
                    published_at = None

                all_news.append({
                    'headline': article.get('title', ''),
                    'url': article.get('link', ''),
                    'source': article.get('publisher', 'Yahoo Finance'),
                    'published_at': published_at,
                })
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance news for {symbol}: {e}")

        return {
            'symbol': symbol,
            'news_count': len(all_news),
            'news': all_news,
        }

    def get_market_news(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get general market news from major indices."""
        all_news = []

        # Get news from major market indices
        market_symbols = ['^GSPC', '^DJI', '^IXIC']

        for symbol in market_symbols:
            try:
                ticker = yf.Ticker(symbol)
                news = ticker.news or []

                for article in news[:10]:
                    published_time = article.get('providerPublishTime')
                    if published_time:
                        published_at = datetime.fromtimestamp(published_time)
                    else:
                        published_at = None

                    headline = article.get('title', '')
                    # Avoid duplicates
                    if not any(n['headline'] == headline for n in all_news):
                        all_news.append({
                            'headline': headline,
                            'url': article.get('link', ''),
                            'source': article.get('publisher', 'Yahoo Finance'),
                            'category': 'market',
                            'published_at': published_at,
                        })
            except Exception as e:
                logger.error(f"Error getting market news from {symbol}: {e}")

        # Sort by date, most recent first
        all_news.sort(key=lambda x: x.get('published_at') or datetime.min, reverse=True)

        return all_news[:limit]


class InvestingScraper(BaseScraper):
    """Scraper for Investing.com news - good source with real dates."""

    def __init__(self):
        super().__init__('Investing.com')
        self.base_url = 'https://www.investing.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        return {'news': self.get_stock_news(symbol)}

    def get_stock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news for a specific stock from Investing.com."""
        url = f"{self.base_url}/equities/{symbol.lower()}-news"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            # Find news articles
            articles = soup.find_all('article', class_=re.compile(r'js-article-item|articleItem'))
            for article in articles[:10]:
                # Get headline
                title_elem = article.find(['a', 'h3', 'h4'], class_=re.compile(r'title|headline'))
                if not title_elem:
                    title_elem = article.find('a')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = urljoin(self.base_url, link)

                    # Get date
                    date_elem = article.find(['time', 'span'], class_=re.compile(r'date|time'))
                    published_at = None
                    if date_elem:
                        date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                        try:
                            if 'ago' in date_str.lower():
                                published_at = datetime.now()
                            else:
                                published_at = datetime.strptime(date_str[:10], '%Y-%m-%d')
                        except:
                            published_at = datetime.now()

                    if title and len(title) > 10:
                        news_items.append({
                            'headline': title,
                            'url': link,
                            'source': 'Investing.com',
                            'published_at': published_at,
                        })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Investing.com for {symbol}: {e}")
            return []

    def get_market_news(self) -> List[Dict[str, Any]]:
        """Get general market news from Investing.com."""
        url = f"{self.base_url}/news/stock-market-news"
        response = self._make_request(url)

        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = []

            articles = soup.find_all('article', class_=re.compile(r'js-article-item|articleItem'))
            for article in articles[:15]:
                title_elem = article.find(['a', 'h3', 'h4'], class_=re.compile(r'title|headline'))
                if not title_elem:
                    title_elem = article.find('a')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = urljoin(self.base_url, link)

                    date_elem = article.find(['time', 'span'], class_=re.compile(r'date|time'))
                    published_at = None
                    if date_elem:
                        date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                        try:
                            if 'ago' in date_str.lower():
                                published_at = datetime.now()
                            else:
                                published_at = datetime.strptime(date_str[:10], '%Y-%m-%d')
                        except:
                            published_at = datetime.now()

                    if title and len(title) > 10:
                        news_items.append({
                            'headline': title,
                            'url': link,
                            'source': 'Investing.com',
                            'category': 'market',
                            'published_at': published_at,
                        })

            return news_items
        except Exception as e:
            logger.error(f"Error parsing Investing.com market news: {e}")
            return []


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
