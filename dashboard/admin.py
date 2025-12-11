"""
Admin configuration for Market Stock Dashboard.
"""
from django.contrib import admin
from .models import (
    Stock, Index, StockPrice, IndexPrice, StockAnalysis,
    StockNews, MarketNews, ScrapingLog, ReportCache
)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'sector', 'is_active', 'updated_at']
    list_filter = ['sector', 'is_active']
    search_fields = ['symbol', 'name']


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['symbol', 'name']


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'price', 'change_percent', 'timestamp', 'source']
    list_filter = ['source', 'timestamp']
    search_fields = ['stock__symbol']
    date_hierarchy = 'timestamp'


@admin.register(IndexPrice)
class IndexPriceAdmin(admin.ModelAdmin):
    list_display = ['index', 'level', 'change_percent', 'timestamp', 'source']
    list_filter = ['source', 'timestamp']
    search_fields = ['index__symbol']
    date_hierarchy = 'timestamp'


@admin.register(StockAnalysis)
class StockAnalysisAdmin(admin.ModelAdmin):
    list_display = ['stock', 'price', 'rating', 'sentiment', 'timestamp']
    list_filter = ['rating', 'sentiment', 'timestamp']
    search_fields = ['stock__symbol']
    date_hierarchy = 'timestamp'


@admin.register(StockNews)
class StockNewsAdmin(admin.ModelAdmin):
    list_display = ['stock', 'headline', 'source', 'sentiment', 'published_at']
    list_filter = ['source', 'sentiment', 'published_at']
    search_fields = ['stock__symbol', 'headline']
    date_hierarchy = 'published_at'


@admin.register(MarketNews)
class MarketNewsAdmin(admin.ModelAdmin):
    list_display = ['headline', 'source', 'category', 'published_at']
    list_filter = ['source', 'category', 'published_at']
    search_fields = ['headline']
    date_hierarchy = 'published_at'


@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    list_display = ['source', 'task_type', 'status', 'items_scraped', 'timestamp']
    list_filter = ['source', 'task_type', 'status']
    date_hierarchy = 'timestamp'


@admin.register(ReportCache)
class ReportCacheAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'language', 'generated_at']
    list_filter = ['report_type', 'language']
