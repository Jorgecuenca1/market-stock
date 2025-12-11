"""
Management command to run the background scheduler for automatic updates.
"""
import time
import threading
import signal
import sys
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from scraper.services import ScrapingService


class Command(BaseCommand):
    help = 'Run background scheduler for automatic data updates'

    def __init__(self):
        super().__init__()
        self.running = True
        self.service = ScrapingService()

    def add_arguments(self, parser):
        parser.add_argument(
            '--price-interval',
            type=int,
            default=60,
            help='Price update interval in seconds (default: 60)',
        )
        parser.add_argument(
            '--news-interval',
            type=int,
            default=300,
            help='News update interval in seconds (default: 300)',
        )
        parser.add_argument(
            '--analysis-interval',
            type=int,
            default=3600,
            help='Analysis update interval in seconds (default: 3600)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Market Stock Scheduler...'))
        self.stdout.write(f"  Price updates: every {options['price_interval']}s")
        self.stdout.write(f"  News updates: every {options['news_interval']}s")
        self.stdout.write(f"  Analysis updates: every {options['analysis_interval']}s")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Initialize stocks if not done
        self.service.initialize_stocks()

        # Track last update times
        last_price_update = 0
        last_news_update = 0
        last_analysis_update = 0

        while self.running:
            current_time = time.time()

            try:
                # Update prices
                if current_time - last_price_update >= options['price_interval']:
                    self.stdout.write(f"[{datetime.now().strftime('%H:%M:%S')}] Updating prices...")
                    results = self.service.update_prices()
                    self.stdout.write(f"  -> {results['stocks']} stocks, {results['indices']} indices")
                    last_price_update = current_time

                # Update news
                if current_time - last_news_update >= options['news_interval']:
                    self.stdout.write(f"[{datetime.now().strftime('%H:%M:%S')}] Updating news...")
                    results = self.service.update_news()
                    self.stdout.write(f"  -> {results['articles']} new articles")
                    last_news_update = current_time

                # Update analysis
                if current_time - last_analysis_update >= options['analysis_interval']:
                    self.stdout.write(f"[{datetime.now().strftime('%H:%M:%S')}] Updating analysis...")
                    results = self.service.update_analysis()
                    self.stdout.write(f"  -> {results['stocks']} stocks analyzed")
                    last_analysis_update = current_time

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))

            # Sleep for a short interval before checking again
            time.sleep(10)

        self.stdout.write(self.style.SUCCESS('Scheduler stopped.'))

    def signal_handler(self, signum, frame):
        self.stdout.write('\nReceived shutdown signal, stopping...')
        self.running = False
