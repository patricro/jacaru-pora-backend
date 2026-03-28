from base64 import b64decode
from uuid import uuid4
from typing import Optional
from django.core.files.base import ContentFile
from django import forms
from core.forms import BeneficiarioForm
from .models import Relevamiento


class _RelevamientoForm(forms.ModelForm):

    class Meta:
        model = Relevamiento
        fields = [
            "kit", "observaciones",
            "latitud", "longitud",
            "puntaje"]


class RelevamientoForm():

    def __init__(self, user, data: list):
        self.data = data
        self.user = user

    def decodificar(self, base64_file: Optional[str]) -> Optional[ContentFile]:
        if base64_file:
            return ContentFile(b64decode(base64_file), f"{uuid4()}.jpeg")

    def save(self) -> list:
        lst = []

        for obj in self.data:
            beneficiario_form = BeneficiarioForm(data=obj)

            if beneficiario_form.is_valid():
                bnf = beneficiario_form.save(commit=True)
                form = _RelevamientoForm(
                    data=obj,
                    instance=Relevamiento(
                        beneficiario=bnf,
                        user=self.user, 
                        foto1=self.decodificar(obj.get("foto1")),
                        foto2=self.decodificar(obj.get("foto2")),
                    )
                )
                if form.is_valid():
                    form.save(commit=True)
                    lst.append(obj["dni"])

        return lst
