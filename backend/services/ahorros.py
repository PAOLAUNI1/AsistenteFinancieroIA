"""
Ahorros del usuario: reglas del registro y persistencia.

Una regla incumplida lanza ValueError con el texto que se muestra en la app.
"""

import logging
from datetime import date

from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from backend.models import Ahorro
from backend.tiempo import hoy_colombia

logger = logging.getLogger(__name__)


class AhorroNoGuardado(Exception):
    """La base rechazó el ahorro (dato fuera de rango o regla incumplida) y se deshizo el guardado."""


def validar_ahorro_otro(
    *,
    subtipo: str,
    nombre: str,
    descripcion: str | None,
    monto_actual: float,
    moneda: str,
    es_meta: bool,
    meta_nombre: str | None,
    monto_objetivo: float | None,
    fecha_objetivo: date | None,
    metodo: str,
) -> dict:
    """Devuelve las columnas de `ahorros` para un ahorro de la categoría OTRO."""
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("Ingresa el nombre del ahorro.")
    if monto_actual < 0:
        raise ValueError("El monto actual no puede ser negativo.")

    meta = {"es_meta": False, "meta_nombre": None, "monto_objetivo": None, "fecha_objetivo": None}
    if es_meta:
        if monto_objetivo is None or monto_objetivo <= 0:
            raise ValueError("Ingresa el monto objetivo de la meta.")
        if fecha_objetivo is not None and fecha_objetivo < hoy_colombia():
            raise ValueError("La fecha objetivo no puede ser anterior a hoy.")
        meta = {
            "es_meta": True,
            "meta_nombre": (meta_nombre or "").strip() or None,
            "monto_objetivo": monto_objetivo,
            "fecha_objetivo": fecha_objetivo,
        }

    return {
        "categoria": "OTRO",
        "subtipo": subtipo,
        "nombre": nombre,
        "descripcion": (descripcion or "").strip() or None,
        "monto_actual": monto_actual,
        "moneda": moneda,
        "metodo": metodo,
        "estado": "ACTIVA",
        **meta,
    }


def registrar_ahorro(db: Session, usuario_id: int, columnas: dict) -> Ahorro:
    ahorro = Ahorro(usuario_id=usuario_id, **columnas)
    try:
        db.add(ahorro)
        db.commit()
    except (DataError, IntegrityError) as exc:
        db.rollback()
        logger.warning("MySQL rechazó el ahorro del usuario %s: %s", usuario_id, exc.orig)
        raise AhorroNoGuardado() from exc
    db.refresh(ahorro)
    return ahorro


def listar_ahorros(db: Session, usuario_id: int) -> list[Ahorro]:
    return (
        db.query(Ahorro)
        .filter(Ahorro.usuario_id == usuario_id)
        .order_by(Ahorro.fecha_registro.desc(), Ahorro.id.desc())
        .all()
    )


def eliminar_ahorro(db: Session, usuario_id: int, ahorro_id: int) -> bool:
    """False si no existe o es de otro usuario."""
    ahorro = (
        db.query(Ahorro).filter(Ahorro.id == ahorro_id, Ahorro.usuario_id == usuario_id).first()
    )
    if ahorro is None:
        return False
    db.delete(ahorro)
    db.commit()
    return True
