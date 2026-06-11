from django.shortcuts import render, redirect
from .models import Producto, Categoria , Carrito, CarritoItem
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
import re
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404



# Función para verificar si es administrador
def es_administrador(user):
    return user.is_authenticated and user.is_staff

# validacion de rut chileno 
def validar_rut_chileno(rut):
    """
    Valida un RUT chileno con algoritmo de módulo 11.
    Soporta RUT con o sin puntos, con o sin guión.
    Ejemplos válidos: 12345678K, 12345678-9, 12.345.678-K
    """
    # Limpiar el RUT: eliminar puntos, guiones y espacios
    rut = str(rut).replace('.', '').replace('-', '').replace(' ', '').upper()
    
    # Verificar formato básico (solo números y posible K al final)
    if len(rut) < 2:
        return False
    
    cuerpo = rut[:-1]  # Los números (cuerpo del RUT)
    dv_ingresado = rut[-1]  # El dígito verificador (puede ser número o K)
    
    # Validar que el cuerpo solo tenga números
    if not cuerpo.isdigit():
        return False
    
    # Calcular dígito verificador esperado (algoritmo módulo 11)
    suma = 0
    multiplicador = 2
    
    # Recorrer el cuerpo de derecha a izquierda
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    
    resto = suma % 11
    dv_esperado = 11 - resto
    
    # Convertir según las reglas del RUT chileno
    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)
    
    # Comparar el dígito ingresado con el esperado
    return dv_ingresado == dv_esperado


# ========== VISTAS PRINCIPALES ==========
def index(request):
    # Obtener productos marcados para mostrar en el index
    productos = Producto.objects.filter(mostrar_en_index=True)
    
    # Aplicar 10% de descuento a cada producto
    for producto in productos:
        producto.precio_con_descuento = int(producto.precio * 0.9)

    
    # Obtener cantidad del carrito si el usuario está logueado
    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()
    
    
    return render(request, 'index.html', {'productos': productos, 'cantidad_items': cantidad_carrito})


def conocenos(request):
    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()
    return render(request, 'conocenos.html', {'cantidad_items': cantidad_carrito})

def login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Redirigir según el tipo de usuario
            if user.is_staff or user.is_superuser:
                # Si es administrador, va al panel de admin
                return redirect('panel_admin')
            else:
                # Si es cliente normal, va al inicio
                return redirect('perfil_cli') 
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')




# creacion de usuario, con validacion y json response para ajax
def crearUsuario(request):
    # Verificar si es una petición AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('fname', '').strip()
        apellido = request.POST.get('lname', '').strip()
        rut = request.POST.get('rut', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('pswd1', '')
        password2 = request.POST.get('pswd2', '')
        acepta_terminos = request.POST.get('remember', False)
        
        # Lista para acumular errores
        errores = []
        
        # ========== 1. VALIDACIÓN DE NOMBRE ==========
        if not nombre:
            errores.append(' El nombre es obligatorio.')
        elif len(nombre) < 3:
            errores.append(' El nombre debe tener al menos 3 caracteres.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', nombre):
            errores.append(' El nombre solo puede contener letras.')
        
        # ========== 2. VALIDACIÓN DE APELLIDO ==========
        if not apellido:
            errores.append(' El apellido es obligatorio.')
        elif len(apellido) < 3:
            errores.append(' El apellido debe tener al menos 3 caracteres.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', apellido):
            errores.append(' El apellido solo puede contener letras.')
        
        # ========== 3. VALIDACIÓN DE RUT (con algoritmo chileno) ==========
        if not rut:
            errores.append(' El RUT es obligatorio.')
        elif not validar_rut_chileno(rut):
            errores.append(' RUT no válido. Ejemplo: 12345678K o 123456789')
        
        # ========== 4. VALIDACIÓN DE EMAIL ==========
        if not email:
            errores.append(' El correo electrónico es obligatorio.')
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errores.append(' El formato del correo electrónico no es válido.')
        elif User.objects.filter(email=email).exists():
            errores.append(' Este correo electrónico ya está registrado.')
        
        # ========== 5. VALIDACIÓN DE CONTRASEÑA ==========
        if not password:
            errores.append(' La contraseña es obligatoria.')
        elif len(password) < 6:
            errores.append(' La contraseña debe tener al menos 6 caracteres.')
        
        # ========== 6. VALIDACIÓN DE CONFIRMACIÓN ==========
        if not password2:
            errores.append(' Debes confirmar tu contraseña.')
        elif password != password2:
            errores.append(' Las contraseñas no coinciden.')
        
        # ========== 7. VALIDACIÓN DE TÉRMINOS Y CONDICIONES ==========
        if not acepta_terminos:
            errores.append(' Debes aceptar los términos y condiciones.')
        
        # ========== 8. VALIDAR RUT NO DUPLICADO ==========
        # Limpiar RUT para usar como username
        rut_limpio = str(rut).replace('.', '').replace('-', '').replace(' ', '').upper()
        username = f"cliente_{rut_limpio}"
        if User.objects.filter(username=username).exists():
            errores.append(' Este RUT ya está registrado.')
        
        # ========== 9. SI HAY ERRORES, RESPONDER ==========
        if errores:
            if is_ajax:
                # Respuesta JSON para AJAX
                return JsonResponse({
                    'success': False,
                    'message': errores[0]  # Enviamos solo el primer error
                })
            else:
                # Respuesta tradicional (para navegadores sin JS)
                for error in errores:
                    messages.error(request, error)
                return render(request, 'crearUsuario.html')
            
        # ========== 10. CREAR USUARIO ==========
        try:
            usuario = User.objects.create(
                username=username,
                first_name=nombre,
                last_name=apellido,
                email=email,
                password=make_password(password),
                is_staff=False,
                is_superuser=False,
                is_active=True
            )
            usuario.save()

            # ========== GUARDAR RUT EN EL PERFIL ==========
            perfil = usuario.perfil
            perfil.rut = rut_limpio
            perfil.save()

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': ' ¡Usuario creado correctamente! Redirigiendo al inicio de sesión...',
                    'redirect_url': '/login/'
                })
            else:
                messages.success(request, ' ¡Usuario creado correctamente! Ya puedes iniciar sesión.')
                return redirect('login')

        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f' Error al crear usuario: {str(e)}'
                })
            else:
                messages.error(request, f' Error al crear usuario: {str(e)}')
                return render(request, 'crearUsuario.html')
    
    # Si no es POST, mostrar el formulario
    return render(request, 'crearUsuario.html')


# VISTAS DE CATEGORIAS 
def alimentos(request):
    # llama al id de la categoria (Alimentos = id 4)
    productos = Producto.objects.filter(categoria_id=4)
    
    # aplicación de descuento solo a productos destacados
    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None
     # Obtener cantidad del carrito si el usuario está logueado
    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()
        
    return render(request, 'alimentos.html', {'productos': productos, 'cantidad_items': cantidad_carrito})


def aseo(request):
    productos = Producto.objects.filter(categoria_id=5)
    
    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None
    
    # Obtener cantidad del carrito si el usuario está logueado
    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()

    return render(request, 'aseo.html', {'productos': productos, 'cantidad_items': cantidad_carrito})


def bebestibles(request):
    # llamado de ids: 2 = No alcohólicos, 3 = Alcohólicos
    productos = Producto.objects.filter(categoria_id__in=[2, 3])
    
    # descuento del 10% solo para productos destacados
    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None
    
    # Obtener cantidad del carrito si el usuario está logueado
    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()

    return render(request, 'bebestibles.html', {'productos': productos, 'cantidad_items': cantidad_carrito})


def terminosCondiciones(request):
    return render(request, 'terminosCondiciones.html')

# vista muestra datos de producto seleccionado
def desc_producto(request, producto_id):
    
    # Obtener el producto por su ID
    producto = get_object_or_404(Producto, id_producto=producto_id)
    
    # Calcular precio con descuento si aplica
    if producto.mostrar_en_index:
        precio_con_descuento = int(producto.precio * 0.9)
    else:
        precio_con_descuento = None

    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()
    
    context = {
        'producto': producto,
        'precio_con_descuento': precio_con_descuento,
        'cantidad_items': cantidad_carrito
    }

    
    
    return render(request, 'desc_producto.html', context)

# vista para mostrar perfil de usuario registrado en bd 

@login_required
def panel_admin(request):
    # Obtener el usuario actual
    usuario = request.user
    nombre_completo = f"{usuario.first_name} {usuario.last_name}"
    
    # Si el usuario no tiene nombre, mostrar su username
    if not usuario.first_name and not usuario.last_name:
        nombre_completo = usuario.username
    
    return render(request, 'vistas_admin/panel_admin.html', {'nombre_completo': nombre_completo})

def logout(request):
    auth_logout(request)
    return redirect('index')

# vistas para el usuario admin 

@user_passes_test(es_administrador)
def inventario_admin(request):
    # Obtener todos los productos
    productos = Producto.objects.all()
    
    # Obtener todas las categorías para el filtro
    categorias = Categoria.objects.all()
    
    # Verificar en consola cuántos productos hay (para depuración)
    print(f"Productos encontrados: {productos.count()}")
    
    context = {
        'productos': productos,
        'categorias': categorias
    }
    
    return render(request, 'vistas_admin/inventario_admin.html', context)

@user_passes_test(es_administrador)
def administracion_usuarios_admin(request):
    # Obtener todos los usuarios (excluyendo superusuarios si quieres)
    usuarios = User.objects.all().filter(is_superuser=False, is_staff=False).order_by('last_name')
    
    # Preparar datos para la tabla
    lista_usuarios = []
    for user in usuarios:
        lista_usuarios.append({
            'id': user.id,
            'first_name': user.first_name if user.first_name else "No especificado",
            'last_name': user.last_name if user.last_name else "No especificado",
            'rut': user.perfil.rut if hasattr(user, 'perfil') and user.perfil.rut else "No especificado",
            'email': user.email,
            'direccion': user.perfil.direccion if hasattr(user, 'perfil') and user.perfil.direccion else "No especificada",
            'is_active': user.is_active,
            'is_staff': user.is_staff,
        })
    
    context = {
        'usuarios': lista_usuarios,
        'total_usuarios': len(lista_usuarios)
    }
    
    return render(request, 'vistas_admin/administracion_usuarios_admin.html',context)

@user_passes_test(es_administrador)
def estadisticas_admin(request):
    return render(request, 'vistas_admin/estadisticas_admin.html')

#llamado de datos perfil cliente
@login_required
def perfil_cli(request):
    usuario = request.user
    perfil = usuario.perfil
    direccion = perfil.direccion if perfil.direccion else "Domicilio no especificado"
    
    context = {
        'nombre_completo': f"{usuario.first_name} {usuario.last_name}",
        'email': usuario.email,
        'rut': perfil.rut if perfil.rut else "No especificado",
        'direccion': direccion,
        'username': usuario.username,
    }
    return render(request, 'vistas_cliente/perfil_cli.html', context)


#llamado de datos perfil supervisor
@login_required
def perfil_superv(request):
    return render(request, 'perfil_superv.html')


@user_passes_test(es_administrador)
def vista_perfil_admin(request, usuario_id):
    # Obtener el usuario por su ID
    usuario = get_object_or_404(User, id=usuario_id)
    
    # Obtener datos del perfil
    perfil = usuario.perfil if hasattr(usuario, 'perfil') else None
    
    # Preparar datos para la plantilla
    datos_usuario = {
        'id': usuario.id,
        'username': usuario.username,
        'first_name': usuario.first_name if usuario.first_name else "No especificado",
        'last_name': usuario.last_name if usuario.last_name else "No especificado",
        'email': usuario.email,
        'rut': perfil.rut if perfil and perfil.rut else "No especificado",
        'direccion': perfil.direccion if perfil and perfil.direccion else "No especificada",
        'telefono': perfil.telefono if perfil and perfil.telefono else "No especificado",
        'fecha_registro': usuario.date_joined,
        'ultimo_acceso': usuario.last_login,
        'is_active': usuario.is_active,
    }
    
    context = {
        'usuario': datos_usuario
    }
    
    return render(request, 'vistas_admin/vista_perfil_admin.html', context)


#carrito de compras 
@login_required
def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito del usuario y responde con JSON"""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id_producto=producto_id)
        
        # Obtener o crear el carrito del usuario
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        
        # Verificar si el producto ya está en el carrito
        carrito_item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto
        )
        
        if not created:
            # Si ya existe, aumentar la cantidad
            carrito_item.cantidad += 1
            carrito_item.save()
        
        # Actualizar sesión
        request.session['cantidad_carrito'] = carrito.get_cantidad_items()
        
        return JsonResponse({
            'success': True,
            'message': f'{producto.nombre} añadido al carrito',
            'cantidad': carrito_item.cantidad,
            'total_items': carrito.get_cantidad_items()
        })
    
    return JsonResponse({'success': False, 'message': 'Error al agregar producto'})

@login_required
def ver_carrito(request):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    total = carrito.get_total()
    
    # Guardar la cantidad en la sesión para usarla en el navbar
    request.session['cantidad_carrito'] = carrito.get_cantidad_items()
    
    context = {
        'items': items,
        'total': total,
        'cantidad_items': carrito.get_cantidad_items()
    }
    return render(request, 'vistas_cliente/carrito.html', context)

@login_required
def eliminar_del_carrito(request, item_id):
    """Elimina un item del carrito"""
    carrito_item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    carrito = carrito_item.carrito
    carrito_item.delete()
    
    # Actualizar sesión
    request.session['cantidad_carrito'] = carrito.get_cantidad_items()
    
    return redirect('ver_carrito')

@login_required
def actualizar_cantidad(request, item_id):
    """Actualiza la cantidad de un producto en el carrito"""
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito_item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
        carrito = carrito_item.carrito
        
        if cantidad > 0:
            carrito_item.cantidad = cantidad
            carrito_item.save()
        else:
            carrito_item.delete()
        
        # Actualizar sesión
        request.session['cantidad_carrito'] = carrito.get_cantidad_items()
    
    return redirect('ver_carrito')