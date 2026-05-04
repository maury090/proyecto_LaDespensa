from django.shortcuts import render

# Create your views here.

def index (request): 
    return render (request, 'index.html')

def conocenos (request):
    return render (request, 'conocenos.html')

def login (request):
    return render (request, 'login.html')

def crearUsuario (request):
    return render (request, 'crearUsuario.html')


