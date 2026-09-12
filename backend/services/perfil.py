from sqlalchemy.orm import Session

from backend.models import MetaAhorro, Perfil


def obtener_o_crear_perfil(db: Session) -> Perfil:
    perfil = db.get(Perfil, 1)
    if perfil is None:
        perfil = Perfil(id=1)
        db.add(perfil)
        db.commit()
        db.refresh(perfil)
    return perfil


def obtener_o_crear_meta(db: Session) -> MetaAhorro:
    meta = db.get(MetaAhorro, 1)
    if meta is None:
        meta = MetaAhorro(id=1)
        db.add(meta)
        db.commit()
        db.refresh(meta)
    return meta
