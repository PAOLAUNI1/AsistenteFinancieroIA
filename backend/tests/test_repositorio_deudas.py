"""Persistencia de deudas: consultas acotadas y endpoints de registro generados desde un solo registro."""

import logging

import pytest
from sqlalchemy import event

from backend.main import app
from backend.routers.deudas import ESQUEMAS_POR_TIPO
from backend.services.deudas import VALIDADORES_POR_TIPO


def _tarjeta(i):
    return {
        "entidad": f"Banco {i}",
        "cupo_total": 1_000_000,
        "saldo_actual": 100_000,
        "tasa": 2,
        "dia_corte": 10,
        "dia_pago": 20,
    }


def _vehiculo(i):
    return {
        "entidad": f"Entidad {i}",
        "monto_inicial": 40_000_000,
        "saldo_actual": 30_000_000,
        "tasa": 14,
        "anos": 5,
        "valor_cuota": 900_000,
        "proximo_pago": "2026-12-01",
    }


def _hipotecario(i):
    return {
        "entidad": f"Banco {i}",
        "monto_inicial": 90_000_000,
        "saldo_actual": 80_000_000,
        "tasa": 11,
        "anos": 20,
        "valor_cuota": 990_000,
        "proximo_pago": "2026-12-01",
    }


def _contar_consultas(client, accion):
    consultas = []
    with client.session_factory() as db:
        motor = db.get_bind()

    def contar(conexion, cursor, sentencia, *args):
        consultas.append(sentencia)

    event.listen(motor, "before_cursor_execute", contar)
    try:
        accion()
    finally:
        event.remove(motor, "before_cursor_execute", contar)
    return len(consultas)


def test_listar_deudas_no_hace_una_consulta_por_deuda(client, usuario_id):
    params = {"usuario_id": usuario_id}
    for i in range(3):
        assert client.post("/deudas/tarjeta", params=params, json=_tarjeta(i)).status_code == 201
        assert client.post("/deudas/vehiculo", params=params, json=_vehiculo(i)).status_code == 201
        assert client.post("/deudas/hipotecario", params=params, json=_hipotecario(i)).status_code == 201

    consultas = _contar_consultas(client, lambda: client.get("/deudas", params=params))

    # 9 deudas: un número fijo de consultas (usuario, deudas con su tipo y una por tabla de
    # detalle con deudas), sin importar cuántas deudas haya.
    assert consultas <= 6, f"{consultas} consultas para listar 9 deudas"


def test_el_listado_trae_el_detalle_de_cada_deuda(client, usuario_id):
    params = {"usuario_id": usuario_id}
    client.post("/deudas/tarjeta", params=params, json=_tarjeta(1))
    client.post("/deudas/vehiculo", params=params, json=_vehiculo(1))
    client.post("/deudas/hipotecario", params=params, json=_hipotecario(1))

    por_tipo = {d["tipo_codigo"]: d for d in client.get("/deudas", params=params).json()}

    assert por_tipo["TARJETA"]["detalle"]["dia_corte"] == 10
    assert por_tipo["VEHICULO"]["detalle"]["tipo_vehiculo"] == "OTRO"
    assert por_tipo["HIPOTECARIO"]["detalle"] == {}


def test_cada_tipo_tiene_esquema_y_validador():
    assert ESQUEMAS_POR_TIPO.keys() == VALIDADORES_POR_TIPO.keys()
    assert len(ESQUEMAS_POR_TIPO) == 8


def test_la_documentacion_de_la_api_lista_los_ocho_endpoints_de_registro_con_ids_unicos():
    rutas = app.openapi()["paths"]
    operaciones = []
    for tipo in ESQUEMAS_POR_TIPO:
        post = rutas[f"/deudas/{tipo}"]["post"]
        operaciones.append(post["operationId"])
        assert post["requestBody"], tipo

    assert len(set(operaciones)) == 8


def test_una_deuda_rechazada_por_la_base_deja_el_motivo_en_el_log(client, usuario_id, monkeypatch, caplog):
    from sqlalchemy.exc import IntegrityError

    from backend.routers.deudas import ESQUEMAS_POR_TIPO
    from backend.services import repositorio_deudas as repo
    from backend.services.deudas import VALIDADORES_POR_TIPO
    from backend.tests.test_registro_por_tipo import VALIDOS

    codigo, validar = VALIDADORES_POR_TIPO["hipotecario"]
    resultado = validar(**ESQUEMAS_POR_TIPO["hipotecario"](**VALIDOS["hipotecario"]).model_dump())

    with client.session_factory() as db:
        def commit_rechazado():
            raise IntegrityError("INSERT", {}, Exception("chk_deudas_tasa incumplido"))

        monkeypatch.setattr(db, "commit", commit_rechazado)

        with caplog.at_level(logging.WARNING, logger=repo.__name__):
            with pytest.raises(repo.DeudaNoGuardada):
                repo.registrar_deuda(db, usuario_id, codigo, resultado)

    assert "chk_deudas_tasa incumplido" in caplog.text
