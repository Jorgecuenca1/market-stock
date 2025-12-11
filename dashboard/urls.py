"""
URL configuration for the dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('sp500-analysis/', views.sp500_analysis, name='sp500_analysis'),
    path('news-report/', views.news_report, name='news_report'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('set-language/<str:lang>/', views.set_language, name='set_language'),
]
