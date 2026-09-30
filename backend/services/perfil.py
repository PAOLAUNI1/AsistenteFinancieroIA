"""
Perfil del usuario (sección 4 de CLAUDE.md: ingresos, familia, gastos
mensuales), adaptado al esquema real de `asistente_financiero`: ya no es una
sola fila de "perfil", sino un usuario en `usuarios` con filas en `ingresos`
y `gastos` (una por categoría).

La base impone `monto > 0` en ingresos y gastos (chk_ingresos_monto,
chk_gastos_monto) y `monto_objetivo > 0` en metas_ahorro (chk_metas_objetivo):
un campo en $0 en el formulario no se guarda como fila, simplemente no existe
esa fila (y si existía, se borra al volver a poner el campo en 0).

Todavía no hay autenticación (fue una decisión explícita para esta primera
fase). Mientras tanto, se usa un único usuario "implícito", igual que hoy en
Streamlit con `st.session_state`: si no existe ningún usuario, se crea uno
por defecto la primera vez que se pide el perfil.
"""

from sqlalchemy.orm import Session

from backend.models import CategoriaGasto, Gasto, Ingreso, MetaAhorro, Usuario

CORREO_USUARIO_POR_DEFECTO = "usuario.demo@asistente-financiero.local"

# Categorías de gasto sembradas en la base (sección 4 de CLAUDE.md).
CATEGORIAS_GASTO_PERFIL = {
    "alimentacion": "ALIMENTACION",
    "transporte": "TRANSPORTE",
    "vestimenta": "VESTIMENTA",
    "entretenimiento": "ENTRETENIMIENTO",
    "arriendo_hipoteca": "ARRIENDO",
    "servicios_publicos": "SERVICIOS",
    "pago_colegio": "COLEGIO",
    "pago_universidad": "UNIVERSIDAD",
}


def obtener_o_crear_usuario_actual(db: Session) -> Usuario:
    usuario = db.query(Usuario).order_by(Usuario.id).first()
    if usuario is None:
        usuario = Usuario(nombre="Usuario demo", correo=CORREO_USUARIO_POR_DEFECTO)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario


def _upsert_ingreso(db: Session, usuario_id: int, tipo: str, monto: float) -> None:
    ingreso = (
        db.query(Ingreso)
        .filter(Ingreso.usuario_id == usuario_id, Ingreso.tipo == tipo, Ingreso.activo.is_(True))
        .first()
    )
    if monto <= 0:
        if ingreso is not None:
            db.delete(ingreso)
        return
    if ingreso is None:
        db.add(Ingreso(usuario_id=usuario_id, tipo=tipo, monto=monto, periodicidad="MENSUAL"))
    else:
        ingreso.monto = monto


def _upsert_gasto(db: Session, usuario_id: int, categoria_codigo: str, monto: float) -> None:
    categoria = db.query(CategoriaGasto).filter(CategoriaGasto.codigo == categoria_codigo).one()
    gasto = (
        db.query(Gasto)
        .filter(
            Gasto.usuario_id == usuario_id,
            Gasto.categoria_id == categoria.id,
            Gasto.activo.is_(True),
        )
        .first()
    )
    if monto <= 0:
        if gasto is not None:
            db.delete(gasto)
        return
    if gasto is None:
        db.add(Gasto(usuario_id=usuario_id, categoria_id=categoria.id, monto=monto, periodicidad="MENSUAL"))
    else:
        gasto.monto = monto


def actualizar_perfil(db: Session, usuario: Usuario, datos: dict) -> None:
    usuario.cantidad_hijos = datos["cantidad_hijos"]

    _upsert_ingreso(db, usuario.id, "SALARIO", datos["salario_mensual"])
    _upsert_ingreso(db, usuario.id, "OTRO", datos["otros_ingresos"])

    for campo, codigo in CATEGORIAS_GASTO_PERFIL.items():
        _upsert_gasto(db, usuario.id, codigo, datos[campo])

    db.commit()


def obtener_perfil(db: Session, usuario: Usuario) -> dict:
    ingresos = {i.tipo: float(i.monto) for i in db.query(Ingreso).filter(
        Ingreso.usuario_id == usuario.id, Ingreso.activo.is_(True)
    )}
    gastos = {
        g.categoria.codigo: float(g.monto)
        for g in db.query(Gasto).filter(Gasto.usuario_id == usuario.id, Gasto.activo.is_(True))
    }

    return {
        "salario_mensual": ingresos.get("SALARIO", 0.0),
        "otros_ingresos": ingresos.get("OTRO", 0.0),
        "cantidad_hijos": usuario.cantidad_hijos,
        "pago_colegio": gastos.get("COLEGIO", 0.0),
        "pago_universidad": gastos.get("UNIVERSIDAD", 0.0),
        "alimentacion": gastos.get("ALIMENTACION", 0.0),
        "transporte": gastos.get("TRANSPORTE", 0.0),
        "vestimenta": gastos.get("VESTIMENTA", 0.0),
        "entretenimiento": gastos.get("ENTRETENIMIENTO", 0.0),
        "arriendo_hipoteca": gastos.get("ARRIENDO", 0.0),
        "servicios_publicos": gastos.get("SERVICIOS", 0.0),
    }


def obtener_meta_principal(db: Session, usuario: Usuario) -> MetaAhorro | None:
    return (
        db.query(MetaAhorro)
        .filter(MetaAhorro.usuario_id == usuario.id, MetaAhorro.tipo == "META")
        .order_by(MetaAhorro.id)
        .first()
    )


def establecer_meta_principal(db: Session, usuario: Usuario, monto_objetivo: float) -> MetaAhorro:
    meta = obtener_meta_principal(db, usuario)
    if meta is None:
        meta = MetaAhorro(
            usuario_id=usuario.id,
            nombre="Meta de ahorro anual",
            tipo="META",
            monto_objetivo=monto_objetivo,
        )
        db.add(meta)
    else:
        meta.monto_objetivo = monto_objetivo
    db.commit()
    db.refresh(meta)
    return meta
