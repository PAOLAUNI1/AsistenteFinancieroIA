"""Autenticación por token: sin token no hay datos, y un token solo da acceso a su dueño."""

from datetime import datetime, timedelta, timezone

import jwt

from backend.models import Usuario
from backend.services import tokens

CONTRASENA = "Segura1234"


def _registrar(client, correo):
    return client.post(
        "/usuarios",
        json={
            "nombre": "Usuario",
            "correo": correo,
            "contrasena": CONTRASENA,
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
        },
    ).json()


def _con(token):
    return {"Authorization": f"Bearer {token}"}


def test_registrar_devuelve_un_token_que_sirve(client):
    sesion = _registrar(client, "a@example.com")

    assert sesion["token"]
    assert sesion["token_type"] == "bearer"
    respuesta = client.get("/deudas", headers=_con(sesion["token"]))
    assert respuesta.status_code == 200


def test_login_devuelve_un_token_que_sirve(client):
    registrado = _registrar(client, "b@example.com")

    respuesta = client.post(
        "/usuarios/login", json={"correo": "b@example.com", "contrasena": CONTRASENA}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == registrado["id"]
    assert client.get("/usuarios/me", headers=_con(respuesta.json()["token"])).status_code == 200


def test_el_login_fallido_no_entrega_token(client):
    _registrar(client, "c@example.com")

    respuesta = client.post(
        "/usuarios/login", json={"correo": "c@example.com", "contrasena": "OtraClave99"}
    )

    assert respuesta.status_code == 401
    assert "token" not in respuesta.json()


def test_sin_token_los_endpoints_de_datos_responden_401(client):
    for metodo, ruta in [
        ("get", "/deudas"),
        ("get", "/perfil"),
        ("get", "/meta-ahorro"),
        ("get", "/usuarios/me"),
    ]:
        respuesta = getattr(client, metodo)(ruta)
        assert respuesta.status_code == 401, ruta
        assert respuesta.headers["www-authenticate"] == "Bearer"

    assert client.post("/analisis", json={}).status_code == 401
    assert client.delete("/deudas/1").status_code == 401


def test_pasar_usuario_id_por_la_url_ya_no_da_acceso(client):
    otro = _registrar(client, "d@example.com")

    # Sin el atajo de pruebas: un `usuario_id` suelto en la URL no identifica a nadie.
    respuesta = client.get(f"/deudas?usuario_id={otro['id']}")

    assert respuesta.status_code == 401


def test_un_token_alterado_se_rechaza(client):
    sesion = _registrar(client, "e@example.com")
    alterado = sesion["token"][:-3] + ("AAA" if not sesion["token"].endswith("AAA") else "BBB")

    assert client.get("/deudas", headers=_con(alterado)).status_code == 401


def test_un_token_firmado_con_otra_clave_se_rechaza(client):
    sesion = _registrar(client, "f@example.com")
    falso = jwt.encode(
        {"sub": str(sesion["id"]), "exp": datetime.now(timezone.utc) + timedelta(days=1)},
        "otra-clave",
        algorithm="HS256",
    )

    assert client.get("/deudas", headers=_con(falso)).status_code == 401


def test_un_token_vencido_se_rechaza(client):
    sesion = _registrar(client, "g@example.com")
    vencido = jwt.encode(
        {"sub": str(sesion["id"]), "exp": datetime.now(timezone.utc) - timedelta(seconds=5)},
        tokens._clave,
        algorithm="HS256",
    )

    assert client.get("/deudas", headers=_con(vencido)).status_code == 401


def test_un_token_sin_vencimiento_se_rechaza(client):
    sesion = _registrar(client, "h@example.com")
    eterno = jwt.encode({"sub": str(sesion["id"])}, tokens._clave, algorithm="HS256")

    assert client.get("/deudas", headers=_con(eterno)).status_code == 401


def test_un_token_de_un_usuario_que_ya_no_existe_se_rechaza(client):
    assert client.get("/deudas", headers=_con(tokens.crear_token(987654))).status_code == 401


def test_cada_token_solo_ve_los_datos_de_su_dueno(client):
    uno = _registrar(client, "uno@example.com")
    dos = _registrar(client, "dos@example.com")
    client.post(
        "/deudas/prestamo_personal",
        headers=_con(uno["token"]),
        json={
            "prestamista": "Ana",
            "tipo_relacion": "Amigo / Compañero",
            "saldo_actual": 200_000,
            "valor_cuota": 50_000,
            "proximo_pago": "2026-12-01",
        },
    )

    assert len(client.get("/deudas", headers=_con(uno["token"])).json()) == 1
    assert client.get("/deudas", headers=_con(dos["token"])).json() == []


def test_una_cuenta_inactiva_con_token_valido_recibe_403(client):
    sesion = _registrar(client, "i@example.com")
    with client.session_factory() as db:
        db.get(Usuario, sesion["id"]).estado = "INACTIVO"
        db.commit()

    assert client.get("/deudas", headers=_con(sesion["token"])).status_code == 403


def test_ya_no_existe_el_listado_publico_de_usuarios(client):
    sesion = _registrar(client, "j@example.com")

    # Ni con token se pueden listar los demás usuarios ni consultarlos por id.
    assert client.get("/usuarios", headers=_con(sesion["token"])).status_code in (404, 405)
    assert client.get(f"/usuarios/{sesion['id']}", headers=_con(sesion["token"])).status_code in (404, 422)
