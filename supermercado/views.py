from django.shortcuts import render
from .models import Producto, Categoria

# Create your views here.

def index (request): 

    #llamar elementos producto y cateria de la base de datos 
    try: 
        categoria = Categoria.objects.get(nombre='Alimentos')
        productos = Producto.objects.filter(categoria=categoria)

    except:
        productos = Producto.objects.all()
        
    productos = Producto.objects.filter(mostrar_en_index=True)
    return render (request, 'index.html', {'productos': productos})

def conocenos (request):
    return render (request, 'conocenos.html')

def login (request):
    return render (request, 'login.html')

def crearUsuario (request):
    return render (request, 'crearUsuario.html')

def alimentos (request):
    return render (request, 'alimentos.html')

def aseo (request):
    return render (request, 'aseo.html')

def bebestibles (request):
    return render (request, 'bebestibles.html')
