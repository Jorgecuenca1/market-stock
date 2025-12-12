"""
Management command to clean garbage news from database.
"""
from django.core.management.base import BaseCommand
from dashboard.models import StockNews, MarketNews


class Command(BaseCommand):
    help = 'Clean garbage news entries from database'

    def handle(self, *args, **options):
        # Words that indicate garbage/navigation content
        garbage_keywords = [
            'skip to', 'main content', 'latin america', 'europe & middle east',
            'united states', 'world markets', 'latest news', 'sign in',
            'subscribe', 'menu', 'navigation', 'footer', 'header',
            'cookie', 'privacy', 'terms of', 'contact us', 'marketwatch'
        ]

        deleted_stock_news = 0
        deleted_market_news = 0

        # Clean StockNews
        for news in StockNews.objects.all():
            headline_lower = news.headline.lower()
            is_garbage = False

            # Check for garbage keywords
            for keyword in garbage_keywords:
                if keyword in headline_lower:
                    is_garbage = True
                    break

            # Check for too short headlines
            if len(news.headline) < 20:
                is_garbage = True

            if is_garbage:
                self.stdout.write(f"Deleting: {news.headline[:50]}...")
                news.delete()
                deleted_stock_news += 1

        # Clean MarketNews
        for news in MarketNews.objects.all():
            headline_lower = news.headline.lower()
            is_garbage = False

            for keyword in garbage_keywords:
                if keyword in headline_lower:
                    is_garbage = True
                    break

            if len(news.headline) < 20:
                is_garbage = True

            if is_garbage:
                self.stdout.write(f"Deleting: {news.headline[:50]}...")
                news.delete()
                deleted_market_news += 1

        self.stdout.write(self.style.SUCCESS(
            f"Cleaned {deleted_stock_news} stock news and {deleted_market_news} market news"
        ))
