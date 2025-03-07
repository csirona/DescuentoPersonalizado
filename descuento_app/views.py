from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Discount, DiscountUsage, RutDiscount
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .forms import DiscountForm, RutDiscountForm,BulkRutDiscountForm
from django.core.paginator import Paginator
from django.utils import timezone

def home(request):
    return render(request, 'descuento_app/home.html')

def create_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('discount_list')  # Puedes redirigir a la página de inicio o donde prefieras
    else:
        form = DiscountForm()
    return render(request, 'descuento_app/create_discount.html', {'form': form})

@csrf_exempt  # Si decides usarlo, aunque si envías el token CSRF en AJAX, podrías quitarlo.
def validate_discount(request):
    """ Valida si un RUT tiene un descuento válido """
    if request.method == 'POST':
        try:
            # Cargar datos JSON de la solicitud
            data = json.loads(request.body)
            rut = data.get('rut')  # Obtener el RUT del request

            # Verificar si se proporcionó un RUT
            if not rut:
                return JsonResponse({'valid': False, 'message': 'Codigo no proporcionado'}, status=400)

            # Buscar descuentos asociados al RUT
            rut_discount = RutDiscount.objects.filter(
                rut=rut, 
                state=True,
                discount__state=True, 
                discount__expiration_date__gte=timezone.now().date()
            ).first()

            # Si no tiene descuentos válidos, rechazar
            if not rut_discount:
                return JsonResponse({'valid': False, 'message': 'No hay descuentos disponibles para este Codigo'}, status=404)

            # Verificar si el RUT aún puede usar el descuento
            if rut_discount.can_use_discount():
                return JsonResponse({
                    'valid': True,
                    'message': f'Tienes un descuento válido ({rut_discount.discount.code}) hasta {rut_discount.discount.expiration_date}. Usado {rut_discount.used_count} de {rut_discount.discount.max_uses} veces',
                    'code': rut_discount.discount.code,
                    'max_uses': rut_discount.discount.max_uses,
                    'used_count': rut_discount.used_count
                })
            else:
                return JsonResponse({'valid': False, 'message': 'El descuento para este RUT ya ha sido usado completamente'}, status=400)

        except Exception as e:
            return JsonResponse({'valid': False, 'message': f'Error: {str(e)}'}, status=500)
    
    # Si es GET, renderiza el template
    return render(request, 'descuento_app/validate_discount.html')



# Función para obtener la IP del cliente
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def register_discount_usage(request):
    """Registra el uso de un código de descuento con su boleta."""
    if request.method == 'POST':
        rut_discount_id = request.POST.get('rut_discount_id')
        boleta_number = request.POST.get('boleta_number')
        # Capturar la IP del cliente
        ip_address = get_client_ip(request)

        if not rut_discount_id or not boleta_number:
            return render(request, 'descuento_app/register_discount.html', {'message': "RUT y boleta son requeridos.", 'message_type': 'error'})

        try:
            rut_discount = RutDiscount.objects.get(rut=rut_discount_id, state=True)
        except RutDiscount.DoesNotExist:
            return render(request, 'descuento_app/register_discount.html', {'message': "RUT no encontrado.", 'message_type': 'error'})

        try:
            # Intentar crear el registro de uso de descuento
            DiscountUsage.objects.create(
                rut_discount=rut_discount,
                boleta_number=boleta_number,
                ip_address=ip_address
            )
        except ValueError as e:
            # Si ocurre un error debido a la validación del descuento
            return render(request, 'descuento_app/register_discount.html', {'message': str(e), 'message_type': 'error'})

        if rut_discount:
            # Si el RutDiscount ha alcanzado el número máximo de usos, desactivamos el descuento.
            if rut_discount.used_count >= rut_discount.discount.max_uses:
                rut_discount.state = False
                rut_discount.save()

        # Mensaje de éxito
        message = f"Descuento registrado correctamente. Quedan {rut_discount.discount.max_uses - rut_discount.used_count} usos disponibles."

        return render(request, 'descuento_app/register_discount.html', {'message': message, 'message_type': 'success'})

    return render(request, 'descuento_app/register_discount.html')


def discount_list(request):
    discounts = Discount.objects.all().order_by('-id')
    paginator = Paginator(discounts, 10)  # 10 descuentos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "descuento_app/discounts.html", {"page_obj": page_obj})

def discount_usage_list(request):
    rut = request.GET.get("rut", "").strip()  # Obtener el RUT de la URL
    code = request.GET.get("code", "").strip()  # Obtener el código de descuento de la URL
    usages = DiscountUsage.objects.all()

    if rut:  # Si hay un RUT, filtramos
        usages = usages.filter(rut_discount__rut__icontains=rut)

    if code:  # Si hay un código de descuento, filtramos
        usages = usages.filter(rut_discount__discount__code__icontains=code)

    paginator = Paginator(usages, 10)  # 10 usos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "descuento_app/discount_usages.html", {"page_obj": page_obj, "rut": rut, "code": code})

def create_rut_discount(request):
    if request.method == 'POST':
        form = RutDiscountForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirige a una página de éxito o a la lista de RutDiscounts (puedes cambiar 'home' por otra URL)
            return redirect('discount_list')
    else:
        form = RutDiscountForm()
    return render(request, 'descuento_app/create_rut_discount.html', {'form': form})

def bulk_create_rut_discount(request):
    message = None
    if request.method == 'POST':
        form = BulkRutDiscountForm(request.POST)
        if form.is_valid():
            discount = form.cleaned_data['discount']
            ruts_text = form.cleaned_data['ruts']
            # Separamos los RUTs por línea y eliminamos espacios en blanco
            ruts_list = [rut.strip() for rut in ruts_text.splitlines() if rut.strip()]
            
            created = 0
            duplicates = 0

            for rut in ruts_list:
                # Verificamos si ya existe un registro activo para este RUT y descuento
                if RutDiscount.objects.filter(rut=rut, discount=discount, state=True).exists():
                    duplicates += 1
                else:
                    RutDiscount.objects.create(rut=rut, discount=discount)
                    created += 1

            message = f"Se crearon {created} registros nuevos. {duplicates} registros ya existían o estaban activos."
            # Puedes redirigir o mostrar el mensaje en el template
            # return redirect('alguna_url')  
    else:
        form = BulkRutDiscountForm()

    return render(request, 'descuento_app/bulk_rut_discount.html', {'form': form, 'message': message})