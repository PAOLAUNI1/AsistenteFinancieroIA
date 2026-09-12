from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Deuda(Base):
    """
    Tabla única para los 7 tipos de deuda (sección 4 de CLAUDE.md).

    Las columnas reflejan la forma común que ya produce cada formulario en
    deudas/*.py; lo específico de cada tipo (cupo/día de corte en tarjeta,
    datos del vehículo, prestamista en préstamo personal, etc.) se guarda en
    `detalle` para no perder diferencias funcionales entre tipos.
    """

    __tablename__ = "deudas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    icono: Mapped[str] = mapped_column(String, nullable=False)
    entidad: Mapped[str] = mapped_column(String, nullable=False)

    monto_inicial: Mapped[float] = mapped_column(Float, nullable=False)
    saldo_actual: Mapped[float] = mapped_column(Float, nullable=False)

    tasa: Mapped[float] = mapped_column(Float, nullable=False)
    periodicidad_tasa: Mapped[str] = mapped_column(String, nullable=False)
    tipo_tasa: Mapped[str] = mapped_column(String, nullable=False)

    anos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    meses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # String porque algunos tipos usan valores no numéricos (ej. "Rotativo",
    # "Pactado", "Acuerdo mutuo") en vez de un número de cuotas.
    total_cuotas: Mapped[str] = mapped_column(String, nullable=False)
    cuota_proxima: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    cuotas_pendientes: Mapped[str] = mapped_column(String, nullable=False)

    valor_cuota: Mapped[float] = mapped_column(Float, nullable=False)
    proximo_pago: Mapped[str] = mapped_column(String, nullable=False)

    detalle: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Perfil(Base):
    """
    Fila única con ingresos y gastos mensuales (sección 4 de CLAUDE.md).
    Sin usuario_id todavía: un solo perfil implícito, igual que hoy en
    Streamlit. Al añadir multiusuario, agregar usuario_id aquí.
    """

    __tablename__ = "perfil"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    salario_mensual: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    otros_ingresos: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    cantidad_hijos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pago_colegio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pago_universidad: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    alimentacion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    transporte: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vestimenta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    entretenimiento: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    arriendo_hipoteca: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    servicios_publicos: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class MetaAhorro(Base):
    """Meta de ahorro anual (sección 36 de CLAUDE.md)."""

    __tablename__ = "metas_ahorro"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    monto_objetivo: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
