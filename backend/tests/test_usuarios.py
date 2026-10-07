from backend.models import Usuario

CONTRASENA = "Segura1234"
ACEPTACIONES = {
    "contrasena": CONTRASENA,
    "acepta_terminos": True,
    "acepta_tratamiento_datos": True,
}


def _registrar(client, correo, nombre="Usuario", **extra):
    return client.post(
        "/usuarios", json={"nombre": nombre, "correo": correo, **ACEPTACIONES, **extra}
    )


def test_registrar_usuario(client):
    respuesta = _registrar(
        client, "juancamilo@example.com", nombre="Juan Camilo Garcia", cantidad_hijos=1
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == "juancamilo@example.com"
    assert cuerpo["estado"] == "ACTIVO"
    assert cuerpo["acepto_terminos_en"] is not None
    assert cuerpo["acepto_tratamiento_datos_en"] is not None


def test_la_respuesta_nunca_incluye_la_contrasena_ni_su_hash(client):
    cuerpo = _registrar(client, "oculta@example.com").json()
    assert "contrasena" not in cuerpo
    assert "contrasena_hash" not in cuerpo


def test_la_contrasena_se_guarda_solo_como_hash(client):
    usuario_id = _registrar(client, "hash@example.com").json()["id"]

    with client.session_factory() as db:
        guardada = db.get(Usuario, usuario_id).contrasena_hash

    assert guardada is not None
    assert guardada != CONTRASENA
    assert guardada.startswith("$2")  # formato bcrypt


def test_registrar_usuario_sin_aceptar_terminos_devuelve_422(client):
    respuesta = _registrar(client, "no-acepto@example.com", acepta_terminos=False)
    assert respuesta.status_code == 422


def test_registrar_usuario_sin_aceptar_tratamiento_datos_devuelve_422(client):
    respuesta = _registrar(client, "no-acepto-2@example.com", acepta_tratamiento_datos=False)
    assert respuesta.status_code == 422


def test_registrar_usuario_sin_indicar_aceptaciones_devuelve_422(client):
    respuesta = client.post(
        "/usuarios",
        json={"nombre": "Malo", "correo": "sin-campos@example.com", "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 422


def test_registrar_usuario_sin_contrasena_devuelve_422(client):
    respuesta = client.post(
        "/usuarios",
        json={
            "nombre": "Sin clave",
            "correo": "sin-clave@example.com",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
        },
    )
    assert respuesta.status_code == 422


def test_registrar_usuario_con_contrasena_corta_devuelve_422(client):
    respuesta = _registrar(client, "corta@example.com", contrasena="corta12")  # 7 caracteres
    assert respuesta.status_code == 422


def test_registrar_usuario_con_contrasena_que_supera_72_bytes_devuelve_422(client):
    respuesta = _registrar(client, "larga@example.com", contrasena="ñ" * 40)  # 80 bytes
    assert respuesta.status_code == 422


def test_registrar_usuario_con_correo_duplicado_devuelve_409(client):
    _registrar(client, "repetido@example.com", nombre="Uno")
    respuesta = _registrar(client, "repetido@example.com", nombre="Otro")
    assert respuesta.status_code == 409


def test_registrar_usuario_con_correo_invalido_devuelve_422(client):
    respuesta = _registrar(client, "no-es-un-correo")
    assert respuesta.status_code == 422


def test_mi_usuario_devuelve_al_dueno_del_token(client):
    creado = _registrar(client, "obtener@example.com").json()

    respuesta = client.get("/usuarios/me", params={"usuario_id": creado["id"]})
    assert respuesta.status_code == 200
    assert respuesta.json()["correo"] == "obtener@example.com"
    assert respuesta.json()["estado"] == "ACTIVO"


def test_perfil_usa_el_usuario_id_indicado_explicitamente(client):
    uno = _registrar(client, "uno@example.com", nombre="Uno").json()
    dos = _registrar(client, "dos@example.com", nombre="Dos").json()

    perfil_uno = client.get("/perfil", params={"usuario_id": uno["id"]}).json()
    perfil_dos = client.get("/perfil", params={"usuario_id": dos["id"]}).json()

    assert perfil_uno["usuario_id"] == uno["id"]
    assert perfil_dos["usuario_id"] == dos["id"]


def test_login_correcto_devuelve_el_usuario(client):
    creado = _registrar(client, "login@example.com", nombre="Diana").json()

    respuesta = client.post(
        "/usuarios/login", json={"correo": "login@example.com", "contrasena": CONTRASENA}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == creado["id"]
    assert respuesta.json()["nombre"] == "Diana"


def test_login_con_contrasena_incorrecta_devuelve_401(client):
    _registrar(client, "mala@example.com")

    respuesta = client.post(
        "/usuarios/login", json={"correo": "mala@example.com", "contrasena": "OtraClave99"}
    )

    assert respuesta.status_code == 401


def test_login_con_correo_inexistente_devuelve_el_mismo_401(client):
    _registrar(client, "existe@example.com")

    inexistente = client.post(
        "/usuarios/login", json={"correo": "nadie@example.com", "contrasena": CONTRASENA}
    )
    incorrecta = client.post(
        "/usuarios/login", json={"correo": "existe@example.com", "contrasena": "OtraClave99"}
    )

    assert inexistente.status_code == 401
    assert inexistente.json() == incorrecta.json()  # no revela si el correo existe


def test_usuario_sin_contrasena_guardada_no_puede_iniciar_sesion(client):
    # Caso real: usuarios creados antes de existir la contraseña tienen contrasena_hash NULL.
    with client.session_factory() as db:
        db.add(Usuario(nombre="Antiguo", correo="antiguo@example.com"))
        db.commit()

    respuesta = client.post(
        "/usuarios/login", json={"correo": "antiguo@example.com", "contrasena": CONTRASENA}
    )

    assert respuesta.status_code == 401


def test_login_de_cuenta_inactiva_devuelve_403(client):
    usuario_id = _registrar(client, "inactiva@example.com").json()["id"]
    with client.session_factory() as db:
        db.get(Usuario, usuario_id).estado = "INACTIVO"
        db.commit()

    respuesta = client.post(
        "/usuarios/login", json={"correo": "inactiva@example.com", "contrasena": CONTRASENA}
    )

    assert respuesta.status_code == 403


def test_login_con_correo_invalido_devuelve_422(client):
    respuesta = client.post(
        "/usuarios/login", json={"correo": "no-es-correo", "contrasena": CONTRASENA}
    )
    assert respuesta.status_code == 422


def test_correo_duplicado_con_la_palabra_aceptar_sigue_siendo_409(client):
    datos = {
        "nombre": "Ana",
        "correo": "aceptar@example.com",
        "contrasena": "Segura1234",
        "acepta_terminos": True,
        "acepta_tratamiento_datos": True,
    }
    assert client.post("/usuarios", json=datos).status_code == 201
    assert client.post("/usuarios", json=datos).status_code == 409


def test_registro_simultaneo_con_el_mismo_correo_da_409(client, monkeypatch):
    from backend.services import perfil

    datos = {
        "nombre": "Ana",
        "correo": "carrera@example.com",
        "contrasena": "Segura1234",
        "acepta_terminos": True,
        "acepta_tratamiento_datos": True,
    }
    assert client.post("/usuarios", json=datos).status_code == 201

    # Simula que la consulta previa no vio al otro registro: solo la restricción única lo detecta.
    class _SinResultados:
        def filter(self, *_):
            return self

        def first(self):
            return None

    monkeypatch.setattr(perfil.Session, "query", lambda self, *_: _SinResultados(), raising=False)
    assert client.post("/usuarios", json=datos).status_code == 409


def _registrar_y_login(client, correo="limite@example.com"):
    client.post(
        "/usuarios",
        json={
            "nombre": "Ana",
            "correo": correo,
            "contrasena": "Segura1234",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
        },
    )


def test_cinco_contrasenas_incorrectas_bloquean_el_login_con_429(client):
    _registrar_y_login(client)
    mala = {"correo": "limite@example.com", "contrasena": "incorrecta1"}
    for _ in range(5):
        assert client.post("/usuarios/login", json=mala).status_code == 401

    bloqueado = client.post("/usuarios/login", json={"correo": "limite@example.com", "contrasena": "Segura1234"})
    assert bloqueado.status_code == 429
    assert int(bloqueado.headers["Retry-After"]) > 0


def test_un_login_correcto_reinicia_la_cuenta_de_fallos(client):
    _registrar_y_login(client)
    mala = {"correo": "limite@example.com", "contrasena": "incorrecta1"}
    buena = {"correo": "limite@example.com", "contrasena": "Segura1234"}
    for _ in range(4):
        client.post("/usuarios/login", json=mala)
    assert client.post("/usuarios/login", json=buena).status_code == 200
    for _ in range(4):
        assert client.post("/usuarios/login", json=mala).status_code == 401
    assert client.post("/usuarios/login", json=buena).status_code == 200


def test_el_bloqueo_de_un_correo_no_afecta_a_otro(client):
    _registrar_y_login(client)
    _registrar_y_login(client, "otro@example.com")
    for _ in range(5):
        client.post("/usuarios/login", json={"correo": "limite@example.com", "contrasena": "incorrecta1"})
    ok = client.post("/usuarios/login", json={"correo": "otro@example.com", "contrasena": "Segura1234"})
    assert ok.status_code == 200
