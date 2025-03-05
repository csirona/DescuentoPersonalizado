# descuento_app/admin.py
from django.contrib import admin
from .models import Discount, DiscountUsage,RutDiscount

admin.site.register(Discount)
admin.site.register(DiscountUsage)
admin.site.register(RutDiscount)
