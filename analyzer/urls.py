from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('credentials/', views.credentials, name='credentials'),
    path('credentials/clear/', views.clear_credentials, name='clear_credentials'),
    path('stale-content/', views.stale_content, name='stale_content'),
    path('api/analyze-stale/', views.analyze_stale_content, name='analyze_stale_content'),
]
