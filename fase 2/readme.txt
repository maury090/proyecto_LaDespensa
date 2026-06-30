# La Despensa

## Descripción

La Despensa es una aplicación web desarrollada para la gestión de productos, inventario y pedidos. El sistema permite administrar el catálogo de productos, controlar el stock disponible y gestionar el proceso de compra mediante un carrito de compras y la generación de pedidos.

La aplicación implementa distintos perfiles de usuario con permisos específicos para la administración del sistema y el seguimiento de las operaciones realizadas.

---

## Objetivos

El sistema tiene como objetivo proporcionar una plataforma que permita:

- Administrar productos y categorías.
- Gestionar el inventario disponible.
- Controlar el flujo de pedidos.
- Facilitar el proceso de compra de los clientes.
- Administrar usuarios con distintos niveles de acceso.

---

## Características

### Gestión de usuarios

- Autenticación de usuarios.
- Administración de perfiles.
- Control de acceso por roles.
- Actualización de información personal.

### Gestión de productos

- Registro de productos.
- Modificación de productos.
- Eliminación de productos.
- Gestión de categorías.
- Administración de stock.

### Gestión de pedidos

- Carrito de compras.
- Confirmación de pedidos.
- Historial de pedidos.
- Consulta del detalle de cada pedido.
- Administración del estado de los pedidos.

---

## Arquitectura

El proyecto fue desarrollado utilizando el patrón de arquitectura MTV (Model–Template–View) implementado por Django.

La estructura principal se organiza en:

- Modelos
- Vistas
- Formularios
- Plantillas
- Archivos estáticos
- Recursos multimedia

---

## Tecnologías utilizadas

### Backend

- Python
- Django

### Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript

### Base de datos

- SQLite

---

## Modelo de datos

El sistema se encuentra dividido en los siguientes módulos:

### Usuarios

- Usuario
- PerfilCliente

### Productos

- Categoría
- Producto

### Pedidos

- Carrito
- CarritoItem
- Pedido
- PedidoItem

---

## Instalación

Clonar el repositorio

```bash
git clone https://github.com/maury090/proyecto_LaDespensa.git
```

Ingresar al directorio

```bash
cd proyecto_LaDespensa
```

Crear un entorno virtual

```bash
python -m venv venv
```

Activar el entorno virtual

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

Instalar dependencias

```bash
pip install -r requirements.txt
```

Aplicar migraciones

```bash
python manage.py migrate
```

Ejecutar el servidor

```bash
python manage.py runserver
```

---

## Estructura del proyecto

```
proyecto_LaDespensa/
│
├── despensa/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│
├── media/
├── manage.py
├── db.sqlite3
└── requirements.txt
```

---

## Seguridad

El sistema incorpora mecanismos de seguridad proporcionados por Django, entre ellos:

- Autenticación mediante sesiones.
- Cifrado de contraseñas.
- Protección CSRF.
- Validación de formularios.
- Control de acceso según permisos del usuario.

---

## Funcionalidades implementadas

- Gestión de usuarios.
- Gestión de productos.
- Gestión de categorías.
- Gestión de inventario.
- Carrito de compras.
- Gestión de pedidos.
- Consulta del historial de pedidos.
- Panel administrativo.
- Panel de supervisor.

---

## Posibles mejoras

- Reportes en PDF.
- Exportación a Excel.
- API REST.
- Integración con pasarelas de pago.
- Notificaciones automáticas.
- Panel de estadísticas avanzado.

---

## Licencia

Este proyecto se distribuye únicamente con fines educativos y de demostración.