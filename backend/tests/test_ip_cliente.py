"""La IP que cuenta el límite de login: la que añade el proxy propio, nunca la que escribe el cliente."""

from types import SimpleNamespace

from backend.services.ip_cliente import ip_del_cliente


def _peticion(host="10.0.0.9", reenviado=None):
    encabezados = {"x-forwarded-for": reenviado} if reenviado is not None else {}
    return SimpleNamespace(headers=encabezados, client=SimpleNamespace(host=host) if host else None)


def test_sin_proxy_se_usa_la_ip_de_la_conexion_aunque_llegue_el_encabezado(monkeypatch):
    monkeypatch.delenv("PROXY_HOPS", raising=False)

    assert ip_del_cliente(_peticion(reenviado="1.2.3.4")) == "10.0.0.9"


def test_con_un_proxy_se_toma_la_ultima_entrada(monkeypatch):
    monkeypatch.setenv("PROXY_HOPS", "1")

    assert ip_del_cliente(_peticion(reenviado="203.0.113.7")) == "203.0.113.7"


def test_las_entradas_que_escribe_el_cliente_no_cambian_la_ip(monkeypatch):
    monkeypatch.setenv("PROXY_HOPS", "1")
    # El atacante envía su propio X-Forwarded-For; el proxy añade al final la IP real.
    falsificado = "9.9.9.9, 8.8.8.8, 203.0.113.7"

    assert ip_del_cliente(_peticion(reenviado=falsificado)) == "203.0.113.7"


def test_con_dos_proxies_se_toma_la_penultima(monkeypatch):
    monkeypatch.setenv("PROXY_HOPS", "2")

    assert ip_del_cliente(_peticion(reenviado="203.0.113.7, 172.16.0.5")) == "203.0.113.7"


def test_si_faltan_entradas_se_cae_a_la_ip_de_la_conexion(monkeypatch):
    monkeypatch.setenv("PROXY_HOPS", "2")

    assert ip_del_cliente(_peticion(reenviado="203.0.113.7")) == "10.0.0.9"
    assert ip_del_cliente(_peticion()) == "10.0.0.9"


def test_sin_cliente_ni_encabezado_devuelve_desconocida(monkeypatch):
    monkeypatch.setenv("PROXY_HOPS", "1")

    assert ip_del_cliente(_peticion(host=None)) == "desconocida"


def test_un_valor_invalido_de_proxy_hops_se_ignora(monkeypatch):
    monkeypatch.setenv("PROXY_HOPS", "muchos")

    assert ip_del_cliente(_peticion(reenviado="1.2.3.4")) == "10.0.0.9"


def test_el_login_cuenta_los_fallos_por_la_ip_del_proxy_y_no_por_la_del_encabezado_falso(client, monkeypatch):
    from backend.services.limite_intentos import limite_login

    monkeypatch.setenv("PROXY_HOPS", "1")
    for i in range(3):
        client.post(
            "/usuarios/login",
            json={"correo": f"nadie{i}@example.com", "contrasena": "Incorrecta123"},
            headers={"X-Forwarded-For": f"10.10.10.{i}, 203.0.113.7"},
        )

    # Los tres fallos se contaron contra la misma IP real, aunque el cliente cambió su encabezado.
    assert limite_login._fallos[("ip", "203.0.113.7")].__len__() == 3
