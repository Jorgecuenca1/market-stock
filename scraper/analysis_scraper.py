"""
Analysis data scraper for financial metrics from multiple sources.
Uses Yahoo Finance as primary source with additional web scraping.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from .yahoo_finance import YahooFinanceScraper

logger = logging.getLogger('scraper')


class AnalysisAggregator(BaseScraper):
    """Aggregates analysis data from multiple sources."""

    def __init__(self):
        super().__init__('Analysis Aggregator')
        self.yahoo = YahooFinanceScraper()
        self.gurufocus = GuruFocusScraper()
        self.stockanalysis = StockAnalysisScraper()

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive analysis data for a symbol."""
        # Primary data from Yahoo Finance
        yahoo_data = self.yahoo.scrape(symbol)

        # Additional metrics from other sources
        gf_data = self.gurufocus.scrape(symbol)
        sa_data = self.stockanalysis.scrape(symbol)

        # Merge all data
        analysis = self._merge_data(yahoo_data, gf_data, sa_data)
        analysis['symbol'] = symbol
        analysis['timestamp'] = datetime.now().isoformat()
        analysis['sources'] = ['Yahoo Finance', 'GuruFocus', 'StockAnalysis']

        return analysis

    def _merge_data(self, yahoo: Dict, gf: Dict, sa: Dict) -> Dict[str, Any]:
        """Merge data from multiple sources, preferring most reliable."""
        merged = {
            # Price data (Yahoo is most reliable for real-time)
            'price': yahoo.get('price'),
            'market_cap': self._format_large_number(yahoo.get('market_cap')),

            # Valuation (use Yahoo as primary)
            'pe_trailing': yahoo.get('pe_trailing'),
            'pe_forward': yahoo.get('pe_forward'),
            'peg_ratio': yahoo.get('peg_ratio') or gf.get('peg_ratio'),

            # Balance sheet
            'debt_equity': yahoo.get('debt_to_equity'),
            'current_ratio': yahoo.get('current_ratio'),
            'quick_ratio': yahoo.get('quick_ratio'),

            # Cash and debt
            'cash': self._format_large_number(yahoo.get('total_cash')),
            'total_debt': self._format_large_number(yahoo.get('total_debt')),
            'free_cash_flow': self._format_large_number(yahoo.get('free_cash_flow')),

            # Profitability
            'gross_margin': self._to_percent(yahoo.get('gross_margin')),
            'operating_margin': self._to_percent(yahoo.get('operating_margin')),
            'net_margin': self._to_percent(yahoo.get('profit_margin')),
            'roe': self._to_percent(yahoo.get('roe')),

            # Dividend
            'dividend_yield': self._to_percent(yahoo.get('dividend_yield')),

            # Analyst data
            'price_target': self._format_price_target(yahoo),
            'analyst_rating': yahoo.get('recommendation_key'),

            # Scores from GuruFocus
            'gf_score': gf.get('gf_score'),
            'altman_z_score': gf.get('altman_z_score'),
            'piotroski_score': gf.get('piotroski_score'),

            # Additional from StockAnalysis
            'interest_coverage': sa.get('interest_coverage'),

            # Company info
            'name': yahoo.get('name'),
            'sector': yahoo.get('sector'),
            'industry': yahoo.get('industry'),
            'description': yahoo.get('description'),
            'beta': yahoo.get('beta'),

            # Raw data for reference
            'raw_data': {
                'yahoo': yahoo,
                'gurufocus': gf,
                'stockanalysis': sa,
            }
        }

        # Calculate net cash
        if yahoo.get('total_cash') and yahoo.get('total_debt'):
            net = yahoo.get('total_cash', 0) - yahoo.get('total_debt', 0)
            merged['net_cash'] = self._format_large_number(net)

        return merged

    def _format_large_number(self, value: Optional[float]) -> Optional[str]:
        """Format large numbers with B/M/K suffix."""
        if value is None:
            return None

        try:
            value = float(value)
            if abs(value) >= 1e12:
                return f"${value/1e12:.2f}T"
            elif abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"${value/1e3:.2f}K"
            else:
                return f"${value:.2f}"
        except (ValueError, TypeError):
            return None

    def _to_percent(self, value: Optional[float]) -> Optional[float]:
        """Convert decimal to percentage."""
        if value is None:
            return None
        try:
            return round(float(value) * 100, 2)
        except (ValueError, TypeError):
            return None

    def _format_price_target(self, yahoo: Dict) -> Optional[str]:
        """Format price target with upside/downside."""
        target = yahoo.get('target_mean_price')
        price = yahoo.get('price')

        if target and price and price > 0:
            change = ((target - price) / price) * 100
            sign = '+' if change > 0 else ''
            return f"${target:.2f} ({sign}{change:.1f}%)"
        elif target:
            return f"${target:.2f}"
        return None


class GuruFocusScraper(BaseScraper):
    """Scraper for GuruFocus financial metrics."""

    def __init__(self):
        super().__init__('GuruFocus')
        self.base_url = 'https://www.gurufocus.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Get GF Score and other metrics from GuruFocus."""
        url = f"{self.base_url}/stock/{symbol}/summary"
        response = self._make_request(url)

        if not response:
            return {}

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            data = {}

            # Try to extract GF Score
            gf_score_elem = soup.find(text=re.compile(r'GF Score'))
            if gf_score_elem:
                parent = gf_score_elem.find_parent()
                if parent:
                    score_text = parent.get_text()
                    match = re.search(r'(\d+)/100', score_text)
                    if match:
                        data['gf_score'] = f"{match.group(1)}/100"

            # Try to extract Altman Z-Score
            z_score_elem = soup.find(text=re.compile(r'Altman Z-Score'))
            if z_score_elem:
                parent = z_score_elem.find_parent()
                if parent:
                    score_text = parent.get_text()
                    match = re.search(r'(\d+\.?\d*)', score_text)
                    if match:
                        data['altman_z_score'] = float(match.group(1))

            # Try to extract Piotroski F-Score
            f_score_elem = soup.find(text=re.compile(r'Piotroski F-Score'))
            if f_score_elem:
                parent = f_score_elem.find_parent()
                if parent:
                    score_text = parent.get_text()
                    match = re.search(r'(\d+)/9', score_text)
                    if match:
                        data['piotroski_score'] = f"{match.group(1)}/9"

            # PEG Ratio
            peg_elem = soup.find(text=re.compile(r'PEG Ratio'))
            if peg_elem:
                parent = peg_elem.find_parent()
                if parent:
                    text = parent.get_text()
                    match = re.search(r'(\d+\.?\d*)', text)
                    if match:
                        data['peg_ratio'] = float(match.group(1))

            return data

        except Exception as e:
            logger.error(f"Error parsing GuruFocus for {symbol}: {e}")
            return {}


class StockAnalysisScraper(BaseScraper):
    """Scraper for StockAnalysis.com metrics."""

    def __init__(self):
        super().__init__('StockAnalysis')
        self.base_url = 'https://stockanalysis.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Get financial metrics from StockAnalysis."""
        url = f"{self.base_url}/stocks/{symbol.lower()}/financials/ratios/"
        response = self._make_request(url)

        if not response:
            return {}

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            data = {}

            # Try to extract Interest Coverage
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        if 'Interest Coverage' in label:
                            value = cells[1].get_text(strip=True)
                            try:
                                data['interest_coverage'] = float(value.replace(',', ''))
                            except ValueError:
                                pass

            return data

        except Exception as e:
            logger.error(f"Error parsing StockAnalysis for {symbol}: {e}")
            return {}


class SimplyWallStScraper(BaseScraper):
    """Scraper for Simply Wall St data (limited without API)."""

    def __init__(self):
        super().__init__('Simply Wall St')
        self.base_url = 'https://simplywall.st'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Get available data from Simply Wall St."""
        # Simply Wall St requires JavaScript rendering
        # Return empty dict - would need Selenium for full scraping
        return {}


class MorningstarScraper(BaseScraper):
    """Scraper for Morningstar data."""

    def __init__(self):
        super().__init__('Morningstar')
        self.base_url = 'https://www.morningstar.com'

    def scrape(self, symbol: str) -> Dict[str, Any]:
        """Get financial metrics from Morningstar."""
        url = f"{self.base_url}/stocks/xnas/{symbol.lower()}/quote"
        response = self._make_request(url)

        if not response:
            return {}

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            data = {}

            # Extract available metrics
            # Morningstar structure varies, basic extraction
            stats = soup.find_all(class_=re.compile(r'stat|metric'))
            for stat in stats:
                label_elem = stat.find(class_=re.compile(r'label|name'))
                value_elem = stat.find(class_=re.compile(r'value|number'))
                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    data[label] = value

            return data

        except Exception as e:
            logger.error(f"Error parsing Morningstar for {symbol}: {e}")
            return {}
