"""
WSGI config for Market Stock Dashboard project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market_stock.settings')
application = get_wsgi_application()
