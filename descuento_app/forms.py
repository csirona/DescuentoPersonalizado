from django import forms
from .models import Discount, RutDiscount
from django.core.exceptions import ValidationError

class DiscountValidationForm(forms.Form):
    code = forms.CharField(max_length=50, label="Código de descuento")

class DiscountRegistrationForm(forms.Form):
    code = forms.CharField(max_length=50, label="Código de descuento")
    boleta_number = forms.CharField(max_length=50, label="Número de boleta")



class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['code', 'expiration_date', 'max_uses']

class RutDiscountForm(forms.ModelForm):
    class Meta:
        model = RutDiscount
        fields = ['rut', 'discount']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678'
            }),
            'discount': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        rut = cleaned_data.get('rut')
        # Si se ha proporcionado un RUT, verificamos que no exista un descuento activo para él.
        if rut and RutDiscount.objects.filter(rut=rut, state=True).exists():
            raise ValidationError("Ya existe un descuento activo para este RUT.")
        return cleaned_data
    

class BulkRutDiscountForm(forms.Form):
    discount = forms.ModelChoiceField(
        queryset=Discount.objects.filter(state=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Descuento"
    )
    ruts = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa un RUT por línea (ejemplo: 12345678-9)'
        }),
        label="RUTs"
    )