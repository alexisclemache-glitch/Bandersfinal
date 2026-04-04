from django.contrib import admin
from .models import Perfil, DocumentoAdjunto, NotaKeep

class DocumentoInline(admin.TabularInline):
    model = DocumentoAdjunto
    extra = 1

class NotaKeepInline(admin.TabularInline):
    model = NotaKeep
    extra = 1

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    # Reemplazamos 'mfa_activado' por 'tiene_mfa'
    list_display = ('user', 'especialidad', 'tiene_mfa', 'telefono')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'especialidad')
    list_filter = ('especialidad',)
    inlines = [DocumentoInline, NotaKeepInline]

    # Configuramos cómo se ve 'tiene_mfa' en el admin
    @admin.display(boolean=True, description='MFA Activo')
    def tiene_mfa(self, obj):
        return obj.tiene_mfa

@admin.register(DocumentoAdjunto)
class DocumentoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'fecha_subida')
    list_filter = ('fecha_subida',)

@admin.register(NotaKeep)
class NotaKeepAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'perfil', 'fecha_creacion')