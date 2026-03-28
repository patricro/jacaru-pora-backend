from django import forms
from .models import Beneficiario


class BeneficiarioForm(forms.ModelForm):

    class Meta:
        model = Beneficiario
        fields = [
            "dni", "apellido", "nombre", "direccion",
            "localidad", "telefono", "email", "fecha_nacimiento"]
