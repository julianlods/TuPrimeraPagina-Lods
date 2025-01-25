from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default-avatar.png',  # Imagen por defecto
        blank=True
    )

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class Contenedor(models.Model):
    nombre = models.CharField(max_length=100)  # Se elimina unique=True
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contenedores")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'usuario'], name='unique_contenedor_per_user')
        ]

    def __str__(self):
        return self.nombre


class Articulo(models.Model):
    UNIDAD_MEDIDA_CHOICES = [
        ('UN', 'Unidad'),
        ('KG', 'Kilogramos'),
        ('LT', 'Litros'),
        ('GR', 'Gramos')
    ]

    nombre = models.CharField(max_length=100)
    cantidad = models.FloatField()
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_MEDIDA_CHOICES)
    fecha_ingreso = models.DateField()
    fecha_vencimiento = models.DateField()
    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name="articulos")

    def clean(self):
        if self.cantidad is not None:
            # Validar cantidad según la unidad de medida
            if self.unidad_medida in ['UN', 'LT'] and not self.cantidad.is_integer():
                raise ValidationError(f"La cantidad para la unidad {self.get_unidad_medida_display()} debe ser un número entero.")
            elif self.unidad_medida in ['KG', 'GR']:
                # Verificar que solo tiene un decimal
                if round(self.cantidad, 1) != self.cantidad:
                    raise ValidationError(f"La cantidad para la unidad {self.get_unidad_medida_display()} debe tener como máximo un decimal.")

    def save(self, *args, **kwargs):
        self.clean()  # Llamar a clean antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad_medida})"

class RegistroSalida(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name="salidas")
    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name="salidas")
    cantidad = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"Salida de {self.cantidad} {self.articulo.unidad_medida} de "
                f"{self.articulo.nombre} del contenedor {self.contenedor.nombre} en {self.fecha}")
