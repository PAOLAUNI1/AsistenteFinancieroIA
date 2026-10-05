"""
Modelos SQLAlchemy que reflejan el esquema real de la base `asistente_financiero`
(MySQL), creada directamente en la base de datos. No son la fuente de verdad
del esquema: solo lo describen para que el backend pueda leer/escribir. Si el
esquema cambia en la base de datos, estos modelos deben actualizarse a mano.
"""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    contrasena_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cantidad_hijos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    acepto_terminos_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    acepto_tratamiento_datos_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(
        Enum("ACTIVO", "INACTIVO", name="estado_usuario"), nullable=False, default="ACTIVO"
    )
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class TipoDeuda(Base):
    """Catálogo de los 7 tipos de deuda (sección 4 de CLAUDE.md). Ya viene sembrado."""

    __tablename__ = "tipos_deuda"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    icono: Mapped[str | None] = mapped_column(String(10), nullable=True)


class CategoriaGasto(Base):
    """Catálogo de categorías de gasto (sección 4 de CLAUDE.md). Ya viene sembrado."""

    __tablename__ = "categorias_gasto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    grupo: Mapped[str] = mapped_column(
        Enum("HOGAR", "FAMILIA_EDUCACION", "PERSONAL", name="grupo_categoria"),
        nullable=False,
    )


class Deuda(Base):
    __tablename__ = "deudas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tipo_deuda_id: Mapped[int] = mapped_column(ForeignKey("tipos_deuda.id"), nullable=False)

    entidad: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monto_inicial: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    saldo_actual: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    tiene_intereses: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tasa_interes: Mapped[float | None] = mapped_column(Numeric(7, 4), nullable=True)
    periodicidad_tasa: Mapped[str | None] = mapped_column(
        Enum("EA", "MENSUAL", name="periodicidad_tasa"), nullable=True
    )
    tipo_tasa: Mapped[str | None] = mapped_column(
        Enum("FIJA", "VARIABLE", name="tipo_tasa"), nullable=True
    )

    plazo_meses: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    valor_cuota: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    proxima_cuota: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    fecha_proximo_pago: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    descripcion: Mapped[str | None] = mapped_column(String(200), nullable=True)

    estado: Mapped[str] = mapped_column(
        Enum("ACTIVA", "PAGADA", "CANCELADA", name="estado_deuda"),
        nullable=False,
        default="ACTIVA",
    )
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    tipo_deuda: Mapped[TipoDeuda] = relationship(lazy="joined")


class DeudaTarjeta(Base):
    """Detalle 1:1 para deudas de tipo TARJETA (sección 15/18 de CLAUDE.md)."""

    __tablename__ = "deuda_tarjeta"

    deuda_id: Mapped[int] = mapped_column(ForeignKey("deudas.id"), primary_key=True)
    cupo_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    dia_corte: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dia_pago: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    franquicia: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ultimos_digitos: Mapped[str | None] = mapped_column(String(4), nullable=True)


class DeudaVehiculo(Base):
    """Detalle 1:1 para deudas de tipo VEHICULO (sección 19 de CLAUDE.md)."""

    __tablename__ = "deuda_vehiculo"

    deuda_id: Mapped[int] = mapped_column(ForeignKey("deudas.id"), primary_key=True)
    tipo_vehiculo: Mapped[str] = mapped_column(
        Enum("AUTOMOVIL", "MOTOCICLETA", "CAMIONETA", "OTRO", name="tipo_vehiculo"),
        nullable=False,
        default="AUTOMOVIL",
    )
    marca: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    anio: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    placa: Mapped[str | None] = mapped_column(String(10), nullable=True)
    valor_vehiculo: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cuota_inicial: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)


class DeudaEducativo(Base):
    """Detalle 1:1 para deudas de tipo EDUCATIVO (sección 20 de CLAUDE.md)."""

    __tablename__ = "deuda_educativo"

    deuda_id: Mapped[int] = mapped_column(ForeignKey("deudas.id"), primary_key=True)
    institucion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    programa: Mapped[str | None] = mapped_column(String(120), nullable=True)
    modalidad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    beneficiario: Mapped[str | None] = mapped_column(String(100), nullable=True)


class CompraTarjeta(Base):
    """Compra asociada a una tarjeta ya registrada (sección 16 de CLAUDE.md)."""

    __tablename__ = "compras_tarjeta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deuda_id: Mapped[int] = mapped_column(ForeignKey("deuda_tarjeta.deuda_id"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(150), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    fecha_compra: Mapped[date] = mapped_column(Date, nullable=False)
    numero_cuotas: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    cuotas_pagadas: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    genera_intereses: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tasa_interes: Mapped[float | None] = mapped_column(Numeric(7, 4), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PagoDeuda(Base):
    """Historial de pagos/abonos de una deuda (sección 32, paso 11 de CLAUDE.md)."""

    __tablename__ = "pagos_deuda"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deuda_id: Mapped[int] = mapped_column(ForeignKey("deudas.id"), nullable=False)
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    numero_cuota: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    abono_capital: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    intereses: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    saldo_despues: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    observacion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Ingreso(Base):
    __tablename__ = "ingresos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(Enum("SALARIO", "OTRO", name="tipo_ingreso"), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(150), nullable=True)
    monto: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    periodicidad: Mapped[str] = mapped_column(
        Enum("MENSUAL", "UNICO", name="periodicidad_ingreso"), nullable=False, default="MENSUAL"
    )
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Gasto(Base):
    __tablename__ = "gastos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_gasto.id"), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(150), nullable=True)
    monto: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    periodicidad: Mapped[str] = mapped_column(
        Enum("MENSUAL", "UNICO", name="periodicidad_gasto"), nullable=False, default="MENSUAL"
    )
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    categoria: Mapped[CategoriaGasto] = relationship(lazy="joined")


class MetaAhorro(Base):
    __tablename__ = "metas_ahorro"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(
        Enum("FONDO_EMERGENCIA", "META", name="tipo_meta"), nullable=False, default="META"
    )
    monto_objetivo: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    monto_actual: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    fecha_objetivo: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(
        Enum("ACTIVA", "CUMPLIDA", "CANCELADA", name="estado_meta"),
        nullable=False,
        default="ACTIVA",
    )
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AporteMeta(Base):
    __tablename__ = "aportes_meta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meta_id: Mapped[int] = mapped_column(ForeignKey("metas_ahorro.id"), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    observacion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
