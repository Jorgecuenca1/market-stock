"""
Views for the Market Stock Dashboard.
"""
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from .models import (
    Stock, Index, StockPrice, IndexPrice, StockAnalysis,
    StockNews, MarketNews, ReportCache
)


def get_language(request):
    """Get current language from session."""
    return request.session.get('language', 'en')


def set_language(request, lang):
    """Set language preference."""
    if lang in ['en', 'es']:
        request.session['language'] = lang
    return redirect(request.META.get('HTTP_REFERER', '/'))


def index(request):
    """Main dashboard view."""
    lang = get_language(request)

    # Get latest prices
    stocks = []
    for stock in Stock.objects.filter(is_active=True):
        latest_price = stock.prices.first()
        latest_analysis = stock.analyses.first()
        stocks.append({
            'stock': stock,
            'price': latest_price,
            'analysis': latest_analysis,
        })

    indices = []
    for index in Index.objects.filter(is_active=True):
        latest_price = index.prices.first()
        indices.append({
            'index': index,
            'price': latest_price,
        })

    # Get recent news
    recent_news = StockNews.objects.all()[:10]
    market_news = MarketNews.objects.all()[:5]

    context = {
        'stocks': stocks,
        'indices': indices,
        'recent_news': recent_news,
        'market_news': market_news,
        'lang': lang,
        'last_update': timezone.now(),
    }
    return render(request, 'dashboard/index.html', context)


def sp500_analysis(request):
    """S&P 500 Analysis report view."""
    lang = get_language(request)

    # Get index data
    indices_data = []
    pe_averages = {
        '^GSPC': 18.7,  # S&P 500 10-year average
        '^NDX': 26.3,   # NASDAQ 100 10-year average
        '^DJI': 20.2,   # DOW JONES 10-year average
        '^RUT': 18.0,   # Russell 2000 average
    }

    for index in Index.objects.filter(is_active=True):
        latest_price = index.prices.first()
        if latest_price:
            pe_avg = pe_averages.get(index.symbol, 20)
            pe_current = float(latest_price.pe_ratio) if latest_price.pe_ratio else None

            status = 'FAIR'
            if pe_current and pe_current > pe_avg * 1.3:
                status = 'OVERVALUED'
            elif pe_current and pe_current < pe_avg * 0.8:
                status = 'UNDERVALUED'

            indices_data.append({
                'index': index,
                'price': latest_price,
                'pe_10y_avg': pe_avg,
                'status': status,
            })

    # Get stock analyses grouped by sector
    sectors = {}
    for stock in Stock.objects.filter(is_active=True):
        latest_analysis = stock.analyses.first()
        if latest_analysis:
            sector = stock.sector
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append({
                'stock': stock,
                'analysis': latest_analysis,
            })

    # Calculate summary stats - compatible with SQLite
    all_analyses = []
    for stock in Stock.objects.filter(is_active=True):
        latest = stock.analyses.first()
        if latest:
            all_analyses.append(latest)

    bullish_count = sum(1 for a in all_analyses if a.sentiment == 'BULLISH')
    neutral_count = sum(1 for a in all_analyses if a.sentiment == 'NEUTRAL')
    bearish_count = sum(1 for a in all_analyses if a.sentiment == 'BEARISH')

    context = {
        'indices': indices_data,
        'sectors': sectors,
        'bullish_count': bullish_count,
        'neutral_count': neutral_count,
        'bearish_count': bearish_count,
        'total_stocks': len(all_analyses),
        'lang': lang,
        'report_date': timezone.now(),
    }
    return render(request, 'dashboard/sp500_analysis.html', context)


def news_report(request):
    """News report view with real-time updates."""
    lang = get_language(request)

    # Get news grouped by stock
    stocks_news = []
    for stock in Stock.objects.filter(is_active=True):
        latest_price = stock.prices.first()
        news = stock.news.all()[:6]
        latest_analysis = stock.analyses.first()

        stocks_news.append({
            'stock': stock,
            'price': latest_price,
            'news': news,
            'analysis': latest_analysis,
            'sentiment': latest_analysis.sentiment if latest_analysis else 'NEUTRAL',
        })

    # General market news
    market_news = MarketNews.objects.all()[:15]

    # Calculate sentiment summary
    sentiments = {
        'bullish': sum(1 for s in stocks_news if s['sentiment'] == 'BULLISH'),
        'neutral': sum(1 for s in stocks_news if s['sentiment'] == 'NEUTRAL'),
        'bearish': sum(1 for s in stocks_news if s['sentiment'] == 'BEARISH'),
    }

    context = {
        'stocks_news': stocks_news,
        'market_news': market_news,
        'sentiments': sentiments,
        'lang': lang,
        'report_date': timezone.now(),
        'total_articles': StockNews.objects.count(),
    }
    return render(request, 'dashboard/news_report.html', context)


def stock_detail(request, symbol):
    """Detailed view for a single stock."""
    lang = get_language(request)

    stock = get_object_or_404(Stock, symbol=symbol.upper())
    latest_price = stock.prices.first()
    latest_analysis = stock.analyses.first()
    recent_news = stock.news.all()[:10]

    # Historical prices (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    historical_prices = stock.prices.filter(
        timestamp__gte=thirty_days_ago
    ).order_by('timestamp')

    context = {
        'stock': stock,
        'price': latest_price,
        'analysis': latest_analysis,
        'news': recent_news,
        'historical_prices': historical_prices,
        'lang': lang,
    }
    return render(request, 'dashboard/stock_detail.html', context)
