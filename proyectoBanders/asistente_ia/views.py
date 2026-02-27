import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import NotebookLegal

# SDK de Google Gemini v2.0+
from google import genai
from google.genai import types


@login_required
def inbox_ia(request):
    """Carga la interfaz principal y el historial."""
    notebooks = NotebookLegal.objects.filter(abogado=request.user).order_by('-fecha_creacion')
    return render(request, 'asistente_ia/inbox.html', {'notebooks': notebooks})


@login_required
def generar_escrito_gemini(request):
    """Procesamiento con Gemini 2.0 Flash (Optimizado)."""
    if request.method == "POST":
        prompt_usuario = request.POST.get('prompt', '')
        archivo = request.FILES.get('archivo')

        if not prompt_usuario and not archivo:
            return JsonResponse({'status': 'error', 'message': 'Ingrese consulta o archivo.'}, status=400)

        try:
            # Validamos que la Key exista en settings (cargada del .env)
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if not api_key:
                return JsonResponse({'status': 'error', 'message': 'API Key no encontrada en el sistema.'}, status=500)

            client = genai.Client(api_key=api_key)

            # Definimos el comportamiento de la IA
            instruccion_sistema = (
                "Eres un experto legal ecuatoriano. Responde usando solo etiquetas HTML básicas (p, strong, ul, li). "
                "No uses bloques de código ``` ni estilos CSS. Sé formal y preciso."
            )

            contenidos = []

            # Si hay un archivo, lo preparamos para la IA
            if archivo:
                archivo_data = archivo.read()
                archivo_part = types.Part.from_bytes(
                    data=archivo_data,
                    mime_type=archivo.content_type
                )
                contenidos.append(archivo_part)

            # Agregamos la consulta del abogado
            if prompt_usuario:
                contenidos.append(f"Consulta: {prompt_usuario}")
            else:
                contenidos.append("Analiza el documento adjunto y extrae los puntos legales clave.")

            # Llamada al modelo 2.0 (más estable para el SDK 1.63.0)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contenidos,
                config=types.GenerateContentConfig(
                    system_instruction=instruccion_sistema,
                    temperature=0.3
                )
            )

            if response and response.text:
                # Limpieza de Markdown para que el HTML se renderice bien en el frontend
                respuesta_limpia = response.text.replace('```html', '').replace('```', '').strip()
                return JsonResponse({'status': 'success', 'respuesta': respuesta_limpia})

            return JsonResponse({'status': 'error', 'message': 'La IA no devolvió ninguna respuesta.'})

        except Exception as e:
            print(f"DEBUG ERROR IA: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Error técnico: {str(e)}"}, status=500)


@login_required
def guardar_en_notebook(request):
    """Guarda el resultado en el historial."""
    if request.method == "POST":
        titulo = request.POST.get('titulo', 'Nota Legal')
        contenido = request.POST.get('contenido', '')

        if not contenido:
            return JsonResponse({'status': 'error', 'message': 'No hay contenido para guardar.'}, status=400)

        nuevo = NotebookLegal.objects.create(
            abogado=request.user,
            titulo_caso=titulo[:100],
            contenido_escrito=contenido
        )
        return JsonResponse({'status': 'success', 'id': nuevo.id})


@login_required
def eliminar_cuaderno(request, pk):
    """Elimina una nota del historial."""
    if request.method == "POST":
        registro = get_object_or_404(NotebookLegal, pk=pk, abogado=request.user)
        registro.delete()
        return JsonResponse({'status': 'success'})