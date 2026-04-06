import hashlib
import json
from django.test import TestCase
from core.models import Departamento, Dispositivo, Municipio, Provincia, User
from .models import Relevamiento


class DeviceAuthCompatibilityTests(TestCase):

    def setUp(self):
        provincia = Provincia.objects.create(descripcion="Misiones")
        departamento = Departamento.objects.create(
            provincia=provincia,
            descripcion="Capital",
        )
        self.municipio = Municipio.objects.create(
            departamento=departamento,
            descripcion="Posadas",
        )
        self.user = User.objects.create_user(
            username=12345678,
            password="secreto",
            municipio=self.municipio,
        )

    def auth_payload(self, device_id: str, modelo: str = "Moto G") -> str:
        return json.dumps(
            {
                "username": 12345678,
                "password": "secreto",
                "id_dispositivo": device_id,
                "modelo": modelo,
            }
        )

    def relevamiento_payload(self, dni: int = 30111222) -> str:
        return json.dumps(
            [
                {
                    "dni": dni,
                    "apellido": "Gomez",
                    "nombre": "Ana",
                    "direccion": "Calle 123",
                    "localidad": self.municipio.id,
                    "telefono": 3764123456,
                    "email": "ana@example.com",
                    "fecha_nacimiento": "1990-05-17",
                    "kit": 1,
                    "observaciones": "Carga de prueba",
                    "latitud": "-27.3621371234567890",
                    "longitud": "-55.9008741234567890",
                    "puntaje": 10,
                }
            ]
        )

    def test_auth_creates_canonical_device_for_new_login(self):
        raw_device_id = "android-device-001"
        response = self.client.post(
            "/jakaru_pora/api/v1/auth",
            data=self.auth_payload(raw_device_id),
            content_type="application/json",
        )

        expected_uuid = hashlib.sha256(raw_device_id.encode()).hexdigest()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["device"], expected_uuid)
        self.assertTrue(
            Dispositivo.objects.filter(user=self.user, uuid=expected_uuid).exists()
        )

    def test_auth_updates_legacy_raw_device_and_model(self):
        raw_device_id = "legacy-device-001"
        Dispositivo.objects.bulk_create(
            [
                Dispositivo(
                    user=self.user,
                    uuid=raw_device_id,
                    modelo="Moto G viejo",
                )
            ]
        )

        response = self.client.post(
            "/jakaru_pora/api/v1/auth",
            data=self.auth_payload(raw_device_id, modelo="Moto G nuevo"),
            content_type="application/json",
        )

        expected_uuid = hashlib.sha256(raw_device_id.encode()).hexdigest()
        legacy_device = Dispositivo.objects.get(user=self.user)
        legacy_device.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["device"], expected_uuid)
        self.assertEqual(legacy_device.uuid, expected_uuid)
        self.assertEqual(legacy_device.modelo, "Moto G nuevo")
        self.assertEqual(Dispositivo.objects.filter(user=self.user).count(), 1)

    def test_auth_reuses_existing_canonical_device(self):
        raw_device_id = "stable-device-001"
        canonical_uuid = hashlib.sha256(raw_device_id.encode()).hexdigest()
        Dispositivo.objects.create(
            user=self.user,
            uuid=canonical_uuid,
            modelo="Moto G inicial",
        )

        response = self.client.post(
            "/jakaru_pora/api/v1/auth",
            data=self.auth_payload(raw_device_id, modelo="Moto G actualizada"),
            content_type="application/json",
        )

        device = Dispositivo.objects.get(user=self.user, uuid=canonical_uuid)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["device"], canonical_uuid)
        self.assertEqual(device.modelo, "Moto G actualizada")
        self.assertEqual(Dispositivo.objects.filter(user=self.user).count(), 1)

    def test_relevamiento_post_accepts_device_returned_by_auth(self):
        raw_device_id = "sync-device-001"
        auth_response = self.client.post(
            "/jakaru_pora/api/v1/auth",
            data=self.auth_payload(raw_device_id),
            content_type="application/json",
        )

        response = self.client.post(
            "/jakaru_pora/api/v1/relevamientos",
            data=self.relevamiento_payload(),
            content_type="application/json",
            HTTP_X_DEVICE_ID=auth_response.json()["device"],
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["data"], [30111222])
        self.assertEqual(Relevamiento.objects.count(), 1)
        self.assertEqual(Relevamiento.objects.get().user, self.user)

    def test_relevamiento_post_accepts_legacy_raw_device_header_during_transition(self):
        raw_device_id = "sync-device-legacy"
        self.client.post(
            "/jakaru_pora/api/v1/auth",
            data=self.auth_payload(raw_device_id),
            content_type="application/json",
        )

        response = self.client.post(
            "/jakaru_pora/api/v1/relevamientos",
            data=self.relevamiento_payload(dni=30999888),
            content_type="application/json",
            HTTP_X_DEVICE_ID=raw_device_id,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["data"], [30999888])
        self.assertEqual(Relevamiento.objects.count(), 1)
