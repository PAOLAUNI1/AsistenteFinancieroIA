"""La conexión a la base se arma con DATABASE_URL (nube) o con las variables DB_* (local)."""

from sqlalchemy.engine import make_url

from backend import database


def test_database_url_de_un_proveedor_usa_el_driver_pymysql(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://usuario:clave@host.ejemplo.com:3307/mibase")

    url = make_url(database._url_desde_entorno())

    assert url.drivername == "mysql+pymysql"
    assert (url.username, url.password) == ("usuario", "clave")
    assert (url.host, url.port, url.database) == ("host.ejemplo.com", 3307, "mibase")
    assert url.query["charset"] == "utf8mb4"


def test_database_url_con_parametros_conserva_los_suyos(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://u:p@h:3306/b?ssl=true")

    url = database._url_desde_entorno()

    assert "ssl=true" in url
    assert url.count("charset=utf8mb4") == 1


def test_sin_database_url_se_usan_las_variables_db(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(database, "DB_HOST", "127.0.0.1")
    monkeypatch.setattr(database, "DB_PORT", "3306")
    monkeypatch.setattr(database, "DB_NAME", "asistente")
    monkeypatch.setattr(database, "DB_USER", "root")
    monkeypatch.setattr(database, "DB_PASSWORD", "p@ss word:1")

    url = make_url(database._url_desde_entorno())

    assert url.password == "p@ss word:1"  # los caracteres especiales sobreviven al armado
    assert (url.host, url.database) == ("127.0.0.1", "asistente")


def test_en_produccion_sin_jwt_secret_no_arranca(monkeypatch):
    import pytest

    from backend.services import tokens

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        tokens._cargar_clave()

    monkeypatch.setenv("JWT_SECRET", "corta")
    with pytest.raises(RuntimeError):
        tokens._cargar_clave()

    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    assert tokens._cargar_clave() == "x" * 32


def test_fuera_de_produccion_sin_jwt_secret_usa_clave_temporal(monkeypatch):
    from backend.services import tokens

    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    assert len(tokens._cargar_clave()) >= tokens.LARGO_MINIMO_CLAVE


def test_jwt_dias_con_basura_usa_30(monkeypatch):
    from backend.services import tokens

    monkeypatch.setenv("JWT_DIAS", "abc")
    assert tokens._dias_de_vida() == 30


def _certificado_de_prueba() -> str:
    """Un certificado autofirmado cualquiera, para comprobar que se carga como autoridad."""
    from datetime import datetime, timedelta, timezone

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import NameOID

    clave = ec.generate_private_key(ec.SECP256R1())
    nombre = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA de prueba")])
    ahora = datetime.now(timezone.utc)
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nombre)
        .issuer_name(nombre)
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora - timedelta(days=1))
        .not_valid_after(ahora + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(clave, hashes.SHA256())
    )
    return certificado.public_bytes(serialization.Encoding.PEM).decode()


def _sin_variables_tls(monkeypatch):
    for variable in ("DB_SSL_CA_PEM", "DB_SSL_CA", "DB_SSL"):
        monkeypatch.delenv(variable, raising=False)


def test_sin_variables_tls_la_conexion_no_se_cifra(monkeypatch):
    _sin_variables_tls(monkeypatch)

    assert database._argumentos_de_conexion() == {}


def test_con_el_certificado_en_una_variable_se_valida_la_cadena(monkeypatch):
    import ssl

    _sin_variables_tls(monkeypatch)
    monkeypatch.setenv("DB_SSL_CA_PEM", _certificado_de_prueba())

    contexto = database._argumentos_de_conexion()["ssl"]

    assert contexto.verify_mode == ssl.CERT_REQUIRED
    assert contexto.check_hostname is False  # VERIFY_CA: Aiven documenta validar solo la cadena


def test_el_certificado_con_saltos_de_linea_literales_tambien_se_acepta(monkeypatch):
    _sin_variables_tls(monkeypatch)
    monkeypatch.setenv("DB_SSL_CA_PEM", _certificado_de_prueba().strip().replace("\n", "\n"))

    assert "ssl" in database._argumentos_de_conexion()


def test_con_la_ruta_del_certificado_se_valida_la_cadena(monkeypatch, tmp_path):
    import ssl

    _sin_variables_tls(monkeypatch)
    ruta = tmp_path / "ca.pem"
    ruta.write_text(_certificado_de_prueba())
    monkeypatch.setenv("DB_SSL_CA", str(ruta))

    assert database._argumentos_de_conexion()["ssl"].verify_mode == ssl.CERT_REQUIRED


def test_db_ssl_true_cifra_validando_tambien_el_nombre(monkeypatch):
    _sin_variables_tls(monkeypatch)
    monkeypatch.setenv("DB_SSL", "true")

    assert database._argumentos_de_conexion()["ssl"].check_hostname is True
