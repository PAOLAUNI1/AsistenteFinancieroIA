"""Las fechas del backend: UTC para lo guardado, hora de Colombia para "hoy"."""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from backend import tiempo
from backend.services.deudas import proxima_fecha_de_pago


def test_ahora_utc_no_lleva_zona_y_coincide_con_utc():
    ahora = tiempo.ahora_utc()

    assert ahora.tzinfo is None
    assert abs(ahora - datetime.now(timezone.utc).replace(tzinfo=None)) < timedelta(seconds=5)


def test_hoy_colombia_no_depende_de_la_fecha_utc(monkeypatch):
    # 11:30 p. m. del 7 de octubre en Bogotá ya es el 8 en UTC.
    fijo = datetime(2026, 10, 7, 23, 30, tzinfo=ZoneInfo("America/Bogota"))

    class RelojFalso(datetime):
        @classmethod
        def now(cls, tz=None):
            return fijo.astimezone(tz) if tz else fijo

    monkeypatch.setattr(tiempo, "datetime", RelojFalso)

    assert fijo.astimezone(timezone.utc).date() == date(2026, 10, 8)
    assert tiempo.hoy_colombia() == date(2026, 10, 7)


def test_la_proxima_fecha_de_pago_usa_el_dia_de_colombia(monkeypatch):
    monkeypatch.setattr("backend.services.deudas.hoy_colombia", lambda: date(2026, 10, 7))

    assert proxima_fecha_de_pago(7) == date(2026, 10, 7)  # hoy sigue siendo el día de pago
    assert proxima_fecha_de_pago(6) == date(2026, 11, 6)
