# pages/urls.py

from django.urls import path
from . import views

# 📌 MUY IMPORTANTE: Definir el nombre de la app (namespace)
app_name = 'pages'

urlpatterns = [
    # Esta ruta acepta cualquier cadena (str) y la nombra 'template_name'
    # La vista DynamicPageView usará este nombre.
    path('<str:template_name>/', views.DynamicPageView.as_view(), name='dynamic_pages'),
]