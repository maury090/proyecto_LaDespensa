from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# tabla categorias
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# productos
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField()
    stock = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Campo para controlar la visibilidad en el index
    mostrar_en_index = models.BooleanField(default=False, help_text="Marcar para mostrar en inicio")
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

# Modelo para extender el usuario con más campos
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ... tus modelos Categoria y Producto ...

class PerfilCliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(max_length=12, unique=True, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección de domicilio")
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Administrador'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cliente')

    class Meta:
        verbose_name = 'Perfil de Cliente'
        verbose_name_plural = 'Perfiles de Clientes'

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    def get_direccion(self):
        return self.direccion if self.direccion else "Domicilio no especificado"

# Señales
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilCliente.objects.create(usuario=instance, rol='cliente')

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()



#carrito de compras 
class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def get_total(self):
        """Calcula el total del carrito"""
        total = sum(item.get_subtotal() for item in self.items.all())
        return total
    
    def get_cantidad_items(self):
        """Calcula la cantidad total de productos en el carrito"""
        return sum(item.cantidad for item in self.items.all())


class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    agregado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item del carrito'
        verbose_name_plural = 'Items del carrito'
        unique_together = ['carrito', 'producto']  # Evita duplicados
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def get_subtotal(self):
        """Calcula el subtotal del item (cantidad * precio)"""
        return self.cantidad * self.producto.precio
    
    def get_precio_con_descuento(self):
        """Retorna el precio del producto con descuento si aplica"""
        if self.producto.mostrar_en_index:
            return int(self.producto.precio * 0.9)  # 10% de descuento
        return self.producto.precio
    
    def get_subtotal_con_descuento(self):
        """Calcula el subtotal con descuento"""
        return self.cantidad * self.get_precio_con_descuento()
    

#pedido
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),

]
    
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()
    direccion = models.TextField()
    metodo_entrega = models.CharField(max_length=20, choices=[('retiro', 'Retiro en tienda'), ('despacho', 'Despacho a domicilio')])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.IntegerField()
    subtotal = models.IntegerField()
    
    class Meta:
        verbose_name = 'Item del pedido'
        verbose_name_plural = 'Items del pedido'
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"