from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='MiApp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('editar-perfil/', views.editar_perfil_view, name='editar_perfil'),
    path('contenedores/', views.contenedores_view, name='contenedores'),
    path('consumos/', views.consumos_view, name='consumos'),
    path('dar_baja/', views.dar_baja_view, name='dar_baja'),
    path('disminuir_cantidad/<int:articulo_id>/', views.disminuir_cantidad, name='disminuir_cantidad'),
    path('agregar-articulo/', views.agregar_articulo, name='agregar_articulo'),
    path('acerca-de/', views.acerca_de_view, name='acerca_de'),
    path('contacto/', views.contacto_view, name='contacto'),
]
