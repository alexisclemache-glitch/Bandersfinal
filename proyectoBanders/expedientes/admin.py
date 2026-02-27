from django.contrib import admin
from .models import Expediente, NotaExpediente, DocumentoExpediente

class NotaInline(admin.TabularInline):
    model = NotaExpediente
    extra = 1

class DocumentoInline(admin.TabularInline):
    model = DocumentoExpediente
    extra = 1

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    # 'creado_por' ahora existe en el modelo, por lo que no dará error
    list_display = ('titulo', 'cliente', 'numero_proceso', 'estado', 'prioridad', 'creado_por')
    list_filter = ('estado', 'prioridad', 'tipo_expediente')
    search_fields = ('titulo', 'numero_proceso', 'cliente__nombre')
    inlines = [NotaInline, DocumentoInline]