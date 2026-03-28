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
- MySQL accesible en `127.0.0.1:3306`
- Base de datos `mds` creada
- Credenciales validas para MySQL

## Variables de entorno

Crear `.env` a partir de `.env.example`.

Variables requeridas:

- `DJANGO_SERVER_KEY`: secret key usada para firmar JWT
- `DB_USER`: usuario de MySQL
- `DB_PASSWORD`: password de MySQL

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

## Consideraciones para entorno local

La configuracion actual viene orientada a un despliegue productivo heredado:

- `DEBUG` esta fijo en `False`
- `ALLOWED_HOSTS` solo incluye `jakarupora.telco.com.ar` y `179.0.181.50`
- `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` estan en `True`

Por lo tanto, un arranque local completo por HTTP plano puede requerir ajustes temporales en configuracion para desarrollo. Este bootstrap no cambia ese comportamiento; solo lo documenta.

## Base de datos

La configuracion activa usa MySQL, no SQLite, aun cuando exista un `db.sqlite3` local en el directorio.

Configuracion hardcodeada en `MDS/settings.py`:

- engine: `django.db.backends.mysql`
- database: `mds`
- host: `127.0.0.1`
- port: `3306`

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
- La cobertura de tests no esta implementada en forma significativa.
- Hay dependencias operativas externas no versionadas en este repo: base MySQL, datos reales y archivos media.
- Existen decisiones tecnicas heredadas que conviene revisar antes de evolucionar funcionalmente el sistema.

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
- artefactos bajo `static/`
