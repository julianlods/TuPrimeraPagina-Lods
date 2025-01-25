from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import ContenedorForm, ArticuloForm, DisminuirCantidadForm, EditarPerfilForm, EditarPasswordForm, EditarAvatarForm
from .models import Contenedor, Articulo, Perfil
from django.contrib.auth.models import User


def index(request):
    return render(request, 'MiApp/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registro exitoso. Ahora puedes gestionar tus artículos.")
            return redirect('index')
        else:
            messages.error(request, "Error al registrarte. Verifica los datos ingresados.")
    else:
        form = UserCreationForm()

    return render(request, 'MiApp/register.html', {'form': form})


@login_required
def contenedores_view(request):
    # Filtrar solo los contenedores del usuario logueado
    contenedores = Contenedor.objects.filter(usuario=request.user).prefetch_related(
        models.Prefetch(
            'articulos',
            queryset=Articulo.objects.filter(cantidad__gt=0)  # Excluir artículos con cantidad 0
        )
    )

    contenedor_form = ContenedorForm(usuario=request.user)
    articulo_form = ArticuloForm(usuario=request.user)

    if request.method == "POST":
        if "crear_contenedor" in request.POST:
            contenedor_form = ContenedorForm(request.POST, usuario=request.user)
            if contenedor_form.is_valid():
                contenedor_form.save()
                messages.success(request, "Contenedor creado exitosamente.")
                return redirect("contenedores")
            else:
                messages.error(request, "Error al crear el contenedor.")

        elif "crear_articulo" in request.POST:
            articulo_form = ArticuloForm(request.POST, usuario=request.user)
            if articulo_form.is_valid():
                articulo = articulo_form.save(commit=False)
                if articulo.contenedor.usuario != request.user:
                    messages.error(request, "No puedes agregar artículos a contenedores de otros usuarios.")
                else:
                    articulo.save()
                    messages.success(request, "Artículo agregado con éxito.")
                    return redirect("contenedores")
            else:
                messages.error(request, "Error al agregar el artículo. Verifica los datos ingresados.")

    context = {
        "contenedor_form": contenedor_form,
        "articulo_form": articulo_form,
        "contenedores": contenedores,
    }
    return render(request, "MiApp/contenedores.html", context)


@login_required
def consumos_view(request):
    # Filtrar solo los artículos con cantidad mayor a 0 del usuario logueado
    articulos = Articulo.objects.filter(contenedor__usuario=request.user, cantidad__gt=0)
    proximos_a_vencer = articulos.filter(
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

@login_required
def editar_perfil_view(request):
    perfil = request.user.perfil  # Obtener el perfil del usuario logueado

    if request.method == 'POST':
        perfil_form = EditarPerfilForm(request.POST, instance=request.user)
        avatar_form = EditarAvatarForm(request.POST, request.FILES, instance=perfil)
        password_form = EditarPasswordForm(user=request.user, data=request.POST)

        # Validar solo los formularios relevantes
        if perfil_form.is_valid() and avatar_form.is_valid():
            perfil_form.save()
            avatar_form.save()
            messages.success(request, "Perfil actualizado correctamente.")

            # Solo validar y guardar la contraseña si se ingresaron datos en los campos correspondientes
            if (
                request.POST.get('old_password') or
                request.POST.get('new_password1') or
                request.POST.get('new_password2')
            ):
                if password_form.is_valid():
                    user = password_form.save()
                    update_session_auth_hash(request, user)  # Mantener la sesión activa
                    messages.success(request, "Contraseña actualizada correctamente.")
                else:
                    messages.error(request, "Error al cambiar la contraseña. Verifica los datos ingresados.")

            return redirect('editar_perfil')
    else:
        perfil_form = EditarPerfilForm(instance=request.user)
        avatar_form = EditarAvatarForm(instance=perfil)
        password_form = EditarPasswordForm(user=request.user)

    context = {
        'perfil_form': perfil_form,
        'avatar_form': avatar_form,
        'password_form': password_form,
    }
    return render(request, 'MiApp/editar_perfil.html', context)


def acerca_de_view(request):
    return render(request, 'MiApp/acerca_de.html')

def contacto_view(request):
    return render(request, 'MiApp/contacto.html')
