"""
Dependencia compartida para identificar "qué usuario está pidiendo esto".

El usuario sale del token que la app recibió al registrarse o iniciar sesión
(`Authorization: Bearer <token>`, ver backend/services/tokens.py). Así cada
usuario solo ve y modifica sus propios datos: el servidor no confía en ningún
id enviado por el cliente.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Usuario
from backend.services.tokens import leer_token

_esquema = HTTPBearer(auto_error=False)

def _no_autorizado() -> HTTPException:
    # Una instancia nueva por petición: reutilizar una sola acumularía el traceback de cada
    # rechazo (y lo que sus frames retienen) y compartiría estado entre hilos.
    return HTTPException(
        status_code=401,
        detail="Sesión no válida o vencida. Inicia sesión de nuevo.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_esquema),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciales is None:
        raise _no_autorizado()
    usuario_id = leer_token(credenciales.credentials)
    usuario = db.get(Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None:
        raise _no_autorizado()
    if usuario.estado != "ACTIVO":
        raise HTTPException(status_code=403, detail="La cuenta no está activa.")
    return usuario
