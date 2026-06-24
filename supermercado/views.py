from django.shortcuts import render, redirect
from .models import Producto, Categoria , Carrito, CarritoItem, Pedido, PedidoItem
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
import mercadopago
from django.conf import settings



# Función para verificar si es administrador
def es_administrador(user):
    return user.is_authenticated and user.is_staff

# validacion de rut 
def validar_rut_chileno(rut):
    
    # Limpiar el RUT: eliminar puntos, guiones y espacios
    rut = str(rut).replace('.', '').replace('-', '').replace(' ', '').upper()
    
    # Verificar formato básico (solo números y posible K al final)
    if len(rut) < 2:
        return False
    
    cuerpo = rut[:-1]  #cuerpo del rut
    dv_ingresado = rut[-1]  #dv
    
    # validar que el cuerpo solo tenga números
    if not cuerpo.isdigit():
        return False
    
    # calcular dígito verificador correspondiente al calculo del rut
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
    
    # convertir según las reglas del rut
    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)
    
    # comparar el dígito ingresado con el esperado
    return dv_ingresado == dv_esperado


# vistas principales del proyecto
def index(request):

    # obtener productos marcados para mostrar en el index
    productos = Producto.objects.filter(mostrar_en_index=True)
    
    # 10% desc para prodcutos mostrados en index 
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
        
        # validacion nombre
        if not nombre:
            errores.append(' El nombre es obligatorio.')
        elif len(nombre) < 3:
            errores.append(' El nombre debe tener al menos 3 caracteres.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', nombre):
            errores.append(' El nombre solo puede contener letras.')
        
        # validacion apellido
        if not apellido:
            errores.append(' El apellido es obligatorio.')
        elif len(apellido) < 3:
            errores.append(' El apellido debe tener al menos 3 caracteres.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', apellido):
            errores.append(' El apellido solo puede contener letras.')
        
        # val rut
        if not rut:
            errores.append(' El RUT es obligatorio.')
        elif not validar_rut_chileno(rut):
            errores.append(' RUT no válido. Ejemplo: 12345678K o 123456789')
        
        # validacion correo
        if not email:
            errores.append(' El correo electrónico es obligatorio.')
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errores.append(' El formato del correo electrónico no es válido.')
        elif User.objects.filter(email=email).exists():
            errores.append(' Este correo electrónico ya está registrado.')
        
        # validacion password
        if not password:
            errores.append(' La contraseña es obligatoria.')
        elif len(password) < 6:
            errores.append(' La contraseña debe tener al menos 6 caracteres.')
        
        # confirmacion password
        if not password2:
            errores.append(' Debes confirmar tu contraseña.')
        elif password != password2:
            errores.append(' Las contraseñas no coinciden.')
        
        # terminos y condiciones
        if not acepta_terminos:
            errores.append(' Debes aceptar los términos y condiciones.')
        
        # rut no duplicado
        # Limpiar RUT para usar como username
        rut_limpio = str(rut).replace('.', '').replace('-', '').replace(' ', '').upper()
        username = f"cliente_{rut_limpio}"
        if User.objects.filter(username=username).exists():
            errores.append(' Este RUT ya está registrado.')
        
        # respuesta en caso de errores
        if errores:
            if is_ajax:
                # Respuesta JSON para AJAX
                return JsonResponse({
                    'success': False,
                    'message': errores[0]  
                })
            else:
                
                for error in errores:
                    messages.error(request, error)
                return render(request, 'crearUsuario.html')
            
        # creacion de usuario si no hay errores 
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

            # guardado de rut en perfil cliente
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
    
    
    return render(request, 'crearUsuario.html')


# categorias de productos  
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

#actualizacion de datos cliente 
@login_required
def actualizarDatos(request):
    usuario = request.user
    perfil = usuario.perfil
    
    # Lista de comunas de la provincia de Quillota
    comunas = [
        'Quillota',
        'La Cruz',
        'La Calera',
        'Nogales',
        'Hijuelas'
    ]
    
    # Separar dirección actual (si existe)
    direccion_actual = perfil.direccion if perfil.direccion else ''
    calle_actual = ''
    comuna_actual = 'Quillota'
    
    if direccion_actual and ', ' in direccion_actual:
        partes = direccion_actual.rsplit(', ', 1)
        calle_actual = partes[0]
        comuna_actual = partes[1] if partes[1] in comunas else 'Quillota'
    
    if request.method == 'POST':
        calle = request.POST.get('calle', '').strip()
        comuna = request.POST.get('comuna', '')
        
        # Validar campos de dirección
        if not calle:
            messages.error(request, ' Debes ingresar tu calle y número.')
        elif not comuna:
            messages.error(request, ' Debes seleccionar una comuna.')
        else:
            # Guardar dirección completa
            direccion_completa = f"{calle}, {comuna}"
            perfil.direccion = direccion_completa
            perfil.save()
            
            messages.success(request, ' Dirección actualizada correctamente.')
            return redirect('perfil_cli')
    
    context = {
        'nombre': usuario.first_name,
        'apellido': usuario.last_name,
        'email': usuario.email,
        'comunas': comunas,
        'calle_actual': calle_actual,
        'comuna_actual': comuna_actual,
    }
    return render(request, 'vistas_cliente/actualizarDatos.html', context)


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
    
    # Calcular total con descuento
    total = 0
    for item in items:
        if item.producto.mostrar_en_index:
            total += item.cantidad * int(item.producto.precio * 0.9)
        else:
            total += item.get_subtotal()
    
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
def actualizar_todo_carrito(request):
    if request.method == 'POST':
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        
        for item in carrito.items.all():
            cantidad_key = f'cantidad_{item.id}'
            if cantidad_key in request.POST:
                nueva_cantidad = int(request.POST.get(cantidad_key, 0))
                if nueva_cantidad > 0:
                    item.cantidad = nueva_cantidad
                    item.save()
                else:
                    item.delete()
        
        # Actualizar sesión
        request.session['cantidad_carrito'] = carrito.get_cantidad_items()
        
    return redirect('ver_carrito')

#vista preparacion de pedido previo pago
@login_required
def revisionPedido(request):
    usuario = request.user
    perfil = usuario.perfil
    
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)
    items = carrito.items.all()
    
    if not items:
        messages.warning(request, '❌ Tu carrito está vacío.')
        return redirect('ver_carrito')
    
    total = 0
    for item in items:
        if item.producto.mostrar_en_index:
            precio_item = int(item.producto.precio * 0.9)
            total += item.cantidad * precio_item
        else:
            total += item.get_subtotal()
    
    rut = perfil.rut if perfil.rut else 'No especificado'
    if rut and rut != 'No especificado' and len(rut) > 1:
        if rut[-1].isdigit():
            rut_formateado = f"{rut[:-1]}-{rut[-1]}"
        else:
            rut_formateado = f"{rut[:-1]}-{rut[-1].upper()}"
    else:
        rut_formateado = 'No especificado'
    
    # ========== CORRECCIÓN ==========
    direccion = perfil.direccion if perfil.direccion else 'No especificada'
    tiene_direccion = direccion != 'No especificada' and direccion != 'Domicilio no especificado'
    # =================================
    
    costo_despacho = 1000
    
    context = {
        'items': items,
        'total': total,
        'nombre': usuario.first_name,
        'apellido': usuario.last_name,
        'rut': rut_formateado,
        'direccion': direccion,
        'tiene_direccion': tiene_direccion,
        'costo_despacho': costo_despacho,
        'cantidad_items': carrito.get_cantidad_items(),
        'MERCADO_PAGO_PUBLIC_KEY': settings.MERCADO_PAGO_PUBLIC_KEY,
    }
    return render(request, 'vistas_cliente/revisionPedido.html', context)

@login_required
def confirmar_pedido(request):
    if request.method != 'POST':
        return redirect('revisionPedido')
    
    usuario = request.user
    perfil = usuario.perfil
    
    # Obtener carrito
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)
    items = carrito.items.all()
    
    if not items:
        messages.error(request, '❌ Tu carrito está vacío.')
        return redirect('ver_carrito')
    
    # Obtener método de entrega
    metodo_entrega = request.POST.get('metodo_entrega', 'retiro')
    
    # Calcular total
    total = 0
    for item in items:
        if item.producto.mostrar_en_index:
            precio = int(item.producto.precio * 0.9)
        else:
            precio = item.producto.precio
        total += precio * item.cantidad
    
    if metodo_entrega == 'despacho':
        total += 1000
    
    # Obtener dirección
    direccion = perfil.direccion if perfil.direccion else 'No especificada'
    
    # Crear pedido
    pedido = Pedido.objects.create(
        usuario=usuario,
        total=total,
        direccion=direccion,
        metodo_entrega=metodo_entrega,
        estado='confirmado'
    )
    
    # Crear items del pedido
    for item in items:
        if item.producto.mostrar_en_index:
            precio = int(item.producto.precio * 0.9)
        else:
            precio = item.producto.precio
        
        PedidoItem.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=precio,
            subtotal=precio * item.cantidad
        )
    
    # Vaciar carrito
    carrito.items.all().delete()
    
    messages.success(request, f'✅ ¡Pedido #{pedido.id} confirmado! Gracias por tu compra.')
    return redirect('pago_exitoso')

@login_required
def pago_exitoso(request):
    """Página de confirmación de pedido exitoso"""
    return render(request, 'vistas_cliente/pago_exitoso.html')


# vista de pedidos del cliente
@login_required
def mis_pedidos(request):
    """Muestra el historial de pedidos del usuario"""
    usuario = request.user
    
    # Obtener todos los pedidos del usuario, ordenados por fecha (más reciente primero)
    pedidos = Pedido.objects.filter(usuario=usuario).order_by('-fecha')
    
    # Preparar datos para cada pedido
    pedidos_data = []
    for pedido in pedidos:
        items = pedido.items.all()
        pedidos_data.append({
            'pedido': pedido,
            'items': items,
            'total_items': items.count(),
            'total_productos': sum(item.cantidad for item in items)
        })
    
    context = {
        'pedidos': pedidos_data,
        'total_pedidos': len(pedidos_data)
    }
    
    return render(request, 'vistas_cliente/misPedidos.html', context)