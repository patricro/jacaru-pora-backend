from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import LoginView, RelevamientoView


urlpatterns = [
    path("api/v1/auth", csrf_exempt(LoginView.as_view())),
    path("api/v1/relevamientos", csrf_exempt(RelevamientoView.as_view())),
    path("api/v1/relevamientos/<int:id>", RelevamientoView.as_view())
]
