import jwt
from django.http import JsonResponse
from core.models import Dispositivo
from MDS.settings import SECRET_KEY


def device_required(view_func):

    def wrapper(request, *args, **kwargs):
        if not request.headers.get("X-DEVICE-ID"):
            return JsonResponse({"error": "No autorizado"}, status=401)

        device_id = request.headers.get("X-DEVICE-ID")

        if not Dispositivo.objects.filter(
            uuid=device_id, activo=True).exists():
            return JsonResponse({"error" : "Dispositivo invalido."}, status=403)

        else:
            request.user = Dispositivo.objects.get(uuid=device_id).user

        return view_func(request, *args, **kwargs)

    return wrapper


def token_required(view_func):

    def wrapper(request, *args, **kwargs):
        if request.headers.get("Authorization"):
            token = request.headers.get("Authorization")
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                request.user_id = payload["user_id"]

            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token expirado"}, status=401)

            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Token invalido"}, status=401)

        else:
            return JsonResponse({"error": "No autorizado"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper
