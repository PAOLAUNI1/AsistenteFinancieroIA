from backend.services.limite_intentos import LimiteIntentos


def test_consultar_correos_distintos_no_deja_claves_guardadas():
    limite = LimiteIntentos()

    for i in range(1000):
        assert limite.segundos_de_espera(f"nadie{i}@example.com", f"10.0.{i % 250}.1") == 0

    assert limite.claves_guardadas() == 0


def test_los_fallos_vencidos_se_olvidan_y_liberan_la_clave(monkeypatch):
    reloj = [1000.0]
    monkeypatch.setattr("backend.services.limite_intentos.time.monotonic", lambda: reloj[0])
    limite = LimiteIntentos(max_por_correo=2, max_por_ip=10, ventana=60)
    limite.registrar_fallo("a@example.com", "1.1.1.1")
    limite.registrar_fallo("a@example.com", "1.1.1.1")
    assert limite.segundos_de_espera("a@example.com", "1.1.1.1") > 0

    reloj[0] += 61

    assert limite.segundos_de_espera("a@example.com", "1.1.1.1") == 0
    assert limite.claves_guardadas() == 0


def test_bloquea_al_llegar_al_maximo_por_correo_y_el_exito_lo_libera():
    limite = LimiteIntentos(max_por_correo=3, max_por_ip=100)
    for _ in range(3):
        limite.registrar_fallo("A@Example.com", "1.1.1.1")

    assert limite.segundos_de_espera("a@example.com", "2.2.2.2") > 0

    limite.registrar_exito("a@example.com")

    assert limite.segundos_de_espera("a@example.com", "2.2.2.2") == 0


def test_bloquea_por_ip_aunque_cambie_el_correo():
    limite = LimiteIntentos(max_por_correo=100, max_por_ip=3)
    for i in range(3):
        limite.registrar_fallo(f"u{i}@example.com", "9.9.9.9")

    assert limite.segundos_de_espera("otro@example.com", "9.9.9.9") > 0
    assert limite.segundos_de_espera("otro@example.com", "8.8.8.8") == 0
