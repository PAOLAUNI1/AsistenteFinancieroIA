"""
Catálogos de referencia (sección 4 de CLAUDE.md): los 7 tipos de deuda y las
categorías de gasto ya sembrados en la base. El frontend los usa para armar
sus listas/selectores (p. ej. "qué tipos de deuda puedo agregar") en vez de
tenerlos hardcodeados.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import CategoriaGasto, TipoDeuda
from backend.schemas.catalogo import CategoriaGastoOut, TipoDeudaOut

router = APIRouter(tags=["catalogos"])


@router.get("/tipos-deuda", response_model=list[TipoDeudaOut])
def listar_tipos_deuda(db: Session = Depends(get_db)):
    return db.query(TipoDeuda).order_by(TipoDeuda.id).all()


@router.get("/categorias-gasto", response_model=list[CategoriaGastoOut])
def listar_categorias_gasto(db: Session = Depends(get_db)):
    return db.query(CategoriaGasto).order_by(CategoriaGasto.id).all()
