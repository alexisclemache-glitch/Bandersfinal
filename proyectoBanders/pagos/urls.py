from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('', views.lista_pagos, name='lista_pagos'),
    path('crear/', views.crear_nuevo_pago, name='crear_nuevo_pago'),
    path('abono/<int:pago_id>/', views.registrar_abono, name='registrar_abono'),
    path('detalle-json/<int:pago_id>/', views.detalle_pago_json, name='detalle_pago_json'),
    path('eliminar-abono/<int:abono_id>/', views.eliminar_abono, name='eliminar_abono'),
    path('eliminar-txn/<int:pago_id>/', views.eliminar_transaccion, name='eliminar_transaccion'),
    path('exportar-pdf/<int:pago_id>/', views.exportar_pago_pdf, name='exportar_pago_pdf'),
]