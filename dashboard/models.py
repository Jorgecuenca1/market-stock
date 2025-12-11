"""
Models for the Market Stock Dashboard.
"""
from django.db import models
from django.utils import timezone


class Stock(models.Model):
    """Model representing a tracked stock."""

    SECTOR_CHOICES = [
        ('Technology', 'Technology'),
        ('Healthcare', 'Healthcare'),
        ('Energy', 'Energy'),
        ('Industrial', 'Industrial'),
        ('Financial', 'Financial'),
        ('Consumer', 'Consumer'),
        ('Utilities', 'Utilities'),
        ('Materials', 'Materials'),
        ('Real Estate', 'Real Estate'),
        ('Communication', 'Communication'),
    ]

    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class Index(models.Model):
    """Model representing a market index."""

    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Indices"
        ordering = ['name']

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class StockPrice(models.Model):
    """Model storing historical stock prices."""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    change = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_percent = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    source = models.CharField(max_length=50, default='yahoo_finance')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['stock', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.stock.symbol} - ${self.price} at {self.timestamp}"


class IndexPrice(models.Model):
    """Model storing historical index prices."""

    index = models.ForeignKey(Index, on_delete=models.CASCADE, related_name='prices')
    level = models.DecimalField(max_digits=12, decimal_places=2)
    change = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_percent = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pe_forward = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    source = models.CharField(max_length=50, default='yahoo_finance')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['index', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.index.symbol} - {self.level} at {self.timestamp}"


class StockAnalysis(models.Model):
    """Model storing detailed stock analysis."""

    RATING_CHOICES = [
        ('STRONG_BUY', 'Strong Buy'),
        ('BUY', 'Buy'),
        ('HOLD', 'Hold'),
        ('SELL', 'Sell'),
        ('STRONG_SELL', 'Strong Sell'),
        ('HIGH_RISK', 'High Risk/Reward'),
    ]

    SENTIMENT_CHOICES = [
        ('BULLISH', 'Bullish'),
        ('NEUTRAL', 'Neutral'),
        ('BEARISH', 'Bearish'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='analyses')

    # Price metrics
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    market_cap = models.CharField(max_length=20, null=True, blank=True)

    # Valuation metrics
    pe_trailing = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pe_forward = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    peg_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Balance sheet metrics
    debt_equity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quick_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    interest_coverage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Cash and debt
    cash = models.CharField(max_length=20, null=True, blank=True)
    total_debt = models.CharField(max_length=20, null=True, blank=True)
    net_cash = models.CharField(max_length=20, null=True, blank=True)
    free_cash_flow = models.CharField(max_length=20, null=True, blank=True)

    # Profitability
    gross_margin = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    operating_margin = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    net_margin = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    roe = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Dividend
    dividend_yield = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Scores and ratings
    gf_score = models.CharField(max_length=20, null=True, blank=True)
    altman_z_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    piotroski_score = models.CharField(max_length=20, null=True, blank=True)

    # Analyst data
    price_target = models.CharField(max_length=50, null=True, blank=True)
    analyst_rating = models.CharField(max_length=100, null=True, blank=True)

    # Overall assessment
    rating = models.CharField(max_length=20, choices=RATING_CHOICES, default='HOLD')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='NEUTRAL')
    conclusion_en = models.TextField(null=True, blank=True)
    conclusion_es = models.TextField(null=True, blank=True)

    # Metadata
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    sources = models.JSONField(default=list)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Stock Analyses"
        indexes = [
            models.Index(fields=['stock', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.stock.symbol} Analysis - {self.timestamp.date()}"


class StockNews(models.Model):
    """Model storing stock news articles."""

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='news')
    headline = models.CharField(max_length=500)
    headline_es = models.CharField(max_length=500, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    summary_es = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)
    source = models.CharField(max_length=100)
    published_at = models.DateTimeField(null=True, blank=True)
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = "Stock News"
        indexes = [
            models.Index(fields=['stock', '-published_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.stock.symbol}: {self.headline[:50]}..."


class MarketNews(models.Model):
    """Model storing general market news."""

    CATEGORY_CHOICES = [
        ('market', 'Market'),
        ('economy', 'Economy'),
        ('fed', 'Federal Reserve'),
        ('earnings', 'Earnings'),
        ('sector', 'Sector'),
        ('other', 'Other'),
    ]

    headline = models.CharField(max_length=500)
    headline_es = models.CharField(max_length=500, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    summary_es = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)
    source = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='market')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    related_stocks = models.ManyToManyField(Stock, blank=True, related_name='market_news')

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = "Market News"

    def __str__(self):
        return f"{self.headline[:50]}..."


class ScrapingLog(models.Model):
    """Model for tracking scraping activity."""

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ]

    source = models.CharField(max_length=100)
    task_type = models.CharField(max_length=50)  # news, price, analysis
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    items_scraped = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.source} - {self.task_type} - {self.status} at {self.timestamp}"


class ReportCache(models.Model):
    """Model for caching generated reports."""

    REPORT_TYPES = [
        ('sp500_analysis', 'S&P 500 Analysis'),
        ('news_report', 'News Report'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    language = models.CharField(max_length=2, default='en')
    content = models.JSONField()
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['report_type', 'language']

    def __str__(self):
        return f"{self.report_type} ({self.language}) - {self.generated_at}"
