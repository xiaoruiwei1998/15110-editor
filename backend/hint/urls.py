# urls.py

from django.urls import path
from .views import get_hint

urlpatterns = [
    path('api/get_hint/', get_hint, name='get_hint'),
]
