# Operacion de VPS y continuidad segura

## Baseline versionado

- `origin/main` representa la foto versionada del backend actualmente desplegado.
- `main` debe mantenerse siempre en estado desplegable.
- `prod/bootstrap-2026-04-02` marca el primer baseline congelado de produccion.
- `stabilization/env-device-hardening` conserva el commit `4305864` y las validaciones asociadas antes de promoverlo a `main`.

## Flujo de ramas recomendado

1. Crear toda tarea nueva desde `main` o desde una rama de estabilizacion validada.
2. Mantener cada cambio en una rama dedicada hasta completar checks y smoke tests.
3. Promover a `main` solo cambios listos para deploy.

## Backup reproducible del VPS

Ejecutar en el servidor antes de cualquier deploy o investigacion riesgosa:

```bash
mkdir -p backups
tar -czf "backups/jacarupora-code-$(date +%F-%H%M%S).tar.gz" \
  --exclude='media' \
  --exclude='static' \
  --exclude='backups' \
  /ruta/al/backend
cp /ruta/al/backend/.env "backups/jacarupora-env-$(date +%F-%H%M%S).env"
mysqldump \
  --single-transaction \
  --routines \
  --triggers \
  --default-character-set=utf8mb4 \
  -u "$DB_USER" \
  -p"$DB_PASSWORD" \
  "$DJANGO_DB_NAME" \
  > "backups/jacarupora-db-$(date +%F-%H%M%S).sql"
python3 -m pip freeze > "backups/jacarupora-pip-freeze-$(date +%F-%H%M%S).txt"
```

## Checklist de deploy y rollback

1. Confirmar el commit exacto a desplegar y asociarlo a un tag o merge en `main`.
2. Ejecutar `python3 manage.py check` con el `.env` real del servidor.
3. Guardar backup de codigo, `.env`, dump MySQL y `pip freeze`.
4. Desplegar el codigo, reinstalar dependencias solo si cambia `requirements.txt` y volver a correr `python3 manage.py check`.
5. Si algo falla, restaurar el tar del codigo, el `.env` y el dump SQL tomados en el paso previo.
