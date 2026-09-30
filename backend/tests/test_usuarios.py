ACEPTACIONES = {"acepta_terminos": True, "acepta_tratamiento_datos": True}


def test_registrar_usuario(client):
    respuesta = client.post(
        "/usuarios",
        json={
            "nombre": "Juan Camilo Garcia",
            "correo": "juancamilo@example.com",
            "cantidad_hijos": 1,
            **ACEPTACIONES,
        },
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == "juancamilo@example.com"
    assert cuerpo["estado"] == "ACTIVO"
    assert cuerpo["acepto_terminos_en"] is not None
    assert cuerpo["acepto_tratamiento_datos_en"] is not None


def test_registrar_usuario_sin_aceptar_terminos_devuelve_422(client):
    respuesta = client.post(
        "/usuarios",
        json={
            "nombre": "Malo",
            "correo": "no-acepto@example.com",
            "acepta_terminos": False,
            "acepta_tratamiento_datos": True,
        },
    )
    assert respuesta.status_code == 422


def test_registrar_usuario_sin_aceptar_tratamiento_datos_devuelve_422(client):
    respuesta = client.post(
        "/usuarios",
        json={
            "nombre": "Malo",
            "correo": "no-acepto-2@example.com",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": False,
        },
    )
    assert respuesta.status_code == 422


def test_registrar_usuario_sin_indicar_aceptaciones_devuelve_422(client):
    respuesta = client.post(
        "/usuarios", json={"nombre": "Malo", "correo": "sin-campos@example.com"}
    )
    assert respuesta.status_code == 422


def test_registrar_usuario_con_correo_duplicado_devuelve_409(client):
    client.post(
        "/usuarios",
        json={"nombre": "Uno", "correo": "repetido@example.com", **ACEPTACIONES},
    )
    respuesta = client.post(
        "/usuarios",
        json={"nombre": "Otro", "correo": "repetido@example.com", **ACEPTACIONES},
    )
    assert respuesta.status_code == 409


def test_registrar_usuario_con_correo_invalido_devuelve_422(client):
    respuesta = client.post(
        "/usuarios",
        json={"nombre": "Malo", "correo": "no-es-un-correo", **ACEPTACIONES},
    )
    assert respuesta.status_code == 422


def test_obtener_usuario_por_id(client):
    creado = client.post(
        "/usuarios",
        json={"nombre": "Uno", "correo": "obtener@example.com", **ACEPTACIONES},
    ).json()

    respuesta = client.get(f"/usuarios/{creado['id']}")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ACTIVO"


def test_obtener_usuario_inexistente_devuelve_404(client):
    respuesta = client.get("/usuarios/999999")
    assert respuesta.status_code == 404


def test_perfil_usa_el_usuario_id_indicado_explicitamente(client):
    uno = client.post(
        "/usuarios", json={"nombre": "Uno", "correo": "uno@example.com", **ACEPTACIONES}
    ).json()
    dos = client.post(
        "/usuarios", json={"nombre": "Dos", "correo": "dos@example.com", **ACEPTACIONES}
    ).json()

    perfil_uno = client.get("/perfil", params={"usuario_id": uno["id"]}).json()
    perfil_dos = client.get("/perfil", params={"usuario_id": dos["id"]}).json()

    assert perfil_uno["usuario_id"] == uno["id"]
    assert perfil_dos["usuario_id"] == dos["id"]
