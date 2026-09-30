"""
Dependencia compartida para identificar "qué usuario está pidiendo esto".

Todavía no hay login (sección de autenticación pendiente, fuera del alcance
de esta fase): en vez de adivinar un usuario "actual" implícito, cada
request debe indicar explícitamente `usuario_id` (obtenido antes con
POST /usuarios). Esto evita que, con varios usuarios registrados, uno vea
o modifique los datos de otro.
"""

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Usuario


def usuario_actual(
    usuario_id: int = Query(..., description="Id devuelto por POST /usuarios"),
    db: Session = Depends(get_db),
) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"No existe un usuario con id {usuario_id}.")
    return usuario
