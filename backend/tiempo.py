"""
Fechas y horas del backend.

- La base guarda las marcas de tiempo en UTC, sin zona (`ahora_utc`).
- "Hoy" para el usuario es la fecha en Colombia (`hoy_colombia`): el servidor en la nube
  corre en UTC, y a las 7 p. m. de Bogotá ya sería "mañana" allí, lo que correría un día
  la próxima fecha de pago de una tarjeta.
"""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

ZONA_COLOMBIA = ZoneInfo("America/Bogota")


def ahora_utc() -> datetime:
    """Momento actual en UTC como `datetime` sin zona (el formato que ya tiene la base)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hoy_colombia() -> date:
    return datetime.now(ZONA_COLOMBIA).date()
