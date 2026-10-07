"""
Persistencia de las deudas: guardar una deuda con su tabla de detalle, listarlas y borrarlas.

Los routers solo traducen HTTP; todo lo que toca la base está aquí.
"""

import logging
from decimal import Decimal

from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from backend.models import (
    DETALLE_POR_TIPO,
    CompraTarjeta,
    Deuda,
    PagoDeuda,
    TipoDeuda,
)
from backend.schemas.deuda import DeudaOut

logger = logging.getLogger(__name__)


class DeudaNoGuardada(Exception):
    """La base rechazó la deuda (dato fuera de rango o regla incumplida) y se deshizo el guardado."""


def _sin_decimal(valor):
    return float(valor) if isinstance(valor, Decimal) else valor


def registrar_deuda(db: Session, usuario_id: int, codigo_tipo: str, resultado: dict) -> Deuda:
    """Guarda la deuda (tabla base y, si el tipo la tiene, su tabla de detalle) en una sola transacción."""
    tipo_deuda = db.query(TipoDeuda).filter(TipoDeuda.codigo == codigo_tipo).one()
    deuda = Deuda(usuario_id=usuario_id, tipo_deuda_id=tipo_deuda.id, **resultado["base"])
    try:
        db.add(deuda)
        db.flush()  # asigna deuda.id sin cerrar la transacción

        if resultado["detalle"] is not None:
            modelo_detalle = DETALLE_POR_TIPO[codigo_tipo]
            db.add(modelo_detalle(deuda_id=deuda.id, **resultado["detalle"]))

        db.commit()
    except (DataError, IntegrityError) as exc:
        db.rollback()
        # El usuario solo ve un 422 genérico; el motivo real queda en el log.
        logger.warning("MySQL rechazó la deuda de tipo %s del usuario %s: %s", codigo_tipo, usuario_id, exc.orig)
        raise DeudaNoGuardada() from exc
    db.refresh(deuda)
    return deuda


def listar_deudas(db: Session, usuario_id: int) -> list[Deuda]:
    return (
        db.query(Deuda)
        .filter(Deuda.usuario_id == usuario_id)
        .order_by(Deuda.fecha_registro.desc())
        .all()
    )


def _detalles_por_deuda(db: Session, deudas: list[Deuda]) -> dict[int, dict]:
    """Datos de la tabla de detalle de cada deuda, con una sola consulta por tabla (no una por deuda)."""
    detalles: dict[int, dict] = {}
    for codigo, modelo_detalle in DETALLE_POR_TIPO.items():
        ids = [d.id for d in deudas if d.tipo_deuda.codigo == codigo]
        if not ids:
            continue
        columnas = [c.name for c in modelo_detalle.__table__.columns if c.name != "deuda_id"]
        for fila in db.query(modelo_detalle).filter(modelo_detalle.deuda_id.in_(ids)):
            detalles[fila.deuda_id] = {c: _sin_decimal(getattr(fila, c)) for c in columnas}
    return detalles


def a_deudas_out(db: Session, deudas: list[Deuda]) -> list[DeudaOut]:
    detalles = _detalles_por_deuda(db, deudas)
    return [DeudaOut.desde_modelo(d, detalles.get(d.id, {})) for d in deudas]


def eliminar_deuda(db: Session, usuario_id: int, deuda_id: int) -> bool:
    """Borra una deuda del usuario con todo lo que cuelga de ella. False si no existe o es de otro usuario."""
    deuda = (
        db.query(Deuda)
        .filter(Deuda.id == deuda_id, Deuda.usuario_id == usuario_id)
        .first()
    )
    if deuda is None:
        return False

    # La base tiene ON DELETE CASCADE para estas tablas hijas, pero se borra
    # explícito aquí para que el mismo código funcione igual en los tests
    # (SQLite en memoria, sin FKs habilitadas).
    db.query(CompraTarjeta).filter(CompraTarjeta.deuda_id == deuda_id).delete()
    db.query(PagoDeuda).filter(PagoDeuda.deuda_id == deuda_id).delete()
    for modelo_detalle in DETALLE_POR_TIPO.values():
        db.query(modelo_detalle).filter(modelo_detalle.deuda_id == deuda_id).delete()

    db.delete(deuda)
    db.commit()
    return True
