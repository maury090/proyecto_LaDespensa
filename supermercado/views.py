from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Carrito, CarritoItem, Pedido, PedidoItem, PerfilCliente
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
import re
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings


# ========== FUNCIONES DE VERIFICACIÓN DE ROLES ==========
def es_cliente(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'cliente'

def es_supervisor(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'supervisor'

def es_administrador(user):
    return user.is_authenticated and user.is_staff


# ========== VALIDACIÓN DE RUT ==========
def validar_rut_chileno(rut):
    rut = str(rut).replace('.', '').replace('-', '').replace(' ', '').upper()
    if len(rut) < 2:
        return False
    cuerpo = rut[:-1]
    dv_ingresado = rut[-1]
    if not cuerpo.isdigit():
        return False
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    resto = suma % 11
    dv_esperado = 11 - resto
    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)
    return dv_ingresado == dv_esperado


# ========== VISTAS PRINCIPALES ==========
def index(request):
    productos = Producto.objects.filter(mostrar_en_index=True)
    for producto in productos:
        producto.precio_con_descuento = int(producto.precio * 0.9)

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


# ========== LOGIN ==========
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            if user.is_staff or user.is_superuser:
                return redirect('panel_admin')
            elif es_supervisor(user):
                return redirect('panel_supervisor')
            else:
                return redirect('perfil_cli')
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos.')

    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    return redirect('index')


# ========== REGISTRO DE CLIENTE ==========
def crearUsuario(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        nombre = request.POST.get('fname', '').strip()
        apellido = request.POST.get('lname', '').strip()
        rut = request.POST.get('rut', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('pswd1', '')
        password2 = request.POST.get('pswd2', '')
        acepta_terminos = request.POST.get('remember', False)

        errores = []

        if not nombre:
            errores.append(' El nombre es obligatorio.')
        elif len(nombre) < 3:
            errores.append(' El nombre debe tener al menos 3 caracteres.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', nombre):
            errores.append(' El nombre solo puede contener letras.')

        if not apellido:
            errores.append(' El apellido es obligatorio.')
        elif len(apellido) < 3:
            errores.append(' El apellido debe tener al menos 3 caracteres.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', apellido):
            errores.append(' El apellido solo puede contener letras.')

        if not rut:
            errores.append(' El RUT es obligatorio.')
        elif not validar_rut_chileno(rut):
            errores.append(' RUT no válido. Ejemplo: 12345678K o 123456789')

        if not email:
            errores.append(' El correo electrónico es obligatorio.')
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errores.append(' El formato del correo electrónico no es válido.')
        elif User.objects.filter(email=email).exists():
            errores.append(' Este correo electrónico ya está registrado.')

        if not password:
            errores.append(' La contraseña es obligatoria.')
        elif len(password) < 6:
            errores.append(' La contraseña debe tener al menos 6 caracteres.')

        if not password2:
            errores.append(' Debes confirmar tu contraseña.')
        elif password != password2:
            errores.append(' Las contraseñas no coinciden.')

        if not acepta_terminos:
            errores.append(' Debes aceptar los términos y condiciones.')

        rut_limpio = str(rut).replace('.', '').replace('-', '').replace(' ', '').upper()
        username = f"cliente_{rut_limpio}"
        if User.objects.filter(username=username).exists():
            errores.append(' Este RUT ya está registrado.')

        if errores:
            if is_ajax:
                return JsonResponse({'success': False, 'message': errores[0]})
            else:
                for error in errores:
                    messages.error(request, error)
                return render(request, 'crearUsuario.html')

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

            perfil = usuario.perfil
            perfil.rut = rut_limpio
            perfil.rol = 'cliente'  # ← Rol CLIENTE
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
                return JsonResponse({'success': False, 'message': f' Error al crear usuario: {str(e)}'})
            else:
                messages.error(request, f' Error al crear usuario: {str(e)}')
                return render(request, 'crearUsuario.html')

    return render(request, 'crearUsuario.html')


# ========== CATEGORÍAS ==========
def alimentos(request):
    productos = Producto.objects.filter(categoria_id=4)
    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None

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

    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()

    return render(request, 'aseo.html', {'productos': productos, 'cantidad_items': cantidad_carrito})


def bebestibles(request):
    productos = Producto.objects.filter(categoria_id__in=[2, 3])
    for producto in productos:
        if producto.mostrar_en_index:
            producto.precio_con_descuento = int(producto.precio * 0.9)
        else:
            producto.precio_con_descuento = None

    cantidad_carrito = 0
    if request.user.is_authenticated and not request.user.is_staff:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        cantidad_carrito = carrito.get_cantidad_items()

    return render(request, 'bebestibles.html', {'productos': productos, 'cantidad_items': cantidad_carrito})


def terminosCondiciones(request):
    return render(request, 'terminosCondiciones.html')


def desc_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)

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


# ========== VISTAS DE ADMIN ==========
@login_required
def panel_admin(request):
    usuario = request.user
    nombre_completo = f"{usuario.first_name} {usuario.last_name}"
    if not usuario.first_name and not usuario.last_name:
        nombre_completo = usuario.username
    return render(request, 'vistas_admin/panel_admin.html', {'nombre_completo': nombre_completo})


@user_passes_test(es_administrador)
def inventario_admin(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'vistas_admin/inventario_admin.html', {'productos': productos, 'categorias': categorias})


@user_passes_test(es_administrador)
def administracion_usuarios_admin(request):
    usuarios = User.objects.all().filter(is_superuser=False, is_staff=False).order_by('last_name')
    lista_usuarios = []
    
    for user in usuarios:
        # ========== OBTENER RUT ==========
        rut_display = "No especificado"
        
        # 1. Intentar obtener desde el perfil
        if hasattr(user, 'perfil') and user.perfil.rut:
            rut_display = user.perfil.rut
        # 2. Si no, extraer del username
        elif user.username.startswith('super_'):
            rut_display = user.username.replace('super_', '')
        elif user.username.startswith('cliente_'):
            rut_display = user.username.replace('cliente_', '')
        elif user.username.startswith('supervisor_'):
            rut_display = user.username.replace('supervisor_', '')
        # =================================
        
        lista_usuarios.append({
            'id': user.id,
            'first_name': user.first_name if user.first_name else "No especificado",
            'last_name': user.last_name if user.last_name else "No especificado",
            'rut': rut_display,
            'email': user.email,
            'direccion': user.perfil.direccion if hasattr(user, 'perfil') and user.perfil.direccion else "No especificada",
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'rol': user.perfil.rol if hasattr(user, 'perfil') else 'cliente',
        })
    
    context = {
        'usuarios': lista_usuarios,
        'total_usuarios': len(lista_usuarios)
    }
    return render(request, 'vistas_admin/administracion_usuarios_admin.html', context)


@user_passes_test(es_administrador)
def estadisticas_admin(request):
    from django.db.models import Sum, Count

    productos = Producto.objects.all()

    # Producto más vendido
    producto_estrella = None
    ventas_estrella = 0

    for producto in productos:
        total_vendido = PedidoItem.objects.filter(producto=producto).aggregate(total=Sum('cantidad'))['total'] or 0
        if total_vendido > ventas_estrella:
            ventas_estrella = total_vendido
            producto_estrella = producto

    # Producto menos vendido
    producto_menos_vendido = None
    ventas_menos = None

    for producto in productos:
        total_vendido = PedidoItem.objects.filter(producto=producto).aggregate(total=Sum('cantidad'))['total'] or 0
        if ventas_menos is None or total_vendido < ventas_menos:
            ventas_menos = total_vendido
            producto_menos_vendido = producto

    productos_stock_bajo = Producto.objects.filter(stock__lt=20).order_by('stock')

    total_pedidos = Pedido.objects.count()
    total_clientes = User.objects.filter(is_staff=False, is_superuser=False).count()
    ingresos_totales = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0

    context = {
        'producto_estrella': producto_estrella,
        'ventas_estrella': ventas_estrella,
        'producto_menos_vendido': producto_menos_vendido,
        'ventas_menos': ventas_menos,
        'productos_stock_bajo': productos_stock_bajo,
        'total_pedidos': total_pedidos,
        'total_clientes': total_clientes,
        'ingresos_totales': ingresos_totales,
        'total_productos': productos.count(),
    }

    return render(request, 'vistas_admin/estadisticas_admin.html', context)


@user_passes_test(es_administrador)
def otras_est_admin(request):
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import timedelta, datetime

    top_productos = []
    for producto in Producto.objects.all():
        total_vendido = PedidoItem.objects.filter(producto=producto).aggregate(total=Sum('cantidad'))['total'] or 0
        if total_vendido > 0:
            top_productos.append({
                'nombre': producto.nombre,
                'total': total_vendido
            })

    top_productos = sorted(top_productos, key=lambda x: x['total'], reverse=True)[:10]

    fecha_inicio = timezone.now() - timedelta(days=30)
    pedidos = Pedido.objects.filter(fecha__gte=fecha_inicio).order_by('fecha')

    pedidos_por_dia = {}
    for pedido in pedidos:
        fecha_str = pedido.fecha.strftime('%Y-%m-%d')
        if fecha_str not in pedidos_por_dia:
            pedidos_por_dia[fecha_str] = {'total_pedidos': 0, 'total_valor': 0}
        pedidos_por_dia[fecha_str]['total_pedidos'] += 1
        pedidos_por_dia[fecha_str]['total_valor'] += pedido.total

    dias_ordenados = sorted(pedidos_por_dia.keys())

    dias = []
    cantidad_pedidos = []
    valor_pedidos = []

    for fecha_str in dias_ordenados:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        dias.append(fecha_obj.strftime('%d/%m'))
        cantidad_pedidos.append(pedidos_por_dia[fecha_str]['total_pedidos'])
        valor_pedidos.append(pedidos_por_dia[fecha_str]['total_valor'])

    context = {
        'top_productos': top_productos,
        'dias': dias,
        'cantidad_pedidos': cantidad_pedidos,
        'valor_pedidos': valor_pedidos,
    }

    return render(request, 'vistas_admin/otras_est_admin.html', context)


# ========== CREAR SUPERVISOR (ADMIN) ==========
@user_passes_test(es_administrador)
def nuevo_usuario_admin(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        rut = request.POST.get('rut', '').strip()

        if not nombre or not apellido or not rut:
            messages.error(request, '❌ Todos los campos son obligatorios.')
            return render(request, 'vistas_admin/nuevo_usuario_admin.html')

        if not validar_rut_chileno(rut):
            messages.error(request, '❌ RUT no válido.')
            return render(request, 'vistas_admin/nuevo_usuario_admin.html')

        rut_limpio = str(rut).replace('.', '').replace('-', '').replace(' ', '').upper()

        # ========== VALIDACIÓN: YA EXISTE UN SUPERVISOR CON ESTE RUT ==========
        # 1. Verificar en el perfil
        supervisor_existente = PerfilCliente.objects.filter(rut=rut_limpio, rol='supervisor')
        if supervisor_existente.exists():
            messages.error(request, f'❌ Ya existe un supervisor con el RUT {rut_limpio}.')
            return render(request, 'vistas_admin/nuevo_usuario_admin.html')

        # 2. Verificar en el username (por si el RUT quedó en el username)
        usuarios_super = User.objects.filter(username__startswith='super_') | User.objects.filter(username__startswith='supervisor_')
        for user in usuarios_super:
            if rut_limpio in user.username:
                messages.error(request, f'❌ Ya existe un supervisor con el RUT {rut_limpio}.')
                return render(request, 'vistas_admin/nuevo_usuario_admin.html')
        # =========================================================================

        # Generar correo único
        nombre_base = nombre[:2].lower()
        apellido_base = apellido[-2:].lower()
        base_email = f"{nombre_base}{apellido_base}@ladespensa.com"

        email = base_email
        contador = 1
        while User.objects.filter(email=email).exists():
            email = f"{nombre_base}{apellido_base}{contador}@ladespensa.com"
            contador += 1

        # Generar username único
        base_username = f"super_{rut_limpio}"
        username = base_username
        contador_user = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{contador_user}"
            contador_user += 1

        password = username

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

            perfil = usuario.perfil
            perfil.rut = rut_limpio
            perfil.rol = 'supervisor'
            perfil.save()

            messages.success(request, f'✅ Usuario supervisor creado correctamente.')
            messages.info(request, f'📧 Correo: {email}')
            messages.info(request, f'🔑 Contraseña: {password}')

            return redirect('nuevo_usuario_admin')

        except Exception as e:
            messages.error(request, f'❌ Error al crear usuario: {str(e)}')
            return render(request, 'vistas_admin/nuevo_usuario_admin.html')

    return render(request, 'vistas_admin/nuevo_usuario_admin.html')


# ========== VISTAS DE SUPERVISOR ==========
@login_required
def panel_supervisor(request):
    if not es_supervisor(request.user):
        messages.error(request, '❌ Acceso no autorizado.')
        return redirect('index')

    usuario = request.user
    nombre_completo = f"{usuario.first_name} {usuario.last_name}"

    return render(request, 'vistas_supervisor/panel_supervisor.html', {'nombre_completo': nombre_completo})


@login_required
def inventario_supervisor(request):
    if not es_supervisor(request.user):
        messages.error(request, '❌ Acceso no autorizado.')
        return redirect('index')

    productos = Producto.objects.all()
    categorias = Categoria.objects.all()

    context = {
        'productos': productos,
        'categorias': categorias,
    }
    return render(request, 'vistas_supervisor/inventario_supervisor.html', context)


# ========== VISTAS DE CLIENTE ==========
@login_required
def perfil_cli(request):
    if not es_cliente(request.user):
        messages.error(request, '❌ Acceso no autorizado.')
        return redirect('index')

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


@login_required
def actualizarDatos(request):
    usuario = request.user
    perfil = usuario.perfil

    comunas = ['Quillota', 'La Cruz', 'La Calera', 'Nogales', 'Hijuelas']

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

        if not calle:
            messages.error(request, ' Debes ingresar tu calle y número.')
        elif not comuna:
            messages.error(request, ' Debes seleccionar una comuna.')
        else:
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


# ========== PERFIL SUPERVISOR (placeholder) ==========
@login_required
def perfil_superv(request):
    return render(request, 'perfil_superv.html')


# ========== VISTA PERFIL ADMIN ==========
@user_passes_test(es_administrador)
def vista_perfil_admin(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    perfil = usuario.perfil if hasattr(usuario, 'perfil') else None

    # ========== OBTENER RUT ==========
    if perfil and perfil.rut:
        rut_display = perfil.rut
    else:
        # Extraer RUT del username
        username = usuario.username
        if username.startswith('super_'):
            rut_display = username.replace('super_', '')
        elif username.startswith('cliente_'):
            rut_display = username.replace('cliente_', '')
        else:
            rut_display = "No especificado"
    # =================================

    datos_usuario = {
        'id': usuario.id,
        'username': usuario.username,
        'first_name': usuario.first_name if usuario.first_name else "No especificado",
        'last_name': usuario.last_name if usuario.last_name else "No especificado",
        'email': usuario.email,
        'rut': rut_display,  # ← Mostramos el RUT desde donde esté
        'direccion': perfil.direccion if perfil and perfil.direccion else "No especificada",
        'telefono': perfil.telefono if perfil and perfil.telefono else "No especificado",
        'fecha_registro': usuario.date_joined,
        'ultimo_acceso': usuario.last_login,
        'is_active': usuario.is_active,
    }

    context = {'usuario': datos_usuario}
    return render(request, 'vistas_admin/vista_perfil_admin.html', context)


# ========== CARRITO ==========
@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id_producto=producto_id)
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)

        carrito_item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto
        )

        if not created:
            carrito_item.cantidad += 1
            carrito_item.save()

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
    carrito_item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    carrito = carrito_item.carrito
    carrito_item.delete()
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

        request.session['cantidad_carrito'] = carrito.get_cantidad_items()

    return redirect('ver_carrito')


# ========== PEDIDOS ==========
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

    direccion = perfil.direccion if perfil.direccion else 'No especificada'
    tiene_direccion = direccion != 'No especificada' and direccion != 'Domicilio no especificado'

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

    carrito, created = Carrito.objects.get_or_create(usuario=usuario)
    items = carrito.items.all()

    if not items:
        messages.error(request, '❌ Tu carrito está vacío.')
        return redirect('ver_carrito')

    metodo_entrega = request.POST.get('metodo_entrega', 'retiro')

    total = 0
    for item in items:
        if item.producto.mostrar_en_index:
            precio = int(item.producto.precio * 0.9)
        else:
            precio = item.producto.precio
        total += precio * item.cantidad

    if metodo_entrega == 'despacho':
        total += 1000

    direccion = perfil.direccion if perfil.direccion else 'No especificada'

    pedido = Pedido.objects.create(
        usuario=usuario,
        total=total,
        direccion=direccion,
        metodo_entrega=metodo_entrega,
        estado='confirmado'
    )

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

    carrito.items.all().delete()

    messages.success(request, f'✅ ¡Pedido #{pedido.id} confirmado! Gracias por tu compra.')
    return redirect('pago_exitoso')


@login_required
def pago_exitoso(request):
    return render(request, 'vistas_cliente/pago_exitoso.html')


# ========== HISTORIAL DE PEDIDOS ==========
@login_required
def mis_pedidos(request):
    usuario = request.user
    pedidos = Pedido.objects.filter(usuario=usuario).order_by('-fecha')

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


@login_required
def detalle_pedido(request, pedido_id):
    usuario = request.user
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=usuario)
    items = pedido.items.all()

    context = {
        'pedido': pedido,
        'items': items,
        'total_items': items.count(),
        'total_productos': sum(item.cantidad for item in items)
    }

    return render(request, 'vistas_cliente/detallePedido.html', context)


#admin eliminacion de usuario registrado
@user_passes_test(es_administrador)
def eliminar_usuario_admin(request, usuario_id):
    """Elimina un usuario del sistema (solo administradores)"""
    usuario = get_object_or_404(User, id=usuario_id)
    
    # Evitar que el admin se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, '❌ No puedes eliminar tu propio usuario.')
        return redirect('vista_perfil_admin', usuario_id=usuario_id)
    
    # Evitar eliminar superusuarios
    if usuario.is_superuser:
        messages.error(request, '❌ No puedes eliminar un superusuario.')
        return redirect('vista_perfil_admin', usuario_id=usuario_id)
    
    nombre = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
    usuario.delete()
    
    messages.success(request, f'✅ Usuario "{nombre}" eliminado correctamente.')
    return redirect('administracion_usuarios_admin')








@user_passes_test(es_administrador)
def agregar_producto(request):
    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        precio = request.POST.get('precio', '').strip()
        stock = request.POST.get('stock', 0)
        categoria_id = request.POST.get('categoria', '').strip()
        mostrar_en_index = request.POST.get('mostrar_en_index', False) == 'on'
        imagen = request.FILES.get('imagen', None)
        
        # Validaciones
        if not codigo:
            messages.error(request, '❌ El código es obligatorio.')
            return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})
        
        if Producto.objects.filter(codigo=codigo).exists():
            messages.error(request, '❌ Ya existe un producto con este código.')
            return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})
        
        if not nombre:
            messages.error(request, '❌ El nombre es obligatorio.')
            return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})
        
        if not precio:
            messages.error(request, '❌ El precio es obligatorio.')
            return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})
        
        try:
            precio = int(precio)
            stock = int(stock)
        except ValueError:
            messages.error(request, '❌ Precio y stock deben ser números.')
            return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})
        
        if not categoria_id:
            messages.error(request, '❌ Debes seleccionar una categoría.')
            return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})
        
        try:
            categoria = Categoria.objects.get(id_categoria=categoria_id)
        except Categoria.DoesNotExist:
            messages.error(request, '❌ Categoría no válida.')
            return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})
        
        # Crear producto
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria,
            mostrar_en_index=mostrar_en_index,
        )
        
        if imagen:
            producto.imagen = imagen
        
        producto.save()
        
        messages.success(request, f'✅ Producto "{nombre}" creado correctamente.')
        return redirect('agregar_producto')
    
    return render(request, 'vistas_admin/agregar_producto.html', {'categorias': categorias})




@user_passes_test(es_administrador)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    nombre_producto = producto.nombre
    producto.delete()
    
    messages.success(request, f'✅ Producto "{nombre_producto}" eliminado correctamente.')
    return redirect('inventario_admin')

@user_passes_test(es_administrador)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion', '').strip()
        precio = request.POST.get('precio', '').strip()
        stock = request.POST.get('stock', 0)
        mostrar_en_index = request.POST.get('mostrar_en_index', False) == 'on'
        imagen = request.FILES.get('imagen', None)
        
        # Validaciones
        if not precio:
            messages.error(request, '❌ El precio es obligatorio.')
            return render(request, 'vistas_admin/editar_producto.html', {
                'producto': producto,
                'categorias': categorias
            })
        
        try:
            precio = int(precio)
            stock = int(stock)
        except ValueError:
            messages.error(request, '❌ Precio y stock deben ser números.')
            return render(request, 'vistas_admin/editar_producto.html', {
                'producto': producto,
                'categorias': categorias
            })
        
        # Actualizar campos editables
        producto.descripcion = descripcion
        producto.precio = precio
        producto.stock = stock
        producto.mostrar_en_index = mostrar_en_index
        
        if imagen:
            producto.imagen = imagen
        
        producto.save()
        
        messages.success(request, f'✅ Producto "{producto.nombre}" actualizado correctamente.')
        return redirect('inventario_admin')
    
    context = {
        'producto': producto,
        'categorias': categorias,
    }
    return render(request, 'vistas_admin/editar_producto.html', context)

#supervisor 
@login_required
def panel_supervisor(request):
    if not es_supervisor(request.user):
        messages.error(request, '❌ Acceso no autorizado.')
        return redirect('index')
    
    usuario = request.user
    nombre_completo = f"{usuario.first_name} {usuario.last_name}"
    if not usuario.first_name and not usuario.last_name:
        nombre_completo = usuario.username
    
    return render(request, 'vistas_supervisor/panel_supervisor.html', {'nombre_completo': nombre_completo})

@login_required
def ver_pedidos_supervisor(request):
    if not es_supervisor(request.user):
        messages.error(request, '❌ Acceso no autorizado.')
        return redirect('index')
    
    # Obtener todos los pedidos con sus clientes
    pedidos = Pedido.objects.all().order_by('-fecha')
    
    # Preparar datos para la tabla
    pedidos_data = []
    for pedido in pedidos:
        pedidos_data.append({
            'pedido': pedido,
            'cliente': f"{pedido.usuario.first_name} {pedido.usuario.last_name}",
            'total_items': pedido.items.count(),
        })
    
    context = {
        'pedidos': pedidos_data,
        'total_pedidos': len(pedidos_data),
    }
    
    return render(request, 'vistas_supervisor/ver_pedidos_supervisor.html', context)


@login_required
def detalle_pedido_supervisor(request, pedido_id):
    if not es_supervisor(request.user):
        messages.error(request, '❌ Acceso no autorizado.')
        return redirect('index')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    items = pedido.items.all()
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'✅ Estado del pedido actualizado a "{pedido.get_estado_display()}".')
            return redirect('detalle_pedido_supervisor', pedido_id=pedido.id)
    
    context = {
        'pedido': pedido,
        'items': items,
        'estados': Pedido.ESTADO_CHOICES,
    }
    return render(request, 'vistas_supervisor/detalle_pedido_supervisor.html', context)