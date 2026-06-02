def usuario_context(request):
    """
    Esta función hace disponible el usuario en TODAS las plantillas
    """
    return {
        'user': request.user
    }