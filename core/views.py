import jwt
from datetime import datetime, timedelta
from json import loads, JSONDecodeError
from django.views import View
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.http import JsonResponse
from MDS.settings import SECRET_KEY


class LoginView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = loads(request.body)

            user = authenticate(
                request, username=data.get("username"),
                password=data.get("password"))

            if user:
                return JsonResponse({
                    "token": jwt.encode({
                        "user_id" : user.id,
                        "exp": datetime.utcnow() + timedelta(minutes=60),
                        "iat": datetime.utcnow()
                    },
                    SECRET_KEY,
                    algorithm="HS256")})

            return JsonResponse({"error" : "Credenciales invalidas"}, status=401)

        except JSONDecodeError:
            return JsonResponse({"error" : "Solicitud invalida"}, status=400)

class CommonView(View):
    model = None
    vals = None

    def get(self, request, *args, **kwargs):
        qs = self.model.objects.values(*self.vals)

        if kwargs.get("dni"):
            qs = qs.filter(dni=kwargs["dni"])

        return JsonResponse({
            "data" : list(Paginator(qs, 25).get_page(request.GET.get("page")))
            })
