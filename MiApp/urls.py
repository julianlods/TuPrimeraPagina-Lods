from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contenedores/', views.contenedores_view, name='contenedores'),  # Ruta para contenedores
    path('consumos/', views.consumos_view, name='consumos'),
    path('dar_baja/', views.dar_baja_view, name='dar_baja'),
    path('disminuir_cantidad/<int:articulo_id>/', views.disminuir_cantidad, name='disminuir_cantidad'), 
    path('agregar-articulo/', views.agregar_articulo, name='agregar_articulo'),
]
