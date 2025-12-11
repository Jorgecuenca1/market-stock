"""
API views for the scraper app.
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from dashboard.models import Stock, Index, StockPrice, IndexPrice, StockNews, StockAnalysis
from .services import ScrapingService


@require_GET
def api_prices(request):
    """Get latest prices for all stocks and indices."""
    stocks_data = []
    for stock in Stock.objects.filter(is_active=True):
        latest_price = stock.prices.first()
        if latest_price:
            stocks_data.append({
                'symbol': stock.symbol,
                'name': stock.name,
                'sector': stock.sector,
                'price': float(latest_price.price),
                'change': float(latest_price.change) if latest_price.change else None,
                'change_percent': float(latest_price.change_percent) if latest_price.change_percent else None,
                'volume': latest_price.volume,
                'market_cap': float(latest_price.market_cap) if latest_price.market_cap else None,
                'timestamp': latest_price.timestamp.isoformat(),
            })

    indices_data = []
    for index in Index.objects.filter(is_active=True):
        latest_price = index.prices.first()
        if latest_price:
            indices_data.append({
                'symbol': index.symbol,
                'name': index.name,
                'level': float(latest_price.level),
                'change': float(latest_price.change) if latest_price.change else None,
                'change_percent': float(latest_price.change_percent) if latest_price.change_percent else None,
                'timestamp': latest_price.timestamp.isoformat(),
            })

    return JsonResponse({
        'stocks': stocks_data,
        'indices': indices_data,
        'timestamp': timezone.now().isoformat(),
    })


@require_GET
def api_news(request):
    """Get latest news for all stocks."""
    symbol = request.GET.get('symbol')
    limit = int(request.GET.get('limit', 20))

    if symbol:
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
            news = stock.news.all()[:limit]
        except Stock.DoesNotExist:
            return JsonResponse({'error': 'Stock not found'}, status=404)
    else:
        news = StockNews.objects.all()[:limit]

    news_data = []
    for article in news:
        news_data.append({
            'symbol': article.stock.symbol,
            'headline': article.headline,
            'headline_es': article.headline_es,
            'summary': article.summary,
            'summary_es': article.summary_es,
            'url': article.url,
            'source': article.source,
            'sentiment': article.sentiment,
            'published_at': article.published_at.isoformat() if article.published_at else None,
        })

    return JsonResponse({
        'news': news_data,
        'count': len(news_data),
        'timestamp': timezone.now().isoformat(),
    })


@require_GET
def api_analysis(request):
    """Get latest analysis for all stocks."""
    symbol = request.GET.get('symbol')

    if symbol:
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
            analyses = [stock.analyses.first()] if stock.analyses.exists() else []
        except Stock.DoesNotExist:
            return JsonResponse({'error': 'Stock not found'}, status=404)
    else:
        analyses = []
        for stock in Stock.objects.filter(is_active=True):
            latest = stock.analyses.first()
            if latest:
                analyses.append(latest)

    analysis_data = []
    for analysis in analyses:
        if analysis:
            analysis_data.append({
                'symbol': analysis.stock.symbol,
                'name': analysis.stock.name,
                'sector': analysis.stock.sector,
                'price': float(analysis.price) if analysis.price else None,
                'market_cap': analysis.market_cap,
                'pe_trailing': float(analysis.pe_trailing) if analysis.pe_trailing else None,
                'pe_forward': float(analysis.pe_forward) if analysis.pe_forward else None,
                'peg_ratio': float(analysis.peg_ratio) if analysis.peg_ratio else None,
                'debt_equity': float(analysis.debt_equity) if analysis.debt_equity else None,
                'current_ratio': float(analysis.current_ratio) if analysis.current_ratio else None,
                'quick_ratio': float(analysis.quick_ratio) if analysis.quick_ratio else None,
                'interest_coverage': float(analysis.interest_coverage) if analysis.interest_coverage else None,
                'cash': analysis.cash,
                'total_debt': analysis.total_debt,
                'net_cash': analysis.net_cash,
                'free_cash_flow': analysis.free_cash_flow,
                'gross_margin': float(analysis.gross_margin) if analysis.gross_margin else None,
                'operating_margin': float(analysis.operating_margin) if analysis.operating_margin else None,
                'net_margin': float(analysis.net_margin) if analysis.net_margin else None,
                'roe': float(analysis.roe) if analysis.roe else None,
                'dividend_yield': float(analysis.dividend_yield) if analysis.dividend_yield else None,
                'gf_score': analysis.gf_score,
                'altman_z_score': float(analysis.altman_z_score) if analysis.altman_z_score else None,
                'piotroski_score': analysis.piotroski_score,
                'price_target': analysis.price_target,
                'analyst_rating': analysis.analyst_rating,
                'rating': analysis.rating,
                'sentiment': analysis.sentiment,
                'conclusion_en': analysis.conclusion_en,
                'conclusion_es': analysis.conclusion_es,
                'timestamp': analysis.timestamp.isoformat(),
            })

    return JsonResponse({
        'analyses': analysis_data,
        'count': len(analysis_data),
        'timestamp': timezone.now().isoformat(),
    })


@csrf_exempt
@require_POST
def trigger_price_update(request):
    """Trigger manual price update."""
    try:
        service = ScrapingService()
        results = service.update_prices()
        return JsonResponse({
            'status': 'success',
            'results': results,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def trigger_news_update(request):
    """Trigger manual news update."""
    try:
        service = ScrapingService()
        results = service.update_news()
        return JsonResponse({
            'status': 'success',
            'results': results,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def trigger_analysis_update(request):
    """Trigger manual analysis update."""
    try:
        service = ScrapingService()
        results = service.update_analysis()
        return JsonResponse({
            'status': 'success',
            'results': results,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def trigger_full_update(request):
    """Trigger full update (prices, news, analysis)."""
    try:
        service = ScrapingService()
        results = {
            'prices': service.update_prices(),
            'news': service.update_news(),
            'analysis': service.update_analysis(),
        }
        return JsonResponse({
            'status': 'success',
            'results': results,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)
