from django.db import models
from django.utils import timezone

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    expiration_date = models.DateField()
    state = models.BooleanField(default=True)  # Activo por defecto
    max_uses = models.IntegerField(default=1)  # Número máximo de usos permitidos

    def is_valid(self):
        """ Verifica si el descuento sigue siendo válido """
        return (
            self.state 
            and self.expiration_date >= timezone.now().date()
        )



    def __str__(self):
        return f"{self.code} - Max usos {self.max_uses}"


class RutDiscount(models.Model):
    rut = models.CharField(max_length=12)  # Ejemplo: "12345678-9"
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    used_count = models.IntegerField(default=0)  # Número de usos por RUT
    state = models.BooleanField(default=True)

    class Meta:
        unique_together = ('rut', 'discount')  # Evita que un RUT tenga el mismo descuento repetido

    def can_use_discount(self):
        """ Verifica si el RUT aún puede usar este descuento """
        return self.used_count < self.discount.max_uses and self.state==True and self.discount.is_valid()

    def __str__(self):
        return f"{self.rut} - {self.discount.code} ({self.used_count}/{self.discount.max_uses})"




class DiscountUsage(models.Model):
    rut_discount = models.ForeignKey(RutDiscount, on_delete=models.CASCADE)
    boleta_number = models.CharField(max_length=50)
    used_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """ Verifica si el RUT puede usar el descuento antes de guardarlo """
        if not self.rut_discount.can_use_discount():
            raise ValueError("Este descuento ya no es válido para este RUT.")

        super().save(*args, **kwargs)
        self.rut_discount.used_count += 1  # Incrementa el contador de usos por RUT
        self.rut_discount.save()

    def __str__(self):
        return f"{self.rut_discount.rut} - {self.rut_discount.discount.code} (Boleta {self.boleta_number})"

    
