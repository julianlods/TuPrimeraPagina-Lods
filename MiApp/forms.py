# MiApp/forms.py
from django import forms
from .models import Contenedor, Articulo
from django.forms import DateInput

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

class ArticuloForm(forms.ModelForm):
    unidad_medida = forms.ChoiceField(choices=UNIDADES_MEDIDA_CHOICES)  # Añadir este campo

    class Meta:
        model = Articulo
        fields = ['nombre', 'cantidad', 'unidad_medida', 'fecha_ingreso', 'fecha_vencimiento', 'contenedor']
        widgets = {
            'fecha_ingreso': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_vencimiento': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    # Opcional: Personalizar la visualización de los campos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contenedor'].queryset = Contenedor.objects.all()
        self.fields['cantidad'].widget.attrs.update({'min': '0'})  # Para asegurar valores no negativos


    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        unidad_medida = self.cleaned_data.get('unidad_medida')

        if cantidad is None or unidad_medida is None:
            raise forms.ValidationError("La cantidad y la unidad de medida son obligatorias.")
        
        # Valida que la cantidad sea positiva
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        
        return cantidad

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
