from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página de inicio
    path('validate_discount/', views.validate_discount, name='validate_discount'),  # Validar descuento
    path('register_discount_usage/', views.register_discount_usage, name='register_discount_usage'),  # Registrar uso de descuento
    path('create_discount/', views.create_discount, name='create_discount'),
    path('descuentos/', views.discount_list, name='discount_list'),
    path('usos/', views.discount_usage_list, name='discount_usage_list'),
    path('crear-rut-descuento/', views.create_rut_discount, name='create_rut_discount'),
    path('ingreso-masivo/', views.bulk_create_rut_discount, name='bulk_create_rut_discount'),

]
