from django.db import models
from core.models import Beneficiario, User


class Relevamiento(models.Model):
    KIT_CHOICES = (
        (1, "Huerta familiar inicial"),
        (2, "Huerta familiar ampliada"),
        (3, "Huerta comunitaria"),
        (4, "Huerta familiar productiva"),
        (5, "Huerta productiva escalable")
    )
    beneficiario = models.ForeignKey(
        Beneficiario, on_delete=models.CASCADE)
    kit = models.PositiveSmallIntegerField("Kit", choices=KIT_CHOICES)
    observaciones = models.CharField(
        "Oberservaciones", max_length=5000, null=True, default=None, blank=True)
    latitud = models.DecimalField(
        "Latitud", max_digits=19, decimal_places=16)
    longitud = models.DecimalField(
        "Longitud", max_digits=19, decimal_places=16)
    puntaje = models.PositiveSmallIntegerField("Puntaje", default=0)
    foto1 = models.ImageField(
        "Foto 1", upload_to="jakaru_pora/relevamiento",
        null=True, default=None, blank=True)
    foto2 = models.ImageField(
        "Foto 2", upload_to="jakaru_pora/relevamiento",
        null=True, default=None, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)
