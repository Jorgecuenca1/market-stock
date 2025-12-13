"""
Django settings for Market Stock Dashboard project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-market-stock-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    'marketstock.jorgecuenca.com',
    'localhost',
    '127.0.0.1',
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://marketstock.jorgecuenca.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://marketstock.jorgecuenca.com",
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'django_extensions',
    # Local apps
    'dashboard',
    'scraper',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'market_stock.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.language_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'market_stock.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Stock Configuration
TRACKED_STOCKS = [
    # Technology
    {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology'},
    {'symbol': 'AVGO', 'name': 'Broadcom Inc.', 'sector': 'Technology'},
    {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
    {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
    {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
    {'symbol': 'INTC', 'name': 'Intel Corporation', 'sector': 'Technology'},
    {'symbol': 'TSM', 'name': 'Taiwan Semiconductor', 'sector': 'Technology'},
    # Financial Services
    {'symbol': 'AMP', 'name': 'Ameriprise Financial', 'sector': 'Financial Services'},
    {'symbol': 'AXP', 'name': 'American Express Co.', 'sector': 'Financial Services'},
    # Insurance
    {'symbol': 'CB', 'name': 'Chubb Limited', 'sector': 'Insurance'},
    # Energy / Utilities
    {'symbol': 'CEG', 'name': 'Constellation Energy', 'sector': 'Utilities'},
    {'symbol': 'GEV', 'name': 'GE Vernova Inc.', 'sector': 'Industrial'},
    # Construction
    {'symbol': 'EME', 'name': 'EMCOR Group Inc.', 'sector': 'Construction'},
    # Aerospace
    {'symbol': 'SPCE', 'name': 'Virgin Galactic Holdings', 'sector': 'Aerospace'},
]

TRACKED_INDICES = [
    {'symbol': '^GSPC', 'name': 'S&P 500'},
    {'symbol': '^NDX', 'name': 'NASDAQ 100'},
    {'symbol': '^DJI', 'name': 'DOW JONES'},
    {'symbol': '^RUT', 'name': 'Russell 2000'},
    {'symbol': '^VIX', 'name': 'VIX'},
]

# Secondary Dashboard Stocks
TRACKED_STOCKS_SECONDARY = [
    # Technology
    {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
    {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'Technology'},
    {'symbol': 'AMAT', 'name': 'Applied Materials', 'sector': 'Technology'},
    {'symbol': 'ANET', 'name': 'Arista Networks', 'sector': 'Technology'},
    {'symbol': 'BABA', 'name': 'Alibaba Group', 'sector': 'Technology'},
    {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'sector': 'Technology'},
    {'symbol': 'ORCL', 'name': 'Oracle Corporation', 'sector': 'Technology'},
    {'symbol': 'QCOM', 'name': 'Qualcomm Inc.', 'sector': 'Technology'},
    {'symbol': 'RBLX', 'name': 'Roblox Corporation', 'sector': 'Technology'},
    # Cybersecurity
    {'symbol': 'CRWD', 'name': 'CrowdStrike Holdings', 'sector': 'Cybersecurity'},
    {'symbol': 'CYBR', 'name': 'CyberArk Software', 'sector': 'Cybersecurity'},
    # Financial Services
    {'symbol': 'GS', 'name': 'Goldman Sachs', 'sector': 'Financial Services'},
    {'symbol': 'JPM', 'name': 'JPMorgan Chase', 'sector': 'Financial Services'},
    {'symbol': 'MA', 'name': 'Mastercard Inc.', 'sector': 'Financial Services'},
    {'symbol': 'V', 'name': 'Visa Inc.', 'sector': 'Financial Services'},
    {'symbol': 'PRU', 'name': 'Prudential Financial', 'sector': 'Financial Services'},
    {'symbol': 'HOOD', 'name': 'Robinhood Markets', 'sector': 'Financial Services'},
    {'symbol': 'DAVE', 'name': 'Dave Inc.', 'sector': 'Financial Services'},
    # Energy
    {'symbol': 'XOM', 'name': 'Exxon Mobil', 'sector': 'Energy'},
    {'symbol': 'CVX', 'name': 'Chevron Corporation', 'sector': 'Energy'},
    {'symbol': 'ET', 'name': 'Energy Transfer LP', 'sector': 'Energy'},
    {'symbol': 'FSLR', 'name': 'First Solar Inc.', 'sector': 'Energy'},
    {'symbol': 'NRG', 'name': 'NRG Energy', 'sector': 'Energy'},
    {'symbol': 'VST', 'name': 'Vistra Corp.', 'sector': 'Energy'},
    # Healthcare
    {'symbol': 'GILD', 'name': 'Gilead Sciences', 'sector': 'Healthcare'},
    {'symbol': 'LLY', 'name': 'Eli Lilly & Co.', 'sector': 'Healthcare'},
    {'symbol': 'ISRG', 'name': 'Intuitive Surgical', 'sector': 'Healthcare'},
    {'symbol': 'AZNCF', 'name': 'AstraZeneca PLC', 'sector': 'Healthcare'},
    # Industrial / Aerospace
    {'symbol': 'BA', 'name': 'Boeing Company', 'sector': 'Aerospace'},
    {'symbol': 'GE', 'name': 'General Electric', 'sector': 'Industrial'},
    {'symbol': 'ETN', 'name': 'Eaton Corporation', 'sector': 'Industrial'},
    {'symbol': 'NOC', 'name': 'Northrop Grumman', 'sector': 'Aerospace'},
    {'symbol': 'AVAV', 'name': 'AeroVironment Inc.', 'sector': 'Aerospace'},
    {'symbol': 'AXON', 'name': 'Axon Enterprise', 'sector': 'Industrial'},
    # Infrastructure / Construction
    {'symbol': 'ROAD', 'name': 'Construction Partners', 'sector': 'Construction'},
    # Crypto / Mining
    {'symbol': 'IREN', 'name': 'Iris Energy Limited', 'sector': 'Crypto Mining'},
    # Travel
    {'symbol': 'VIK', 'name': 'Viking Holdings Ltd', 'sector': 'Travel'},
    # Other
    {'symbol': 'CRWV', 'name': 'CrowdStrike Holdings', 'sector': 'Technology'},
    {'symbol': 'CRCL', 'name': 'Circle Internet', 'sector': 'Financial Services'},
    {'symbol': 'IVES', 'name': 'IVES ETF', 'sector': 'ETF'},
    {'symbol': 'OSMCX', 'name': 'Osmium Fund', 'sector': 'Fund'},
]

# Scraping intervals (in minutes)
NEWS_UPDATE_INTERVAL = 5
PRICE_UPDATE_INTERVAL = 1
ANALYSIS_UPDATE_INTERVAL = 60

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'market_stock.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'scraper': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)
