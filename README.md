# jacarupora

Backend Django heredado para autenticacion, consulta de beneficiarios/municipios y carga de relevamientos asociados al modulo `jakaru_pora`.

## Estado del proyecto

Este repositorio se inicializa como onboarding tecnico de un sistema heredado por otra empresa.

- Se documenta el estado actual del codigo sin redisenar la solucion.
- Se versiona codigo fuente, migraciones y documentacion.
- No se versionan secretos, bases locales, archivos de media, CSV operativos ni backups.

## Stack actual

- Python 3.12 recomendado para el entorno local
- Django 5.2.x
- MySQL como base de datos principal
- PyMySQL como adaptador MySQL
- PyJWT para tokens Bearer
- python-dotenv para carga de variables desde `.env`
- Pillow para manejo de imagenes en `ImageField`

## Estructura general

- `MDS/`: configuracion del proyecto Django, settings, URLs y decoradores de autenticacion
- `core/`: usuario custom, dispositivos, ubicaciones, beneficiarios, login y comando `createuser`
- `jakaru_pora/`: relevamientos, autenticacion por dispositivo y carga de fotos/base64
- `docs/`: documentacion tecnica adicional
- `manage.py`: entrypoint de administracion Django

## Requisitos previos

- Python 3.12 o compatible
- `venv` y `pip` disponibles para Python 3
- MySQL accesible en `127.0.0.1:3306` para el modo heredado por defecto
- Opcionalmente, SQLite para desarrollo rapido local
- Base de datos `mds` creada si se usa MySQL
- Credenciales validas para MySQL si se usa MySQL

## Variables de entorno

Crear `.env` a partir de `.env.example`.

Variables requeridas:

- `DJANGO_SERVER_KEY`: secret key usada para firmar JWT
- `DJANGO_DB_ENGINE`: `mysql` por defecto, `sqlite` para desarrollo local
- `DJANGO_DB_NAME`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`

Compatibilidad heredada:

- `DB_USER`
- `DB_PASSWORD`

## Baseline y flujo Git

- `origin/main` es la foto versionada del backend hoy tomado como baseline de produccion.
- `main` debe mantenerse siempre en estado desplegable.
- `prod/bootstrap-2026-04-02` congela el bootstrap inicial de produccion.
- `stabilization/env-device-hardening` concentra la validacion del commit `4305864` antes de promoverlo a `main`.
- Toda nueva tarea debe salir desde `main` o desde una rama de estabilizacion ya validada.

## Puesta en marcha local

1. Crear entorno virtual:

```bash
python3 -m venv .venv
```

2. Instalar dependencias:

```bash
.venv/bin/pip install -r requirements.txt
```

3. Crear `.env` local a partir de `.env.example` y completar credenciales reales.

4. Ejecutar chequeo basico:

```bash
.venv/bin/python manage.py check
```

5. Aplicar migraciones si corresponde al entorno:

```bash
.venv/bin/python manage.py migrate
```

6. Levantar el servidor:

```bash
.venv/bin/python manage.py runserver
```

### Modo local rapido con SQLite

Para desarrollo local sin MySQL:

```bash
DJANGO_SERVER_KEY=dev-secret \
DJANGO_DEBUG=true \
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost \
DJANGO_SESSION_COOKIE_SECURE=false \
DJANGO_CSRF_COOKIE_SECURE=false \
DJANGO_DB_ENGINE=sqlite \
DJANGO_DB_NAME=db.sqlite3 \
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

### Smoke tests minimos

Para validar la configuracion local y el flujo mobile sin depender de MySQL:

```bash
DJANGO_SERVER_KEY=test-secret \
DJANGO_DB_ENGINE=sqlite \
DJANGO_DB_NAME=/tmp/jacarupora-smoke.sqlite3 \
python3 manage.py test
```

## Consideraciones para entorno local

La configuracion heredada sigue orientada a produccion, pero ahora puede sobreescribirse por entorno para desarrollo local. MySQL sigue siendo el default si no se define nada.

## Base de datos

La configuracion activa usa MySQL por defecto, pero ahora admite SQLite para desarrollo local mediante `DJANGO_DB_ENGINE=sqlite`.

## API disponible hoy

### Core

- `POST /api/v1/login`
  - autentica con `username` y `password`
  - devuelve `token` JWT con expiracion de 60 minutos

- `GET /api/v1/beneficiarios`
  - requiere header `Authorization: Bearer <token>`
  - devuelve listado paginado de beneficiarios

- `GET /api/v1/beneficiarios/<dni>`
  - requiere Bearer token
  - filtra por DNI

- `GET /api/v1/municipios`
  - requiere Bearer token
  - devuelve municipios

### jakaru_pora

- `POST /jakaru_pora/api/v1/auth`
  - autentica usuario y registra/valida un dispositivo
  - espera `username`, `password`, `id_dispositivo` y `modelo`
  - devuelve `device` para usar en el header `X-DEVICE-ID`
  - permanece marcado con `@csrf_exempt` por tratarse de una API JSON usada por cliente mobile
  - normaliza `device` al valor canonico basado en SHA-256

- `GET /jakaru_pora/api/v1/relevamientos`
  - requiere Bearer token
  - devuelve relevamientos paginados

- `GET /jakaru_pora/api/v1/relevamientos/<id>`
  - requiere Bearer token
  - filtra por ID

- `POST /jakaru_pora/api/v1/relevamientos`
  - requiere header `X-DEVICE-ID`
  - recibe una lista JSON con datos de beneficiario y relevamiento
  - soporta `foto1` y `foto2` en base64
  - durante la transicion acepta tanto el `device` canonico devuelto por `/auth` como IDs legacy raw ya conocidos por el backend

## Comando de usuarios

El proyecto incluye el comando custom:

```bash
.venv/bin/python manage.py createuser --help
```

Usos principales:

- crear usuarios masivamente desde CSV
- crear superusuario con argumentos explicitos

El comando genera `media/out.csv` con credenciales cuando se usa el modo masivo.

## Riesgos y observaciones del sistema heredado

- No hay lockfile ni manifiesto de dependencias original; `requirements.txt` fue reconstruido a partir del codigo.
- La cobertura sigue siendo minima; hoy se cubren smoke tests de configuracion y compatibilidad del flujo mobile.
- Hay dependencias operativas externas no versionadas en este repo: base MySQL, datos reales y archivos media.
- Existen decisiones tecnicas heredadas que conviene revisar antes de evolucionar funcionalmente el sistema.
- El endpoint mobile de auth sigue usando `@csrf_exempt`.
- La seguridad y operacion heredadas se mantuvieron; solo se agrego configuracion por entorno y una compatibilidad transitoria para `device`.

## Operacion y backup

El procedimiento base de backup, deploy y rollback del VPS quedo documentado en `docs/operacion-vps.md`.

## Contenido versionado en esta inicializacion

Se incluyen:

- codigo Python del proyecto
- migraciones
- documentacion tecnica
- archivos de bootstrap del repositorio

Se excluyen:

- `.env`
- `db.sqlite3`
- `media/`
- `data.csv`
- `jakaru_pora/mds_respaldo.tar.gz`
- `backups/`
- artefactos bajo `static/`
