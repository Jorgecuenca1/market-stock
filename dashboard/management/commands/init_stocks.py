"""
Management command to initialize stocks and indices.
"""
from django.core.management.base import BaseCommand
from scraper.services import ScrapingService


class Command(BaseCommand):
    help = 'Initialize tracked stocks and indices from settings'

    def handle(self, *args, **options):
        self.stdout.write('Initializing stocks and indices...')

        service = ScrapingService()
        service.initialize_stocks()

        self.stdout.write(self.style.SUCCESS('Successfully initialized stocks and indices!'))
