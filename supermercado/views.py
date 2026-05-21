from django.shortcuts import render
from .models import Producto, Categoria


def index(request):
    # Obtener productos marcados para mostrar en el index
    productos = Producto.objects.filter(mostrar_en_index=True)
    
    # Aplicar 10% de descuento a cada producto
    for producto in productos:
        producto.precio_con_descuento = int(producto.precio * 0.9)  # 10% descuento
    
    return render(request, 'index.html', {'productos': productos})

def conocenos (request):
    return render (request, 'conocenos.html')

def login (request):
    return render (request, 'login.html')

def crearUsuario (request):
    return render (request, 'crearUsuario.html')

def alimentos (request):
    #llama al id de la categoria
    productos = Producto.objects.filter(categoria_id=4)  
    
    #aplicacion de descuento
    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None

    return render (request, 'alimentos.html', {'productos': productos})

def aseo (request):
    productos = Producto.objects.filter(categoria_id=5)

    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None

    return render (request, 'aseo.html', {'productos': productos})

def bebestibles (request):
    #llamado de ids
    productos = Producto.objects.filter(
        categoria_id__in=[2, 3]  
    )

    #descuento del 10% 
    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None  
    
    return render(request, 'bebestibles.html', {'productos': productos})

def terminosCondiciones (request):
    return render (request, 'terminosCondiciones.html')