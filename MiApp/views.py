from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import ContenedorForm, ArticuloForm, DisminuirCantidadForm
from .models import Contenedor, Articulo

def index(request):
    return render(request, 'MiApp/index.html')

def contenedores_view(request):
    contenedor_form = ContenedorForm()
    articulo_form = ArticuloForm()

    if request.method == "POST":
        if "crear_contenedor" in request.POST:
            contenedor_form = ContenedorForm(request.POST)
            if contenedor_form.is_valid():
                contenedor_form.save()
                messages.success(request, "Contenedor creado exitosamente.")
                return redirect("contenedores")  # Ajusta el nombre de tu vista o URL
            else:
                messages.error(request, "Error al crear el contenedor.")
        
        elif "crear_articulo" in request.POST:
            articulo_form = ArticuloForm(request.POST)
            if articulo_form.is_valid():
                articulo_form.save()
                messages.success(request, "Artículo agregado con éxito.")
                return redirect("contenedores")
            else:
                messages.error(request, "Error al agregar el artículo. Verifica los datos ingresados.")

    contenedores = Contenedor.objects.prefetch_related("articulos").all()
    context = {
        "contenedor_form": contenedor_form,
        "articulo_form": articulo_form,
        "contenedores": contenedores,
    }
    return render(request, "MiApp/contenedores.html", context)

def consumos_view(request):
    articulos = Articulo.objects.all()
    proximos_a_vencer = Articulo.objects.filter(
        fecha_vencimiento__lte=timezone.now() + timedelta(days=30)
    )

    return render(request, 'MiApp/consumos.html', {
        'articulos': articulos,
        'proximos_a_vencer': proximos_a_vencer,
    })

def dar_baja_view(request):
    if request.method == 'POST':
        articulo_id = request.POST.get('articulo')
        articulo = get_object_or_404(Articulo, id=articulo_id)
        articulo.delete()
        messages.success(request, "Artículo eliminado correctamente.")
        return redirect('consumos')

    return redirect('consumos')

def disminuir_cantidad(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)

    if request.method == 'POST':
        form = DisminuirCantidadForm(request.POST)
        if form.is_valid():
            cantidad_a_eliminar = form.cleaned_data['cantidad_a_eliminar']

            if cantidad_a_eliminar > articulo.cantidad:
                messages.error(request, "La cantidad a eliminar no puede ser mayor que la cantidad disponible.")
                return redirect('disminuir_cantidad', articulo_id=articulo.id)

            articulo.cantidad -= cantidad_a_eliminar
            articulo.save(update_fields=['cantidad'])
            messages.success(request, f"Se han eliminado {cantidad_a_eliminar} unidades de {articulo.nombre}.")
            return redirect('consumos')

    else:
        form = DisminuirCantidadForm()

    return render(request, 'MiApp/disminuir_cantidad.html', {'form': form, 'articulo': articulo})

def agregar_articulo(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Artículo agregado con éxito.")
            return redirect('contenedores')
        else:
            messages.error(request, "Error al agregar el artículo. Verifica los datos ingresados.")
    else:
        form = ArticuloForm()

    return render(request, 'MiApp/formulario_articulo.html', {'form': form})
