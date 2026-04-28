from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id_categoria', 'nombre']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'precio', 'stock', 'categoria']
    list_filter = ['categoria']
    search_fields = ['codigo', 'nombre']
    list_editable = ['precio', 'stock']

# Register your models here.
