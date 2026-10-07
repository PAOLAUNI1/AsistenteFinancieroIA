"""
Tokens de sesión (JWT firmado con HS256). Al registrarse o iniciar sesión la
app recibe un token y lo envía en `Authorization: Bearer <token>`; el backend
deduce de él quién es el usuario, así nadie puede pedir datos ajenos cambiando
un `usuario_id`.

La clave sale de la variable de entorno `JWT_SECRET`. En producción
(`APP_ENV=production`, ya fijada en el Dockerfile) es obligatoria y debe tener
al menos 32 caracteres: si no, el servidor no arranca. Fuera de producción, si
falta, se genera una al azar en cada arranque y las sesiones se pierden al
reiniciar (con varios procesos cada uno tendría una clave distinta).
"""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

logger = logging.getLogger(__name__)

ALGORITMO = "HS256"
LARGO_MINIMO_CLAVE = 32


def _dias_de_vida() -> int:
    try:
        return max(int(os.getenv("JWT_DIAS", "30")), 1)
    except ValueError:
        logger.warning("JWT_DIAS no es un número entero: se usan 30 días.")
        return 30


def _cargar_clave() -> str:
    clave = os.getenv("JWT_SECRET")
    en_produccion = os.getenv("APP_ENV", "").lower() in ("production", "prod")
    if clave and len(clave) >= LARGO_MINIMO_CLAVE:
        return clave
    if en_produccion:
        raise RuntimeError(
            f"JWT_SECRET es obligatoria en producción y debe tener al menos {LARGO_MINIMO_CLAVE} caracteres."
        )
    logger.warning(
        "JWT_SECRET no está definida o es muy corta: se usa una clave temporal y las "
        "sesiones se perderán al reiniciar. Defínela en el servidor."
    )
    return secrets.token_urlsafe(48)


DIAS_DE_VIDA = _dias_de_vida()
_clave = _cargar_clave()


def crear_token(usuario_id: int) -> str:
    ahora = datetime.now(timezone.utc)
    carga = {"sub": str(usuario_id), "iat": ahora, "exp": ahora + timedelta(days=DIAS_DE_VIDA)}
    return jwt.encode(carga, _clave, algorithm=ALGORITMO)


def leer_token(token: str) -> int | None:
    """Devuelve el id del usuario del token, o None si es inválido, está alterado o venció."""
    try:
        carga = jwt.decode(token, _clave, algorithms=[ALGORITMO], options={"require": ["exp", "sub"]})
        return int(carga["sub"])
    except (jwt.PyJWTError, ValueError):
        return None
