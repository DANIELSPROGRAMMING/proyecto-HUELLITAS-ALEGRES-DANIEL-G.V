from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from usuarios.decorators import role_required
from .models import Servicio, CATEGORIAS_SERVICIO
from .forms import ServicioForm


@login_required(login_url='/usuarios/login/')
def catalogo_servicios(request):
    """Catálogo de servicios para Cliente — vista de tarjetas con opción de agendar.

    Cualquier usuario autenticado puede ver los servicios.
    Los servicios se muestran en tarjetas con imagen, nombre, duración y tarifa.
    El botón 'Agendar' redirige al formulario de cita con el servicio pre-seleccionado.
    """
    qs = Servicio.objects.order_by('categoria', 'nombre')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(nombre__icontains=search) | Q(descripcion__icontains=search)
        )

    categoria = request.GET.get('categoria', '').strip()
    if categoria:
        qs = qs.filter(categoria=categoria)

    paginator = Paginator(qs, 9)  # 9 per page (3×3 grid)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'servicios/catalogo_servicios.html', {
        'page_obj': page_obj,
        'search': search,
        'categoria': categoria,
        'categorias': CATEGORIAS_SERVICIO,
    })


@login_required(login_url='/usuarios/login/')
def lista_servicios(request):
    """Lista de servicios activos — cualquier usuario autenticado puede ver."""
    qs = Servicio.objects.order_by('nombre')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(nombre__icontains=search)
            | Q(descripcion__icontains=search)
        )

    categoria = request.GET.get('categoria', '').strip()
    if categoria:
        qs = qs.filter(categoria=categoria)

    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'servicios/servicio_list.html', {
        'page_obj': page_obj,
        'search': search,
        'categoria': categoria,
        'categorias': CATEGORIAS_SERVICIO,
    })


@role_required('Administrador')
def crear_servicio(request):
    """Crear nuevo servicio — solo Administrador."""
    form = ServicioForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Servicio creado exitosamente.')
        return redirect('servicios:lista')
    return render(request, 'servicios/servicio_form.html', {'form': form})


@role_required('Administrador')
def editar_servicio(request, pk):
    """Editar servicio existente — solo Administrador."""
    servicio = get_object_or_404(Servicio.all_objects, pk=pk)
    form = ServicioForm(request.POST or None, request.FILES or None, instance=servicio)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Servicio actualizado exitosamente.')
        return redirect('servicios:lista')
    return render(request, 'servicios/servicio_form.html', {'form': form, 'servicio': servicio})


@role_required('Administrador')
def eliminar_servicio(request, pk):
    """Soft-delete service (set esta_activo=False) — solo Administrador."""
    servicio = get_object_or_404(Servicio.all_objects, pk=pk)
    if request.method == 'POST':
        servicio.esta_activo = False
        servicio.save()
        messages.success(request, f'Servicio "{servicio.nombre}" desactivado exitosamente.')
        return redirect('servicios:lista')
    return render(request, 'servicios/servicio_confirm_delete.html', {'servicio': servicio})