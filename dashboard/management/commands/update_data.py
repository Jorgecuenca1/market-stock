"""
Management command to update stock data (prices, news, analysis).
"""
from django.core.management.base import BaseCommand
from scraper.services import ScrapingService


class Command(BaseCommand):
    help = 'Update stock data from all sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prices',
            action='store_true',
            help='Update prices only',
        )
        parser.add_argument(
            '--news',
            action='store_true',
            help='Update news only',
        )
        parser.add_argument(
            '--analysis',
            action='store_true',
            help='Update analysis only',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Update all data (default)',
        )

    def handle(self, *args, **options):
        service = ScrapingService()

        # Determine what to update
        update_all = options['all'] or not any([options['prices'], options['news'], options['analysis']])

        if update_all or options['prices']:
            self.stdout.write('Updating prices...')
            results = service.update_prices()
            self.stdout.write(f"  Stocks: {results['stocks']}, Indices: {results['indices']}")
            if results['errors']:
                self.stdout.write(self.style.WARNING(f"  Errors: {len(results['errors'])}"))

        if update_all or options['news']:
            self.stdout.write('Updating news...')
            results = service.update_news()
            self.stdout.write(f"  Articles: {results['articles']}")
            if results['errors']:
                self.stdout.write(self.style.WARNING(f"  Errors: {len(results['errors'])}"))

        if update_all or options['analysis']:
            self.stdout.write('Updating analysis...')
            results = service.update_analysis()
            self.stdout.write(f"  Stocks analyzed: {results['stocks']}")
            if results['errors']:
                self.stdout.write(self.style.WARNING(f"  Errors: {len(results['errors'])}"))

        self.stdout.write(self.style.SUCCESS('Data update completed!'))
