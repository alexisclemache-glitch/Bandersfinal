from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCustom

@admin.register(UsuarioCustom)
class UsuarioCustomAdmin(UserAdmin):
    # Esto hará que el panel de usuario se vea ordenado
    model = UsuarioCustom
    list_display = ['username', 'email', 'rol', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol', {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Rol', {'fields': ('rol',)}),
    )