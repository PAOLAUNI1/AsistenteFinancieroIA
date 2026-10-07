"""
Tokens de sesión (JWT firmado con HS256). Al registrarse o iniciar sesión la
app recibe un token y lo envía en `Authorization: Bearer <token>`; el backend
deduce de él quién es el usuario, así nadie puede pedir datos ajenos cambiando
un `usuario_id`.

La clave sale de la variable de entorno `JWT_SECRET`. En un servidor público
DEBE definirse (cualquier texto largo y aleatorio): si falta, se genera una al
azar en cada arranque y todas las sesiones se invalidan cuando el servidor se
reinicia.
"""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

logger = logging.getLogger(__name__)

ALGORITMO = "HS256"
DIAS_DE_VIDA = int(os.getenv("JWT_DIAS", "30"))

_clave = os.getenv("JWT_SECRET")
if not _clave:
    _clave = secrets.token_urlsafe(48)
    logger.warning(
        "JWT_SECRET no está definida: se usa una clave temporal y las sesiones "
        "se perderán al reiniciar. Defínela en el servidor."
    )


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
