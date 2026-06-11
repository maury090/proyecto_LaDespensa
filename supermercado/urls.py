from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('conocenos/', views.conocenos, name='conocenos'),
    path('login/', views.login, name='login'),
    path('crearUsuario/', views.crearUsuario, name='crearUsuario'),
    path('alimentos/', views.alimentos, name='alimentos'),
    path('aseo/', views.aseo, name='aseo'),
    path('bebestibles/', views.bebestibles, name='bebestibles'),
    path('terminosCondiciones/', views.terminosCondiciones, name='terminosCondiciones'),
    path('vistas_admin/panel_admin/', views.panel_admin, name='panel_admin'),
    path('logout/', views.logout, name='logout'),
    path('vistas_admin/inventario_admin/', views.inventario_admin, name='inventario_admin'),
    path('vistas_admin/administracion_usuarios_admin/', views.administracion_usuarios_admin, name='administracion_usuarios_admin'),
    path('vistas_admin/estadisticas_admin/', views.estadisticas_admin, name='estadisticas_admin'),
    path('vistas_cliente/perfil_cli/', views.perfil_cli, name='perfil_cli'),
    path('vistas_supervisor/perfil_superv/', views.perfil_superv, name='perfil_superv'),
    path('vistas_admin/vista_perfil_admin/<int:usuario_id>/', views.vista_perfil_admin, name='vista_perfil_admin'),
    path('producto/<int:producto_id>/', views.desc_producto, name='desc_producto'),

    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
]

