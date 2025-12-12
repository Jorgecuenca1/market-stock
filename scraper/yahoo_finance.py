"""
Yahoo Finance scraper using yfinance library.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

import yfinance as yf

from .base_scraper import BaseScraper

logger = logging.getLogger('scraper')


class YahooFinanceScraper(BaseScraper):
    """Scraper for Yahoo Finance data using yfinance library."""

    def __init__(self):
        super().__init__('Yahoo Finance')

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'source': self.source_name,
                'timestamp': datetime.now().isoformat(),

                # Price data
                'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'previous_close': info.get('previousClose'),
                'open': info.get('open') or info.get('regularMarketOpen'),
                'day_high': info.get('dayHigh') or info.get('regularMarketDayHigh'),
                'day_low': info.get('dayLow') or info.get('regularMarketDayLow'),
                'volume': info.get('volume') or info.get('regularMarketVolume'),
                'avg_volume': info.get('averageVolume'),

                # Market data
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),

                # Valuation
                'pe_trailing': info.get('trailingPE'),
                'pe_forward': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'ev_to_revenue': info.get('enterpriseToRevenue'),
                'ev_to_ebitda': info.get('enterpriseToEbitda'),

                # Profitability
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),

                # Balance sheet
                'total_cash': info.get('totalCash'),
                'total_debt': info.get('totalDebt'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),

                # Cash flow
                'free_cash_flow': info.get('freeCashflow'),
                'operating_cash_flow': info.get('operatingCashflow'),

                # Dividend
                'dividend_rate': info.get('dividendRate'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'ex_dividend_date': info.get('exDividendDate'),

                # Analyst data
                'target_high_price': info.get('targetHighPrice'),
                'target_low_price': info.get('targetLowPrice'),
                'target_mean_price': info.get('targetMeanPrice'),
                'target_median_price': info.get('targetMedianPrice'),
                'recommendation_key': info.get('recommendationKey'),
                'recommendation_mean': info.get('recommendationMean'),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),

                # Company info
                'name': info.get('longName') or info.get('shortName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'country': info.get('country'),
                'website': info.get('website'),
                'description': info.get('longBusinessSummary'),

                # 52-week data
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_day_average': info.get('fiftyDayAverage'),
                'two_hundred_day_average': info.get('twoHundredDayAverage'),

                # Revenue and earnings
                'revenue': info.get('totalRevenue'),
                'revenue_per_share': info.get('revenuePerShare'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),

                # Beta
                'beta': info.get('beta'),
            }
        except Exception as e:
            logger.error(f"Error scraping {symbol} from Yahoo Finance: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def get_index_data(self, symbol: str) -> Dict[str, Any]:
        """Get index data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'source': self.source_name,
                'timestamp': datetime.now().isoformat(),
                'level': info.get('regularMarketPrice') or info.get('previousClose'),
                'previous_close': info.get('previousClose'),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'day_high': info.get('regularMarketDayHigh'),
                'day_low': info.get('regularMarketDayLow'),
                'volume': info.get('regularMarketVolume'),
                'name': info.get('shortName'),
            }
        except Exception as e:
            logger.error(f"Error scraping index {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def get_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news for a stock from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            results = []
            for article in news[:limit]:
                # New yfinance format has nested 'content' structure
                content = article.get('content', article)

                title = content.get('title', '')
                if not title:
                    continue

                # Get URL from canonicalUrl or clickThroughUrl
                url = ''
                if content.get('canonicalUrl'):
                    url = content['canonicalUrl'].get('url', '')
                elif content.get('clickThroughUrl'):
                    url = content['clickThroughUrl'].get('url', '')

                # Get publisher
                publisher = 'Yahoo Finance'
                if content.get('provider'):
                    publisher = content['provider'].get('displayName', 'Yahoo Finance')

                # Get published date
                published_at = None
                pub_date = content.get('pubDate')
                if pub_date:
                    try:
                        # Format: '2025-11-04T23:18:53Z'
                        published_at = datetime.strptime(pub_date, '%Y-%m-%dT%H:%M:%SZ')
                    except:
                        pass

                results.append({
                    'title': title,
                    'publisher': publisher,
                    'link': url,
                    'published_at': published_at,
                    'summary': content.get('summary', ''),
                    'source': publisher,
                })
            return results
        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {e}")
            return []

    def get_historical_prices(self, symbol: str, period: str = '1mo') -> List[Dict[str, Any]]:
        """Get historical price data."""
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)

            results = []
            for date, row in history.iterrows():
                results.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                })
            return results
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []
