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
]

