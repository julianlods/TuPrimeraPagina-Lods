from django.contrib import admin
from .models import Contenedor, Articulo, RegistroSalida, Perfil

class ContenedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario')  # Muestra el nombre y el usuario
    search_fields = ('nombre', 'usuario__username')  # Permite buscar por nombre y usuario
    ordering = ('nombre',)  # Ordena por nombre

class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'unidad_medida', 'fecha_ingreso', 'fecha_vencimiento', 'contenedor')  # Muestra información relevante
    search_fields = ('nombre', 'contenedor__nombre')  # Permite buscar por nombre y contenedor
    list_filter = ('unidad_medida', 'contenedor')  # Filtrar por unidad de medida y contenedor
    ordering = ('nombre',)  # Ordena por nombre

    def get_list_display(self, request):
        return ('nombre', 'cantidad', 'unidad_medida', 'fecha_ingreso', 'fecha_vencimiento', 'contenedor')  # Cambia la lista de campos a mostrar

    def clean(self, obj):
        # Llamamos a la validación personalizada aquí si es necesario
        try:
            obj.clean()
        except ValidationError as e:
            raise e

class RegistroSalidaAdmin(admin.ModelAdmin):
    list_display = ('articulo', 'contenedor', 'cantidad', 'fecha')  # Muestra la información de la salida
    search_fields = ('articulo__nombre', 'contenedor__nombre')  # Permite buscar por artículo y contenedor
    list_filter = ('fecha',)  # Filtrar por fecha
    ordering = ('-fecha',)  # Ordena por fecha de forma descendente

# Agregar la clase Perfil al admin
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'avatar')  # Muestra el usuario y el avatar
    search_fields = ('usuario__username',)  # Permite buscar por el nombre de usuario
    ordering = ('usuario__username',)  # Ordena por nombre de usuario

admin.site.register(Contenedor, ContenedorAdmin)
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(RegistroSalida, RegistroSalidaAdmin)
admin.site.register(Perfil, PerfilAdmin)
