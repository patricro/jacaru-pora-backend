# Documento tecnico de `jacarupora`

## 1. Objetivo

Este documento describe el estado tecnico actual del backend heredado `jacarupora` para facilitar mantenimiento, onboarding y futuras decisiones de refactor.

## 2. Arquitectura general

El proyecto esta construido sobre Django y se organiza en un proyecto principal (`MDS`) y dos apps:

- `core`: autenticacion general, usuario custom, dispositivos, maestros geograficos y beneficiarios
- `jakaru_pora`: relevamientos asociados al dominio del proyecto

### Componentes principales

- `MDS/settings.py`: configuracion global, base de datos, apps instaladas y archivos estaticos/media
- `MDS/urls.py`: enrutamiento principal
- `MDS/decorators.py`: validaciones de acceso por JWT y por dispositivo
- `core/views.py`: login por JWT y endpoints genericos de lectura
- `jakaru_pora/views.py`: autenticacion por dispositivo y CRUD minimo de relevamientos

## 3. Flujo de autenticacion y acceso

### 3.1 Bearer token

Ruta: `POST /api/v1/login`

Entrada:

```json
{
  "username": "12345678",
  "password": "secreto"
}
```

Salida exitosa:

```json
{
  "token": "<jwt>"
}
```

Detalles:

- Usa `django.contrib.auth.authenticate`
- Firma JWT con `DJANGO_SERVER_KEY`
- Emite `user_id`, `iat` y `exp`
- Vigencia actual: 60 minutos

Los endpoints de lectura de `core` y el `GET` de relevamientos usan el decorador `token_required`.

### 3.2 Autenticacion por dispositivo

Ruta: `POST /jakaru_pora/api/v1/auth`

Entrada esperada:

```json
{
  "username": "12345678",
  "password": "secreto",
  "id_dispositivo": "device-native-id",
  "modelo": "Moto G"
}
```

Salida exitosa:

```json
{
  "device": "<uuid_guardado>"
}
```

Detalles:

- Autentica usuario con credenciales Django
- Busca o crea un `Dispositivo`
- El endpoint sigue expuesto con `@csrf_exempt` por tratarse de una API JSON usada por cliente mobile
- El identificador devuelto en `device` se normaliza al formato canónico `sha256(id_dispositivo)`
- El `POST` de relevamientos usa `device_required` y espera el header `X-DEVICE-ID`

## 4. Modelado actual

### 4.1 `core.User`

Extiende `AbstractUser` y redefine:

- `username`: DNI (`PositiveBigIntegerField`)
- `cuil`
- `municipio`

Notas:

- El login sigue usando `username`, pero semanticamente representa DNI.

### 4.2 `core.Dispositivo`

Campos:

- `uuid`
- `modelo`
- `user`
- `activo`

Responsabilidad:

- asociar un dispositivo a un usuario
- validar acceso a carga de relevamientos

### 4.3 Maestros geograficos

Entidades:

- `Pais`
- `Provincia`
- `Departamento`
- `Municipio`

Responsabilidad:

- normalizar ubicaciones usadas por usuarios y beneficiarios

### 4.4 `core.Beneficiario`

Campos principales:

- `dni`
- `apellido`
- `nombre`
- `direccion`
- `localidad`
- `telefono`
- `email`
- `fecha_nacimiento`
- `activo`

### 4.5 `jakaru_pora.Relevamiento`

Campos principales:

- `beneficiario`
- `kit`
- `observaciones`
- `latitud`
- `longitud`
- `puntaje`
- `foto1`
- `foto2`
- `user`

El modelo guarda fotos en `media/jakaru_pora/relevamiento`.

## 5. Endpoints catalogados

## 5.1 Modulo `core`

### `POST /api/v1/login`

- auth: publica
- body: `username`, `password`
- respuesta: JWT

### `GET /api/v1/beneficiarios`

- auth: `Authorization: Bearer <token>`
- comportamiento: lista paginada de 25 elementos por pagina

### `GET /api/v1/beneficiarios/<dni>`

- auth: Bearer token
- comportamiento: filtro por DNI

### `GET /api/v1/municipios`

- auth: Bearer token
- comportamiento: lista paginada

## 5.2 Modulo `jakaru_pora`

### `POST /jakaru_pora/api/v1/auth`

- auth: publica
- body: `username`, `password`, `id_dispositivo`, `modelo`
- respuesta: identificador de dispositivo persistido

### `GET /jakaru_pora/api/v1/relevamientos`

- auth: Bearer token
- comportamiento: lista paginada de 25 elementos

### `GET /jakaru_pora/api/v1/relevamientos/<id>`

- auth: Bearer token
- comportamiento: filtro por ID

### `POST /jakaru_pora/api/v1/relevamientos`

- auth: `X-DEVICE-ID`
- body: lista JSON de objetos
- comportamiento:
  - valida/carga beneficiario con `BeneficiarioForm`
  - crea `Relevamiento`
  - decodifica `foto1` y `foto2` desde base64 si estan presentes
  - devuelve lista de DNIs insertados

## 6. Configuracion y dependencias

### 6.1 Settings relevantes

- `DEBUG` configurable por `DJANGO_DEBUG`
- `ALLOWED_HOSTS` configurable por `DJANGO_ALLOWED_HOSTS`
- `AUTH_USER_MODEL = "core.User"`
- base de datos MySQL por defecto, SQLite opcional para desarrollo local
- `STATICFILES_DIRS = [BASE_DIR / "static"]`
- `MEDIA_ROOT = BASE_DIR / "media"`

### 6.2 Variables de entorno requeridas

- `DJANGO_SERVER_KEY`
- `DJANGO_DB_ENGINE`
- `DJANGO_DB_NAME`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`
- `DB_USER` y `DB_PASSWORD` como compatibilidad heredada

### 6.3 Dependencias reconstruidas

- Django
- PyMySQL
- python-dotenv
- PyJWT
- Pillow

No se encontro lockfile ni manifiesto original del proveedor anterior.

## 7. Comandos operativos

### 7.1 Chequeo de proyecto

```bash
.venv/bin/python manage.py check
```

### 7.2 Migraciones

```bash
.venv/bin/python manage.py migrate
```

### 7.3 Crear usuarios

Ayuda:

```bash
.venv/bin/python manage.py createuser --help
```

Modo masivo:

```bash
.venv/bin/python manage.py createuser --users ruta/al/archivo.csv
```

Formato esperado del CSV:

- DNI
- Email
- Municipio ID
- Nombres
- Apellido

Modo superusuario:

```bash
.venv/bin/python manage.py createuser --superuser DNI PASSWORD EMAIL CUIL MUNICIPIO_ID NOMBRES APELLIDO
```

## 8. Observaciones tecnicas del codigo heredado

- Hay dos mecanismos de acceso distintos: JWT para lectura y `X-DEVICE-ID` para carga de relevamientos.
- `RelevamientoForm.save()` omite silenciosamente registros invalidos; no devuelve detalle de errores por item.
- `db.sqlite3` existe en el directorio, pero el proyecto apunta a MySQL; no debe considerarse fuente de verdad.
- Las suites `core/tests.py` y `jakaru_pora/tests.py` estan practicamente vacias.
- El sistema depende de archivos media y posiblemente datos operativos externos no incluidos en Git.
- La normalizacion del `device` se corrigio para contemplar registros legacy con UUID raw y devolver siempre el valor canonico SHA-256.
- La configuracion ahora admite un perfil local con SQLite y cookies insecure solo por entorno, sin cambiar el default productivo.

## 9. Contenido excluido del versionado inicial

Para el bootstrap del repositorio se excluyen:

- secretos locales (`.env`)
- bases locales (`db.sqlite3`)
- archivos de media
- CSV operativos
- backups comprimidos
- artefactos generados en `static/`

La intencion es que Git contenga codigo fuente, migraciones, documentacion y bootstrap reproducible.
