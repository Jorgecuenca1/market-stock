"""
URL configuration for the dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Primary Dashboard
    path('', views.index, name='index'),
    path('sp500-analysis/', views.sp500_analysis, name='sp500_analysis'),
    path('news-report/', views.news_report, name='news_report'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('set-language/<str:lang>/', views.set_language, name='set_language'),

    # Secondary Dashboard
    path('secondary/', views.secondary_index, name='secondary_index'),
    path('secondary/analysis/', views.secondary_analysis, name='secondary_analysis'),
    path('secondary/news/', views.secondary_news_report, name='secondary_news'),
]
