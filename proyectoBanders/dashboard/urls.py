# dashboard/urls.py
from django.urls import path
from .views import DashboardView

app_name = 'dashboard' # Este es el namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'), # Este es el name
]