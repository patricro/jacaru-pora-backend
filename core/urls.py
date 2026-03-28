from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from MDS.decorators import token_required
from .views import CommonView, LoginView
from .models import Beneficiario, Municipio


urlpatterns = [
    path("api/v1/login", csrf_exempt(LoginView.as_view())),
    path("api/v1/beneficiarios", token_required(CommonView.as_view(
        model=Beneficiario,
        vals=(
            "id", "apellido", "nombre",
            "direccion", "localidad",
            "telefono", "email",
            "fecha_nacimiento", "dni"
        )
    ))),
    path("api/v1/beneficiarios/<int:dni>", token_required(CommonView.as_view(
        model=Beneficiario,
        vals=(
            "id", "apellido", "nombre",
            "direccion", "localidad",
            "telefono", "email",
            "fecha_nacimiento", "dni"
        )
    ))),
    path("api/v1/municipios", token_required(CommonView.as_view(
        model=Municipio,
        vals=("id", "descripcion")
    )))
]
