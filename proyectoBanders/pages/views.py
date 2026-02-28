# pages/views.py

from django.views.generic import TemplateView


class DynamicPageView(TemplateView):
    """
    Vista genérica que toma el nombre de la plantilla de la URL
    y la renderiza.
    """

    def get_template_names(self):
        # 1. Extrae el valor del parámetro 'template_name' de la URL
        template_name = self.kwargs.get('template_name')

        # 2. Construye la ruta de la plantilla (Ej: 'pages-calendar.html')
        return [f'{template_name}.html']


from django.shortcuts import render

# Create your views here.
