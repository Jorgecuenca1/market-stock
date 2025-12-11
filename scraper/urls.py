"""
API URLs for the scraper app.
"""
from django.urls import path
from . import views

app_name = 'scraper'

urlpatterns = [
    path('prices/', views.api_prices, name='api_prices'),
    path('news/', views.api_news, name='api_news'),
    path('analysis/', views.api_analysis, name='api_analysis'),
    path('update/prices/', views.trigger_price_update, name='trigger_price_update'),
    path('update/news/', views.trigger_news_update, name='trigger_news_update'),
    path('update/analysis/', views.trigger_analysis_update, name='trigger_analysis_update'),
    path('update/all/', views.trigger_full_update, name='trigger_full_update'),
]
