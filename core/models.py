import hashlib
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.PositiveBigIntegerField("DNI", unique=True)
    cuil = models.PositiveBigIntegerField(
        "CUIL", unique=True, null=True, default=None, blank=True)
    municipio = models.ForeignKey("Municipio", on_delete=models.CASCADE, default=1)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Dispositivo(models.Model):
    uuid = models.CharField("ID de Dispositivo", max_length=64, unique=True)
    modelo = models.CharField("Modelo", max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Dispositivo {self.user}"

    @classmethod
    def verificar(self, id: str) -> str:
        return hashlib.sha256(id.encode()).hexdigest()

    def save(self, **kwargs):
        if not self.uuid:
            self.uuid = hashlib.sha256(self.uuid.encode()).hexdigest()
        super().save(**kwargs)


class Pais(models.Model): 
    descripcion = models.CharField("Pais", max_length=50)

    class Meta:
        verbose_name_plural = "Países"

    def __str__(self): 
        return self.descripcion

    def save(self, **kwargs):
        self.descripcion = self.descripcion.upper()
        super().save(**kwargs)


class Provincia(models.Model):
    descripcion = models.CharField("Provincia", max_length=30)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ("descripcion",)

    def __str__(self):
        return self.descripcion

    def save(self, **kwargs):
        self.descripcion = self.descripcion.upper()
        super().save(**kwargs)


class Departamento(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.RESTRICT)
    descripcion = models.CharField("Departamento", max_length=30)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name_plural = "Departamentos"
        ordering = ("descripcion",)

    def __str__(self):
        return f"{self.provincia} - {self.descripcion}"

    def save(self, **kwargs):
        self.descripcion = self.descripcion.upper()
        super().save(**kwargs)


class Municipio(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    descripcion = models.CharField("Descripcion", max_length=100)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ("descripcion",)

    def __str__(self):
        return self.descripcion

    @classmethod
    def getOne(cls, id):
        obj = cls.objects.get(id=id)
        return {"id" : obj.id, "descripcion" : obj.descripcion}

    def save(self, **kwargs):
        self.descripcion = self.descripcion.upper()
        super().save(**kwargs)


class Beneficiario(models.Model):
    dni = models.PositiveBigIntegerField("DNI", unique=True, db_index=True)
    apellido = models.CharField("Apellido", max_length=50)
    nombre = models.CharField("Nombre", max_length=50)
    direccion = models.CharField(
        "Direccion", max_length=100, null=True, default=None, blank=True)
    localidad = models.ForeignKey(Municipio, on_delete=models.CASCADE, null=True, default=None, blank=True)
    telefono = models.PositiveBigIntegerField(
        "Teléfono", null=True, default=None, blank=True)
    email = models.EmailField(
        "Email", max_length=50, null=True, default=None, blank=True)
    fecha_nacimiento = models.DateField("Fecha de Nacimiento")
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ("apellido", "nombre",)

    def __str__(self):
        return f"{self.apellido} {self.nombre} - DNI: {self.dni}"

    def save(self, **kwargs):
        self.apellido = self.apellido.upper()
        self.nombre = self.nombre.upper()
        if self.direccion:
            self.direccion = self.direccion.upper()
        super().save(**kwargs)
