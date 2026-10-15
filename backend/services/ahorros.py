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


def _nombre_requerido(nombre: str, mensaje: str) -> str:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError(mensaje)
    return nombre


def _exigir_fecha_no_pasada(fecha: date | None) -> None:
    if fecha is not None and fecha < hoy_colombia():
        raise ValueError("La fecha objetivo no puede ser anterior a hoy.")


def _columnas(
    *,
    categoria: str,
    subtipo: str,
    nombre: str,
    descripcion: str | None,
    monto_actual: float,
    moneda: str,
    metodo: str,
    es_meta: bool = False,
    meta_nombre: str | None = None,
    monto_objetivo: float | None = None,
    fecha_objetivo: date | None = None,
) -> dict:
    """Las columnas de `ahorros` de cualquier categoría: lo que cambia es solo qué reglas se aplican."""
    return {
        "categoria": categoria,
        "subtipo": subtipo,
        "nombre": nombre,
        "descripcion": (descripcion or "").strip() or None,
        "monto_actual": monto_actual,
        "moneda": moneda,
        "metodo": metodo,
        "estado": "ACTIVA",
        "es_meta": es_meta,
        "meta_nombre": (meta_nombre or "").strip() or None,
        "monto_objetivo": monto_objetivo,
        "fecha_objetivo": fecha_objetivo,
    }


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
    """Columnas de `ahorros` para la categoría OTRO (la meta es opcional)."""
    nombre = _nombre_requerido(nombre, "Ingresa el nombre del ahorro.")
    if monto_actual < 0:
        raise ValueError("El monto actual no puede ser negativo.")

    meta: dict = {}
    if es_meta:
        if monto_objetivo is None or monto_objetivo <= 0:
            raise ValueError("Ingresa el monto objetivo de la meta.")
        _exigir_fecha_no_pasada(fecha_objetivo)
        meta = {
            "es_meta": True,
            "meta_nombre": meta_nombre,
            "monto_objetivo": monto_objetivo,
            "fecha_objetivo": fecha_objetivo,
        }

    return _columnas(
        categoria="OTRO", subtipo=subtipo, nombre=nombre, descripcion=descripcion,
        monto_actual=monto_actual, moneda=moneda, metodo=metodo, **meta,
    )


def validar_ahorro_alcancia(
    *,
    subtipo: str,
    nombre: str,
    descripcion: str | None,
    monto_objetivo: float,
    moneda: str,
    fecha_objetivo: date | None,
    metodo: str,
    aporte_inicial: float,
) -> dict:
    """Columnas de `ahorros` para una alcancía (siempre es una meta; el aporte inicial es el monto actual)."""
    nombre = _nombre_requerido(nombre, "Ingresa el nombre de la alcancía.")
    if monto_objetivo <= 0:
        raise ValueError("Ingresa el monto objetivo de la alcancía.")
    if aporte_inicial < 0:
        raise ValueError("El aporte inicial no puede ser negativo.")
    _exigir_fecha_no_pasada(fecha_objetivo)

    return _columnas(
        categoria="ALCANCIA", subtipo=subtipo, nombre=nombre, descripcion=descripcion,
        monto_actual=aporte_inicial, moneda=moneda, metodo=metodo,
        es_meta=True, monto_objetivo=monto_objetivo, fecha_objetivo=fecha_objetivo,
    )


# Cómo se valida cada categoría; las llaves son las del segmento de la ruta POST /ahorros/<categoria>
# y las mismas que `routers/ahorros.ESQUEMAS_POR_CATEGORIA` (que dice qué cuerpo recibe cada una).
VALIDADORES_POR_CATEGORIA = {
    "otro": validar_ahorro_otro,
    "alcancia": validar_ahorro_alcancia,
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
