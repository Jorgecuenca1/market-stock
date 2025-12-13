"""
Service layer for coordinating scraping operations.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.db import transaction

from dashboard.models import (
    Stock, Index, StockPrice, IndexPrice, StockAnalysis,
    StockNews, MarketNews, ScrapingLog
)
from .yahoo_finance import YahooFinanceScraper
from .news_scraper import NewsAggregator
from .analysis_scraper import AnalysisAggregator

logger = logging.getLogger('scraper')


class ScrapingService:
    """Main service for coordinating all scraping operations."""

    def __init__(self):
        self.yahoo = YahooFinanceScraper()
        self.news = NewsAggregator()
        self.analysis = AnalysisAggregator()

    def initialize_stocks(self) -> None:
        """Initialize tracked stocks and indices from settings."""
        # Primary dashboard stocks
        for stock_config in settings.TRACKED_STOCKS:
            Stock.objects.update_or_create(
                symbol=stock_config['symbol'],
                defaults={
                    'name': stock_config['name'],
                    'sector': stock_config['sector'],
                    'is_active': True,
                }
            )
            logger.info(f"Initialized stock: {stock_config['symbol']}")

        # Secondary dashboard stocks
        for stock_config in getattr(settings, 'TRACKED_STOCKS_SECONDARY', []):
            Stock.objects.update_or_create(
                symbol=stock_config['symbol'],
                defaults={
                    'name': stock_config['name'],
                    'sector': stock_config['sector'],
                    'is_active': True,
                }
            )
            logger.info(f"Initialized secondary stock: {stock_config['symbol']}")

        for index_config in settings.TRACKED_INDICES:
            Index.objects.update_or_create(
                symbol=index_config['symbol'],
                defaults={
                    'name': index_config['name'],
                    'is_active': True,
                }
            )
            logger.info(f"Initialized index: {index_config['symbol']}")

    def update_prices(self) -> Dict[str, Any]:
        """Update prices for all tracked stocks and indices."""
        start_time = timezone.now()
        results = {'stocks': 0, 'indices': 0, 'errors': []}

        # Update stock prices
        for stock in Stock.objects.filter(is_active=True):
            try:
                data = self.yahoo.scrape(stock.symbol)
                if data.get('price'):
                    StockPrice.objects.create(
                        stock=stock,
                        price=Decimal(str(data['price'])),
                        change=Decimal(str(data.get('change') or 0)) if data.get('change') else None,
                        change_percent=Decimal(str(data.get('change_percent') or 0)) if data.get('change_percent') else None,
                        volume=data.get('volume'),
                        market_cap=Decimal(str(data.get('market_cap') or 0)) if data.get('market_cap') else None,
                        pe_ratio=Decimal(str(data.get('pe_trailing') or 0)) if data.get('pe_trailing') else None,
                        source='yahoo_finance',
                    )
                    results['stocks'] += 1
            except Exception as e:
                results['errors'].append(f"{stock.symbol}: {str(e)}")
                logger.error(f"Error updating price for {stock.symbol}: {e}")

        # Update index prices
        for index in Index.objects.filter(is_active=True):
            try:
                data = self.yahoo.get_index_data(index.symbol)
                if data.get('level'):
                    IndexPrice.objects.create(
                        index=index,
                        level=Decimal(str(data['level'])),
                        change=Decimal(str(data.get('change') or 0)) if data.get('change') else None,
                        change_percent=Decimal(str(data.get('change_percent') or 0)) if data.get('change_percent') else None,
                        source='yahoo_finance',
                    )
                    results['indices'] += 1
            except Exception as e:
                results['errors'].append(f"{index.symbol}: {str(e)}")
                logger.error(f"Error updating price for {index.symbol}: {e}")

        # Log scraping activity
        duration = (timezone.now() - start_time).total_seconds()
        ScrapingLog.objects.create(
            source='yahoo_finance',
            task_type='price',
            status='success' if not results['errors'] else 'partial',
            items_scraped=results['stocks'] + results['indices'],
            error_message='\n'.join(results['errors']) if results['errors'] else None,
            duration_seconds=duration,
        )

        return results

    def update_news(self) -> Dict[str, Any]:
        """Update news for all tracked stocks using Yahoo Finance only."""
        start_time = timezone.now()
        results = {'stocks': 0, 'articles': 0, 'errors': []}

        # Words that indicate garbage/navigation content
        garbage_keywords = [
            'skip to', 'main content', 'latin america', 'europe & middle east',
            'united states', 'world markets', 'latest news', 'sign in',
            'subscribe', 'menu', 'navigation', 'footer', 'header',
            'cookie', 'privacy', 'terms of', 'contact us'
        ]

        def is_valid_headline(headline):
            """Check if headline is a real news article."""
            if not headline or len(headline) < 20:
                return False
            headline_lower = headline.lower()
            for keyword in garbage_keywords:
                if keyword in headline_lower:
                    return False
            return True

        for stock in Stock.objects.filter(is_active=True):
            try:
                # Get news ONLY from Yahoo Finance (reliable source)
                yahoo_news = self.yahoo.get_news(stock.symbol, limit=15)

                for article in yahoo_news:
                    headline = article.get('title', '')

                    # Skip garbage headlines
                    if not is_valid_headline(headline):
                        continue

                    # Check if article already exists
                    if not StockNews.objects.filter(
                        stock=stock,
                        headline=headline
                    ).exists():
                        StockNews.objects.create(
                            stock=stock,
                            headline=headline,
                            summary=article.get('summary', ''),
                            url=article.get('link', ''),
                            source=article.get('publisher', 'Yahoo Finance'),
                            published_at=article.get('published_at'),
                        )
                        results['articles'] += 1

                results['stocks'] += 1

            except Exception as e:
                results['errors'].append(f"{stock.symbol}: {str(e)}")
                logger.error(f"Error updating news for {stock.symbol}: {e}")

        # Get general market news from major indices
        try:
            market_symbols = ['^GSPC', '^DJI', '^IXIC']
            for symbol in market_symbols:
                market_news = self.yahoo.get_news(symbol, limit=10)
                for article in market_news:
                    headline = article.get('title', '')

                    if not is_valid_headline(headline):
                        continue

                    if not MarketNews.objects.filter(headline=headline).exists():
                        MarketNews.objects.create(
                            headline=headline,
                            summary=article.get('summary', ''),
                            url=article.get('link', ''),
                            source=article.get('publisher', 'Yahoo Finance'),
                            category='market',
                            published_at=article.get('published_at'),
                        )
                        results['articles'] += 1
        except Exception as e:
            results['errors'].append(f"Market news: {str(e)}")
            logger.error(f"Error updating market news: {e}")

        # Log scraping activity
        duration = (timezone.now() - start_time).total_seconds()
        ScrapingLog.objects.create(
            source='news_aggregator',
            task_type='news',
            status='success' if not results['errors'] else 'partial',
            items_scraped=results['articles'],
            error_message='\n'.join(results['errors']) if results['errors'] else None,
            duration_seconds=duration,
        )

        return results

    def update_analysis(self) -> Dict[str, Any]:
        """Update analysis data for all tracked stocks."""
        start_time = timezone.now()
        results = {'stocks': 0, 'errors': []}

        for stock in Stock.objects.filter(is_active=True):
            try:
                data = self.analysis.scrape(stock.symbol)

                # Determine rating based on metrics
                rating = self._determine_rating(data)
                sentiment = self._determine_sentiment(data)

                # Generate conclusions
                conclusion_en = self._generate_conclusion_en(stock.symbol, data, rating)
                conclusion_es = self._generate_conclusion_es(stock.symbol, data, rating)

                StockAnalysis.objects.create(
                    stock=stock,
                    price=Decimal(str(data.get('price'))) if data.get('price') else None,
                    market_cap=data.get('market_cap'),
                    pe_trailing=Decimal(str(data.get('pe_trailing'))) if data.get('pe_trailing') else None,
                    pe_forward=Decimal(str(data.get('pe_forward'))) if data.get('pe_forward') else None,
                    peg_ratio=Decimal(str(data.get('peg_ratio'))) if data.get('peg_ratio') else None,
                    debt_equity=Decimal(str(data.get('debt_equity'))) if data.get('debt_equity') else None,
                    current_ratio=Decimal(str(data.get('current_ratio'))) if data.get('current_ratio') else None,
                    quick_ratio=Decimal(str(data.get('quick_ratio'))) if data.get('quick_ratio') else None,
                    cash=data.get('cash'),
                    total_debt=data.get('total_debt'),
                    net_cash=data.get('net_cash'),
                    free_cash_flow=data.get('free_cash_flow'),
                    gross_margin=Decimal(str(data.get('gross_margin'))) if data.get('gross_margin') else None,
                    operating_margin=Decimal(str(data.get('operating_margin'))) if data.get('operating_margin') else None,
                    net_margin=Decimal(str(data.get('net_margin'))) if data.get('net_margin') else None,
                    roe=Decimal(str(data.get('roe'))) if data.get('roe') else None,
                    dividend_yield=Decimal(str(data.get('dividend_yield'))) if data.get('dividend_yield') else None,
                    gf_score=data.get('gf_score'),
                    altman_z_score=Decimal(str(data.get('altman_z_score'))) if data.get('altman_z_score') else None,
                    piotroski_score=data.get('piotroski_score'),
                    price_target=data.get('price_target'),
                    analyst_rating=data.get('analyst_rating'),
                    rating=rating,
                    sentiment=sentiment,
                    conclusion_en=conclusion_en,
                    conclusion_es=conclusion_es,
                    sources=data.get('sources', []),
                    raw_data=data.get('raw_data', {}),
                )
                results['stocks'] += 1

            except Exception as e:
                results['errors'].append(f"{stock.symbol}: {str(e)}")
                logger.error(f"Error updating analysis for {stock.symbol}: {e}")

        # Log scraping activity
        duration = (timezone.now() - start_time).total_seconds()
        ScrapingLog.objects.create(
            source='analysis_aggregator',
            task_type='analysis',
            status='success' if not results['errors'] else 'partial',
            items_scraped=results['stocks'],
            error_message='\n'.join(results['errors']) if results['errors'] else None,
            duration_seconds=duration,
        )

        return results

    def _determine_rating(self, data: Dict) -> str:
        """
        Determine stock rating based on fundamental metrics.

        Scoring System (max 20 points):
        - PEG Ratio: up to 3 points (growth at reasonable price)
        - P/E Ratio: up to 3 points (valuation)
        - Debt/Equity: up to 3 points (financial health)
        - ROE: up to 3 points (profitability)
        - Current Ratio: up to 2 points (liquidity)
        - Profit Margins: up to 3 points (efficiency)
        - Price vs 52-week: up to 2 points (momentum)
        - Analyst Recommendation: up to 1 point
        """
        score = 0
        max_score = 20

        # 1. PEG Ratio (Price/Earnings to Growth) - max 3 points
        # PEG < 1 = undervalued, PEG 1-2 = fair, PEG > 2 = overvalued
        peg = data.get('peg_ratio')
        if peg is not None and peg > 0:
            if peg < 0.5:
                score += 3
            elif peg < 1:
                score += 2
            elif peg < 1.5:
                score += 1
            elif peg > 3:
                score -= 1

        # 2. P/E Ratio - max 3 points
        pe = data.get('pe_forward') or data.get('pe_trailing')
        if pe is not None and pe > 0:
            if pe < 12:
                score += 3
            elif pe < 18:
                score += 2
            elif pe < 25:
                score += 1
            elif pe > 40:
                score -= 1
            elif pe > 60:
                score -= 2

        # 3. Debt to Equity - max 3 points
        de = data.get('debt_equity')
        if de is not None:
            if de < 0.3:
                score += 3  # Very low debt
            elif de < 0.5:
                score += 2  # Low debt
            elif de < 1.0:
                score += 1  # Moderate debt
            elif de > 2.0:
                score -= 1  # High debt
            elif de > 3.0:
                score -= 2  # Very high debt

        # 4. ROE (Return on Equity) - max 3 points
        roe = data.get('roe')
        if roe is not None:
            if roe > 25:
                score += 3  # Excellent
            elif roe > 15:
                score += 2  # Good
            elif roe > 10:
                score += 1  # Average
            elif roe < 5:
                score -= 1  # Poor

        # 5. Current Ratio (Liquidity) - max 2 points
        current = data.get('current_ratio')
        if current is not None:
            if current > 2.0:
                score += 2  # Very liquid
            elif current > 1.5:
                score += 1  # Healthy
            elif current < 1.0:
                score -= 1  # Liquidity risk

        # 6. Profit Margins - max 3 points
        net_margin = data.get('net_margin')
        gross_margin = data.get('gross_margin')

        if net_margin is not None:
            if net_margin > 20:
                score += 2
            elif net_margin > 10:
                score += 1
            elif net_margin < 0:
                score -= 2

        if gross_margin is not None:
            if gross_margin > 50:
                score += 1
            elif gross_margin < 20:
                score -= 1

        # 7. Analyst Recommendation - max 1 point
        rec = data.get('analyst_rating')
        if rec:
            rec_lower = str(rec).lower()
            if 'buy' in rec_lower or 'strong' in rec_lower:
                score += 1
            elif 'sell' in rec_lower:
                score -= 1

        # Calculate percentage score
        score_percent = (score / max_score) * 100 if max_score > 0 else 50

        # Determine rating based on score percentage
        if score_percent >= 70:
            return 'STRONG_BUY'
        elif score_percent >= 50:
            return 'BUY'
        elif score_percent >= 30:
            return 'HOLD'
        elif score_percent >= 10:
            return 'SELL'
        else:
            return 'STRONG_SELL'

    def _determine_sentiment(self, data: Dict) -> str:
        """
        Determine overall sentiment based on multiple factors.

        Uses a weighted approach considering:
        - Rating (from _determine_rating)
        - Price momentum (52-week position)
        - Analyst consensus
        - Fundamental strength
        """
        # Get base rating
        rating = self._determine_rating(data)

        # Calculate momentum score
        momentum_score = 0

        # Check price vs moving averages (if available from raw data)
        raw = data.get('raw_data', {}).get('yahoo', {})

        price = raw.get('price') or raw.get('regularMarketPrice')
        fifty_day = raw.get('fifty_day_average') or raw.get('fiftyDayAverage')
        two_hundred_day = raw.get('two_hundred_day_average') or raw.get('twoHundredDayAverage')

        if price and fifty_day:
            if price > fifty_day * 1.05:
                momentum_score += 1  # Above 50-day MA
            elif price < fifty_day * 0.95:
                momentum_score -= 1  # Below 50-day MA

        if price and two_hundred_day:
            if price > two_hundred_day * 1.1:
                momentum_score += 1  # Strong uptrend
            elif price < two_hundred_day * 0.9:
                momentum_score -= 1  # Downtrend

        # Combine rating with momentum
        if rating in ['STRONG_BUY', 'BUY']:
            if momentum_score >= 1:
                return 'BULLISH'
            elif momentum_score <= -1:
                return 'NEUTRAL'  # Good fundamentals but weak momentum
            return 'BULLISH'
        elif rating in ['SELL', 'STRONG_SELL']:
            if momentum_score >= 1:
                return 'NEUTRAL'  # Weak fundamentals but positive momentum
            return 'BEARISH'
        else:  # HOLD
            if momentum_score >= 2:
                return 'BULLISH'
            elif momentum_score <= -2:
                return 'BEARISH'
            return 'NEUTRAL'

    def _generate_conclusion_en(self, symbol: str, data: Dict, rating: str) -> str:
        """Generate analysis conclusion in English."""
        parts = []

        pe = data.get('pe_trailing')
        if pe:
            if pe > 50:
                parts.append(f"High valuation at {pe:.1f}x P/E.")
            elif pe < 15:
                parts.append(f"Attractive valuation at {pe:.1f}x P/E.")

        de = data.get('debt_equity')
        if de is not None:
            if de < 0.3:
                parts.append("Excellent balance sheet with minimal debt.")
            elif de < 1:
                parts.append("Healthy debt levels.")
            elif de > 2:
                parts.append("High leverage - monitor debt levels.")

        roe = data.get('roe')
        if roe and roe > 20:
            parts.append(f"Strong profitability with {roe:.1f}% ROE.")

        div = data.get('dividend_yield')
        if div and div > 2:
            parts.append(f"{div:.2f}% dividend yield provides income.")

        rating_text = {
            'STRONG_BUY': 'STRONG BUY',
            'BUY': 'BUY',
            'HOLD': 'HOLD',
            'SELL': 'SELL',
            'STRONG_SELL': 'STRONG SELL',
        }

        if parts:
            return f"{rating_text.get(rating, 'HOLD')}: {' '.join(parts)}"
        return f"{rating_text.get(rating, 'HOLD')}: Metrics within normal ranges."

    def _generate_conclusion_es(self, symbol: str, data: Dict, rating: str) -> str:
        """Generate analysis conclusion in Spanish."""
        parts = []

        pe = data.get('pe_trailing')
        if pe:
            if pe > 50:
                parts.append(f"Valoración alta a {pe:.1f}x P/E.")
            elif pe < 15:
                parts.append(f"Valoración atractiva a {pe:.1f}x P/E.")

        de = data.get('debt_equity')
        if de is not None:
            if de < 0.3:
                parts.append("Excelente balance con deuda mínima.")
            elif de < 1:
                parts.append("Niveles de deuda saludables.")
            elif de > 2:
                parts.append("Alto apalancamiento - monitorear deuda.")

        roe = data.get('roe')
        if roe and roe > 20:
            parts.append(f"Fuerte rentabilidad con {roe:.1f}% ROE.")

        div = data.get('dividend_yield')
        if div and div > 2:
            parts.append(f"{div:.2f}% de dividendo proporciona ingresos.")

        rating_text = {
            'STRONG_BUY': 'COMPRA FUERTE',
            'BUY': 'COMPRA',
            'HOLD': 'MANTENER',
            'SELL': 'VENTA',
            'STRONG_SELL': 'VENTA FUERTE',
        }

        if parts:
            return f"{rating_text.get(rating, 'MANTENER')}: {' '.join(parts)}"
        return f"{rating_text.get(rating, 'MANTENER')}: Métricas dentro de rangos normales."

    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Clean up old data to prevent database bloat."""
        cutoff = timezone.now() - timedelta(days=days)

        deleted = {
            'prices': StockPrice.objects.filter(timestamp__lt=cutoff).delete()[0],
            'index_prices': IndexPrice.objects.filter(timestamp__lt=cutoff).delete()[0],
            'logs': ScrapingLog.objects.filter(timestamp__lt=cutoff).delete()[0],
        }

        # Keep more recent analysis (90 days)
        analysis_cutoff = timezone.now() - timedelta(days=90)
        deleted['analyses'] = StockAnalysis.objects.filter(timestamp__lt=analysis_cutoff).delete()[0]

        # Keep news for 60 days
        news_cutoff = timezone.now() - timedelta(days=60)
        deleted['stock_news'] = StockNews.objects.filter(created_at__lt=news_cutoff).delete()[0]
        deleted['market_news'] = MarketNews.objects.filter(created_at__lt=news_cutoff).delete()[0]

        logger.info(f"Cleanup completed: {deleted}")
        return deleted
