from json import loads, JSONDecodeError
from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate
from MDS.decorators import device_required, token_required
from core.models import Dispositivo
from .models import Relevamiento
try:
    from .forms import RelevamientoForm
except:
    pass


class LoginView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = loads(request.body)

            user = authenticate(
                request, username=data.get("username"),
                password=data.get("password"))

            if user:
                obj = None
                if data.get("id_dispositivo") and data.get("modelo"):
                    raw_device_id = data.get("id_dispositivo")
                    canonical_uuid = Dispositivo.verificar(raw_device_id)

                    obj = user.dispositivo_set.filter(uuid=canonical_uuid).first()
                    if not obj:
                        obj = user.dispositivo_set.filter(uuid=raw_device_id).first()

                    if obj:
                        updated = False
                        if obj.uuid != canonical_uuid:
                            obj.uuid = canonical_uuid
                            updated = True
                        if obj.modelo != data.get("modelo"):
                            obj.modelo = data.get("modelo")
                            updated = True
                        if updated:
                            obj.save()
                    else:
                        obj = user.dispositivo_set.create(
                            uuid=canonical_uuid,
                            modelo=data.get("modelo")
                        )

                    return JsonResponse({"device" : obj.uuid}, status=201)

                return JsonResponse({"msg" : "Solicitud invalida"}, status=400)

            return JsonResponse({"msg" : "Credenciales invalidas"}, status=401)

        except JSONDecodeError:
            return JsonResponse({"error" : "Solicitud invalida"}, status=400)


class RelevamientoView(View):

    @method_decorator(token_required)
    def get(self, request, *args, **kwargs):
        qs = Relevamiento.objects.values(
            "id", "beneficiario", "kit",
            "observaciones", "latitud", "longitud",
            "puntaje", "foto1", "foto2")

        if kwargs.get("id"):
            qs = qs.filter(id=kwargs["id"])
                  
        return JsonResponse({
            "data" : list(Paginator(qs, 25).get_page(request.GET.get("page")))
        })

    @method_decorator(device_required)
    def post(self, request, *args, **kwargs):
        form = RelevamientoForm(request.user, data=loads(request.body))

        return JsonResponse({"data" : form.save()}, status=201)
