from .models import Carrito

def usuario_context(request):
    """
    Esta función hace disponible el usuario en TODAS las plantillas
    """
    return {
        'user': request.user
    }



def carrito_context(request):
    cantidad_items = 0
    
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_items = carrito.get_cantidad_items()
    
    return {
        'cantidad_items': cantidad_items
    }