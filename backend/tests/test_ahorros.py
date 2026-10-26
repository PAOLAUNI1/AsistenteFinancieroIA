"""Registro, listado y borrado de ahorros (flujo "Otro tipo de ahorro")."""

from datetime import date, timedelta

import pytest

BASICO = {"subtipo": "EFECTIVO", "nombre": "Ahorro para emergencias", "monto_actual": 800_000}
CON_META = {
    **BASICO,
    "descripcion": "Fondo para imprevistos y eventualidades.",
    "es_meta": True,
    "meta_nombre": "Fondo de emergencias",
    "monto_objetivo": 5_000_000,
    "fecha_objetivo": "2099-12-31",
    "metodo": "MANUAL",
}


def _registrar(client, usuario_id, cuerpo):
    return client.post("/ahorros/otro", params={"usuario_id": usuario_id}, json=cuerpo)


def test_un_ahorro_sin_meta_se_registra_con_valores_por_defecto(client, usuario_id):
    respuesta = _registrar(client, usuario_id, BASICO)

    assert respuesta.status_code == 201, respuesta.text
    ahorro = respuesta.json()
    assert ahorro["categoria"] == "OTRO"
    assert ahorro["subtipo"] == "EFECTIVO"
    assert ahorro["nombre"] == "Ahorro para emergencias"
    assert ahorro["monto_actual"] == 800_000
    assert ahorro["moneda"] == "COP"
    assert ahorro["metodo"] == "MANUAL"
    assert ahorro["estado"] == "ACTIVA"
    assert ahorro["es_meta"] is False
    assert ahorro["monto_objetivo"] is None
    assert ahorro["progreso"] is None


def test_un_ahorro_con_meta_calcula_el_progreso(client, usuario_id):
    ahorro = _registrar(client, usuario_id, CON_META).json()

    assert ahorro["es_meta"] is True
    assert ahorro["meta_nombre"] == "Fondo de emergencias"
    assert ahorro["monto_objetivo"] == 5_000_000
    assert ahorro["fecha_objetivo"] == "2099-12-31"
    assert ahorro["progreso"] == 16.0  # 800.000 de 5.000.000, como en el diseño


def test_el_progreso_no_pasa_de_100(client, usuario_id):
    ahorro = _registrar(client, usuario_id, {**CON_META, "monto_actual": 9_000_000}).json()

    assert ahorro["progreso"] == 100.0


def test_si_no_es_meta_se_ignoran_los_datos_de_la_meta(client, usuario_id):
    cuerpo = {**CON_META, "es_meta": False}

    ahorro = _registrar(client, usuario_id, cuerpo).json()

    assert ahorro["es_meta"] is False
    assert ahorro["monto_objetivo"] is None
    assert ahorro["fecha_objetivo"] is None
    assert ahorro["meta_nombre"] is None


@pytest.mark.parametrize("subtipo", ["EFECTIVO", "DOLARES", "PLAN", "PENSION", "VIAJE", "VIVIENDA", "EMERGENCIAS", "PERSONALIZADO"])
def test_se_aceptan_los_ocho_subtipos_del_diseno(client, usuario_id, subtipo):
    assert _registrar(client, usuario_id, {**BASICO, "subtipo": subtipo}).status_code == 201


@pytest.mark.parametrize(
    "cambios,mensaje",
    [
        ({"nombre": "   "}, "Ingresa el nombre del ahorro."),
        ({"es_meta": True}, "Ingresa el monto objetivo de la meta."),
        (
            {"es_meta": True, "monto_objetivo": 1000, "fecha_objetivo": (date.today() - timedelta(days=2)).isoformat()},
            "La fecha objetivo no puede ser anterior a hoy.",
        ),
    ],
)
def test_las_reglas_de_negocio_dan_422_con_su_mensaje(client, usuario_id, cambios, mensaje):
    respuesta = _registrar(client, usuario_id, {**BASICO, **cambios})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == mensaje


@pytest.mark.parametrize(
    "cambios",
    [
        {"subtipo": "NO_EXISTE"},
        {"moneda": "XXX"},
        {"metodo": "OTRO"},
        {"monto_actual": -1},
        {"monto_actual": 10**14},
        {"es_meta": True, "monto_objetivo": 0},
        {"nombre": "x" * 101},
        {"descripcion": "x" * 201},
    ],
)
def test_datos_fuera_de_rango_dan_422(client, usuario_id, cambios):
    assert _registrar(client, usuario_id, {**BASICO, **cambios}).status_code == 422


def test_registrar_sin_token_responde_401(client):
    assert client.post("/ahorros/otro", json=BASICO).status_code == 401
    assert client.get("/ahorros").status_code == 401


def test_el_listado_solo_trae_los_ahorros_del_dueno(client, usuario_id):
    propio = _registrar(client, usuario_id, BASICO).json()["id"]
    otro = client.post(
        "/usuarios",
        json={
            "nombre": "Otro", "correo": "otro-ahorro@example.com", "contrasena": "Segura1234",
            "acepta_terminos": True, "acepta_tratamiento_datos": True,
        },
    ).json()["id"]
    _registrar(client, otro, {**BASICO, "nombre": "Ahorro ajeno"})

    propios = client.get("/ahorros", params={"usuario_id": usuario_id}).json()

    assert [a["id"] for a in propios] == [propio]


def test_el_listado_va_del_mas_reciente_al_mas_antiguo(client, usuario_id):
    primero = _registrar(client, usuario_id, {**BASICO, "nombre": "Primero"}).json()["id"]
    segundo = _registrar(client, usuario_id, {**BASICO, "nombre": "Segundo"}).json()["id"]

    ids = [a["id"] for a in client.get("/ahorros", params={"usuario_id": usuario_id}).json()]

    assert ids == [segundo, primero]


def test_se_puede_eliminar_un_ahorro_propio_y_no_uno_ajeno(client, usuario_id):
    id_ahorro = _registrar(client, usuario_id, BASICO).json()["id"]
    otro = client.post(
        "/usuarios",
        json={
            "nombre": "Otro", "correo": "otro-borrar@example.com", "contrasena": "Segura1234",
            "acepta_terminos": True, "acepta_tratamiento_datos": True,
        },
    ).json()["id"]

    ajeno = client.delete(f"/ahorros/{id_ahorro}", params={"usuario_id": otro})
    propio = client.delete(f"/ahorros/{id_ahorro}", params={"usuario_id": usuario_id})
    de_nuevo = client.delete(f"/ahorros/{id_ahorro}", params={"usuario_id": usuario_id})

    assert (ajeno.status_code, propio.status_code, de_nuevo.status_code) == (404, 204, 404)
    assert client.get("/ahorros", params={"usuario_id": usuario_id}).json() == []


# ---------------------------------------------------------------- alcancía

ALCANCIA = {
    "subtipo": "META_PERSONALIZADA",
    "nombre": "Nueva laptop",
    "descripcion": "Ahorro para comprar mi laptop de trabajo y estudio.",
    "monto_objetivo": 3_000_000,
    "moneda": "COP",
    "fecha_objetivo": "2099-06-30",
    "metodo": "MANUAL",
    "aporte_inicial": 200_000,
}


def _alcancia(client, usuario_id, cuerpo):
    return client.post("/ahorros/alcancia", params={"usuario_id": usuario_id}, json=cuerpo)


def test_una_alcancia_se_registra_como_meta_con_su_aporte_inicial(client, usuario_id):
    respuesta = _alcancia(client, usuario_id, ALCANCIA)

    assert respuesta.status_code == 201, respuesta.text
    ahorro = respuesta.json()
    assert ahorro["categoria"] == "ALCANCIA"
    assert ahorro["subtipo"] == "META_PERSONALIZADA"
    assert ahorro["nombre"] == "Nueva laptop"
    assert ahorro["es_meta"] is True
    assert ahorro["monto_objetivo"] == 3_000_000
    assert ahorro["monto_actual"] == 200_000
    assert ahorro["fecha_objetivo"] == "2099-06-30"
    assert ahorro["metodo"] == "MANUAL"
    assert ahorro["estado"] == "ACTIVA"
    assert ahorro["progreso"] == 6.7  # 200.000 de 3.000.000


def test_una_alcancia_sin_aporte_inicial_ni_fecha_arranca_en_cero(client, usuario_id):
    cuerpo = {k: v for k, v in ALCANCIA.items() if k not in ("aporte_inicial", "fecha_objetivo")}

    ahorro = _alcancia(client, usuario_id, cuerpo).json()

    assert ahorro["monto_actual"] == 0
    assert ahorro["fecha_objetivo"] is None
    assert ahorro["progreso"] == 0.0


@pytest.mark.parametrize("subtipo", ["META_PERSONALIZADA", "VACACIONES", "EMERGENCIAS", "EDUCACION", "VIVIENDA", "OTRO"])
def test_se_aceptan_los_seis_propositos_de_alcancia(client, usuario_id, subtipo):
    assert _alcancia(client, usuario_id, {**ALCANCIA, "subtipo": subtipo}).status_code == 201


@pytest.mark.parametrize("metodo", ["MANUAL", "PROGRAMADO", "REDONDEO", "AUTOMATICO"])
def test_la_alcancia_acepta_el_aporte_por_redondeo(client, usuario_id, metodo):
    respuesta = _alcancia(client, usuario_id, {**ALCANCIA, "metodo": metodo})

    assert respuesta.status_code == 201
    assert respuesta.json()["metodo"] == metodo


def test_el_otro_tipo_de_ahorro_no_acepta_el_metodo_redondeo(client, usuario_id):
    assert _registrar(client, usuario_id, {**BASICO, "metodo": "REDONDEO"}).status_code == 422


@pytest.mark.parametrize(
    "cambios,mensaje",
    [
        ({"nombre": "  "}, "Ingresa el nombre de la alcancía."),
        (
            {"fecha_objetivo": (date.today() - timedelta(days=3)).isoformat()},
            "La fecha objetivo no puede ser anterior a hoy.",
        ),
    ],
)
def test_las_reglas_de_la_alcancia_dan_422_con_su_mensaje(client, usuario_id, cambios, mensaje):
    respuesta = _alcancia(client, usuario_id, {**ALCANCIA, **cambios})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == mensaje


@pytest.mark.parametrize(
    "cambios",
    [
        {"subtipo": "VIAJE"},
        {"monto_objetivo": 0},
        {"monto_objetivo": -5},
        {"aporte_inicial": -1},
        {"moneda": "XXX"},
        {"metodo": "OTRO"},
        {"nombre": "x" * 101},
    ],
)
def test_datos_fuera_de_rango_de_la_alcancia_dan_422(client, usuario_id, cambios):
    assert _alcancia(client, usuario_id, {**ALCANCIA, **cambios}).status_code == 422


def test_el_monto_objetivo_es_obligatorio_en_la_alcancia(client, usuario_id):
    cuerpo = {k: v for k, v in ALCANCIA.items() if k != "monto_objetivo"}

    assert _alcancia(client, usuario_id, cuerpo).status_code == 422


def test_registrar_una_alcancia_sin_token_responde_401(client):
    assert client.post("/ahorros/alcancia", json=ALCANCIA).status_code == 401


def test_la_alcancia_aparece_en_el_listado_junto_a_los_otros_ahorros(client, usuario_id):
    _registrar(client, usuario_id, BASICO)
    _alcancia(client, usuario_id, ALCANCIA)

    categorias = [a["categoria"] for a in client.get("/ahorros", params={"usuario_id": usuario_id}).json()]

    assert sorted(categorias) == ["ALCANCIA", "OTRO"]


def test_el_aporte_inicial_puede_superar_el_objetivo_y_el_progreso_queda_en_100(client, usuario_id):
    # Igual que en "Otro tipo de ahorro": ya tienes más de lo que querías ahorrar.
    respuesta = _alcancia(client, usuario_id, {**ALCANCIA, "aporte_inicial": 4_000_000})

    assert respuesta.status_code == 201
    assert respuesta.json()["monto_actual"] == 4_000_000
    assert respuesta.json()["progreso"] == 100.0


# ------------------------------------------------------- ahorro programado

PROGRAMADO = {
    "subtipo": "VIAJES",
    "nombre": "Vacaciones 2027",
    "descripcion": "Ahorro para viaje familiar a Cartagena.",
    "monto_objetivo": 3_000_000,
    "monto_inicial": 200_000,
    "monto_periodo": 300_000,
    "periodicidad": "MENSUAL",
    "fecha_inicio": "2099-01-01",
    "fecha_objetivo": "2099-12-31",
    "metodo": "AUTOMATICO",
}


def _programado(client, usuario_id, cuerpo):
    return client.post("/ahorros/ahorro-programado", params={"usuario_id": usuario_id}, json=cuerpo)


def test_un_ahorro_programado_se_registra_como_meta_con_su_detalle(client, usuario_id):
    respuesta = _programado(client, usuario_id, PROGRAMADO)

    assert respuesta.status_code == 201, respuesta.text
    ahorro = respuesta.json()
    assert ahorro["categoria"] == "PROGRAMADO"
    assert ahorro["subtipo"] == "VIAJES"
    assert ahorro["nombre"] == "Vacaciones 2027"
    assert ahorro["es_meta"] is True
    assert ahorro["monto_objetivo"] == 3_000_000
    assert ahorro["monto_actual"] == 200_000
    assert ahorro["moneda"] == "COP"
    assert ahorro["fecha_objetivo"] == "2099-12-31"
    assert ahorro["metodo"] == "AUTOMATICO"
    assert ahorro["estado"] == "ACTIVA"
    assert ahorro["progreso"] == 6.7
    assert ahorro["monto_periodo"] == 300_000
    assert ahorro["periodicidad"] == "MENSUAL"
    assert ahorro["fecha_inicio"] == "2099-01-01"


def test_el_detalle_programado_vuelve_en_el_listado(client, usuario_id):
    _programado(client, usuario_id, PROGRAMADO)
    _registrar(client, usuario_id, BASICO)

    por_categoria = {
        a["categoria"]: a for a in client.get("/ahorros", params={"usuario_id": usuario_id}).json()
    }

    assert por_categoria["PROGRAMADO"]["monto_periodo"] == 300_000
    assert por_categoria["PROGRAMADO"]["fecha_inicio"] == "2099-01-01"
    # Las demás categorías no traen detalle programado.
    assert por_categoria["OTRO"]["monto_periodo"] is None
    assert por_categoria["OTRO"]["periodicidad"] is None
    assert por_categoria["OTRO"]["fecha_inicio"] is None


def test_el_monto_inicial_es_opcional_y_arranca_en_cero(client, usuario_id):
    cuerpo = {k: v for k, v in PROGRAMADO.items() if k != "monto_inicial"}

    ahorro = _programado(client, usuario_id, cuerpo).json()

    assert ahorro["monto_actual"] == 0
    assert ahorro["progreso"] == 0.0


@pytest.mark.parametrize("subtipo", ["META_PERSONALIZADA", "VIAJES", "ESTUDIOS", "EMERGENCIAS", "OTRO_OBJETIVO"])
def test_se_aceptan_los_cinco_objetivos_del_ahorro_programado(client, usuario_id, subtipo):
    assert _programado(client, usuario_id, {**PROGRAMADO, "subtipo": subtipo}).status_code == 201


@pytest.mark.parametrize("periodicidad", ["SEMANAL", "QUINCENAL", "MENSUAL"])
def test_se_aceptan_las_tres_periodicidades(client, usuario_id, periodicidad):
    respuesta = _programado(client, usuario_id, {**PROGRAMADO, "periodicidad": periodicidad})

    assert respuesta.status_code == 201
    assert respuesta.json()["periodicidad"] == periodicidad


@pytest.mark.parametrize("metodo", ["AUTOMATICO", "RECORDATORIO"])
def test_el_metodo_es_transferencia_automatica_o_recordatorio(client, usuario_id, metodo):
    respuesta = _programado(client, usuario_id, {**PROGRAMADO, "metodo": metodo})

    assert respuesta.status_code == 201
    assert respuesta.json()["metodo"] == metodo


def test_recordatorio_solo_lo_acepta_el_ahorro_programado(client, usuario_id):
    assert _registrar(client, usuario_id, {**BASICO, "metodo": "RECORDATORIO"}).status_code == 422
    assert _alcancia(client, usuario_id, {**ALCANCIA, "metodo": "RECORDATORIO"}).status_code == 422


@pytest.mark.parametrize(
    "cambios,mensaje",
    [
        ({"nombre": "  "}, "Ingresa el nombre de la meta."),
        ({"monto_inicial": 3_000_000}, "El monto inicial debe ser menor que el monto objetivo."),
        (
            {"fecha_inicio": (date.today() - timedelta(days=2)).isoformat()},
            "La fecha de inicio no puede ser anterior a hoy.",
        ),
        (
            {"fecha_inicio": "2099-06-01", "fecha_objetivo": "2099-06-01"},
            "La fecha objetivo debe ser posterior a la fecha de inicio.",
        ),
        (
            {"fecha_inicio": "2099-06-01", "fecha_objetivo": "2099-05-01"},
            "La fecha objetivo debe ser posterior a la fecha de inicio.",
        ),
    ],
)
def test_las_reglas_del_ahorro_programado_dan_422_con_su_mensaje(client, usuario_id, cambios, mensaje):
    respuesta = _programado(client, usuario_id, {**PROGRAMADO, **cambios})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == mensaje


@pytest.mark.parametrize(
    "cambios",
    [
        {"subtipo": "VACACIONES"},
        {"monto_objetivo": 0},
        {"monto_periodo": 0},
        {"monto_periodo": -1},
        {"monto_inicial": -1},
        {"periodicidad": "ANUAL"},
        {"metodo": "MANUAL"},
        {"moneda": "XXX"},
        {"nombre": "x" * 101},
        {"fecha_inicio": "no es fecha"},
    ],
)
def test_datos_fuera_de_rango_del_ahorro_programado_dan_422(client, usuario_id, cambios):
    assert _programado(client, usuario_id, {**PROGRAMADO, **cambios}).status_code == 422


@pytest.mark.parametrize("campo", ["monto_objetivo", "monto_periodo", "fecha_inicio", "fecha_objetivo"])
def test_los_campos_obligatorios_del_ahorro_programado(client, usuario_id, campo):
    cuerpo = {k: v for k, v in PROGRAMADO.items() if k != campo}

    assert _programado(client, usuario_id, cuerpo).status_code == 422


def test_registrar_un_ahorro_programado_sin_token_responde_401(client):
    assert client.post("/ahorros/ahorro-programado", json=PROGRAMADO).status_code == 401


def test_eliminar_un_ahorro_programado_borra_tambien_su_detalle(client, usuario_id):
    from backend.models import AhorroProgramado

    def detalles():
        with client.session_factory() as db:
            return db.query(AhorroProgramado).count()

    id_ahorro = _programado(client, usuario_id, PROGRAMADO).json()["id"]
    assert detalles() == 1

    assert client.delete(f"/ahorros/{id_ahorro}", params={"usuario_id": usuario_id}).status_code == 204

    assert detalles() == 0
