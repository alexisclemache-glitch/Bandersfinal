from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'rut', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'rut')
    # Esto permite que el admin de Expedientes pueda usar 'autocomplete_fields'
    search_help_text = "Busque por nombre, apellido o RUT"