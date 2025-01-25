# MiApp/forms.py
from django import forms
from .models import Contenedor, Articulo
from django.forms import DateInput
from django.contrib.auth.models import User
from .models import Perfil
from django.contrib.auth.forms import PasswordChangeForm


# Define las opciones de unidades de medida
UNIDADES_MEDIDA_CHOICES = [
    ('UN', 'Unidad'), 
    ('KG', 'Kilogramos'), 
    ('GR', 'Gramos'), 
    ('LT', 'Litros'),
    # Agrega más unidades según sea necesario
]

class DisminuirCantidadForm(forms.Form):
    cantidad_a_eliminar = forms.FloatField(min_value=0, label="Cantidad a eliminar")


class ContenedorForm(forms.ModelForm):
    class Meta:
        model = Contenedor
        fields = ['nombre']

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)  # Usuario logueado
        super().__init__(*args, **kwargs)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Contenedor.objects.filter(nombre=nombre, usuario=self.usuario).exists():
            raise forms.ValidationError("Ya tienes un contenedor con este nombre.")
        return nombre

    def save(self, commit=True):
        contenedor = super().save(commit=False)
        if self.usuario:
            contenedor.usuario = self.usuario  # Asociar el contenedor al usuario logueado
        if commit:
            contenedor.save()
        return contenedor


class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['nombre', 'cantidad', 'unidad_medida', 'fecha_ingreso', 'fecha_vencimiento', 'contenedor']
        widgets = {
            'fecha_ingreso': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_vencimiento': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # Recibe el usuario logueado como argumento
        super().__init__(*args, **kwargs)
        if usuario:
            # Filtra los contenedores para que solo se muestren los del usuario logueado
            self.fields['contenedor'].queryset = Contenedor.objects.filter(usuario=usuario)

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        unidad_medida = cleaned_data.get('unidad_medida')

        if cantidad is None:
            raise forms.ValidationError("La cantidad es obligatoria.")
        if unidad_medida is None:
            raise forms.ValidationError("La unidad de medida es obligatoria.")

        # Validación adicional para unidades específicas
        if unidad_medida in ['UN', 'LT'] and not cantidad.is_integer():
            raise forms.ValidationError("La cantidad para unidades como UN o LT debe ser un número entero.")

        return cleaned_data


from django.shortcuts import render, redirect
from .forms import ContenedorForm
from .models import Contenedor

def contenedores_view(request):
    if request.method == 'POST':
        contenedor_form = ContenedorForm(request.POST)
        if contenedor_form.is_valid():
            contenedor_form.save()
            return redirect('contenedores')  # Redirige después de guardar
    else:
        contenedor_form = ContenedorForm()

    # Asegúrate de pasar el formulario al contexto
    context = {
        'contenedor_form': contenedor_form,
        'contenedores': Contenedor.objects.all()
    }
    return render(request, 'MiApp/contenedores.html', context)


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
        }


class EditarPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        # Si no se ingresó ningún campo de contraseña, omitir la validación
        cleaned_data = super().clean()
        if not self.cleaned_data.get('old_password') and not self.cleaned_data.get('new_password1') and not self.cleaned_data.get('new_password2'):
            raise ValidationError("Completa los campos si deseas cambiar la contraseña.")
        return cleaned_data


class EditarAvatarForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
