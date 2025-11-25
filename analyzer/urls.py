from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('credentials/', views.credentials, name='credentials'),
    path('credentials/clear/', views.clear_credentials, name='clear_credentials'),
    path('stale-content/', views.stale_content, name='stale_content'),
    path('api/analyze-stale/', views.analyze_stale_content, name='analyze_stale_content'),
    path('low-engagement/', views.low_engagement, name='low_engagement'),
    path('api/analyze-low-engagement/', views.analyze_low_engagement, name='analyze_low_engagement'),
    path('duplicates/', views.duplicates, name='duplicates'),
    path('api/analyze-duplicates/', views.analyze_duplicates, name='analyze_duplicates'),
    path('priority-queue/', views.priority_queue, name='priority_queue'),
    path('api/analyze-priority/', views.analyze_priority, name='analyze_priority'),
    path('trending/', views.trending, name='trending'),
    path('api/analyze-trending/', views.analyze_trending, name='analyze_trending'),
]
