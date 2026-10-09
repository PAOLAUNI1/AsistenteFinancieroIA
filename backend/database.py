import os
import ssl
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / "bd.env")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "asistente_financiero")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def _url_desde_entorno() -> str:
    """
    En un servidor en la nube la base suele llegar como una sola URL (DATABASE_URL, p. ej.
    `mysql://usuario:clave@host:3306/base`). Si no existe, se arma con las variables DB_* de
    bd.env, como en desarrollo local.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        return (
            f"mysql+pymysql://{quote(DB_USER, safe='')}:{quote(DB_PASSWORD, safe='')}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )
    for prefijo in ("mysql://", "mysql+pymysql://", "mariadb://"):
        if url.startswith(prefijo):
            url = "mysql+pymysql://" + url[len(prefijo):]
            break
    if "charset=" not in url:
        url += ("&" if "?" in url else "?") + "charset=utf8mb4"
    return url


# Parámetros de la URL que el driver (PyMySQL) no entiende como texto y que se traducen a TLS.
_PARAMETROS_SSL_DE_LA_URL = ("ssl-mode", "ssl_mode", "ssl")


def _separar_modo_ssl(url: str) -> tuple[str, str | None]:
    """
    Aiven y otros proveedores entregan la URL con `?ssl-mode=REQUIRED`. PyMySQL no acepta ese
    parámetro (daría TypeError al conectar), así que se quita de la URL y se devuelve aparte:
    (url sin el parámetro, modo en mayúsculas o None).
    """
    objeto = make_url(url)
    modo = None
    for nombre in _PARAMETROS_SSL_DE_LA_URL:
        valor = objeto.query.get(nombre)
        if isinstance(valor, tuple):
            valor = valor[-1]
        if valor is not None:
            modo = str(valor).strip().upper()
    if modo is None:
        return url, None
    objeto = objeto.difference_update_query(_PARAMETROS_SSL_DE_LA_URL)
    return objeto.render_as_string(hide_password=False), modo


def _contexto_tls(modo_de_la_url: str | None = None) -> ssl.SSLContext | None:
    """
    Cifra la conexión con MySQL cuando la base está en otro servidor (p. ej. Aiven). Sin ninguna de
    estas variables ni `ssl-mode` en la URL no se usa TLS, como en desarrollo local:
      DB_SSL_CA_PEM  contenido del certificado de la autoridad (ca.pem) del proveedor
      DB_SSL_CA      ruta a ese archivo
      DB_SSL         true para cifrar validando con las autoridades del sistema
      ssl-mode       parámetro de la URL: DISABLED apaga el cifrado; los demás lo encienden
    Con un certificado propio se valida la cadena (VERIFY_CA, como indica Aiven); con `ssl-mode=REQUIRED`
    y sin certificado se cifra sin validar al servidor, igual que hace el cliente mysql.
    """
    pem = os.getenv("DB_SSL_CA_PEM", "").strip()
    ruta = os.getenv("DB_SSL_CA", "").strip()
    if modo_de_la_url in ("DISABLED", "FALSE", "0"):
        return None
    if pem:
        # Al pegar el certificado en una variable de entorno los saltos de línea pueden llegar como "\n" literal.
        contexto = ssl.create_default_context(cadata=pem.replace("\\n", "\n"))
    elif ruta:
        contexto = ssl.create_default_context(cafile=ruta)
    elif os.getenv("DB_SSL", "").strip().lower() in ("1", "true", "si", "sí") or modo_de_la_url in (
        "VERIFY_CA",
        "VERIFY_IDENTITY",
    ):
        return ssl.create_default_context()
    elif modo_de_la_url is not None:  # REQUIRED, PREFERRED, TRUE...: cifrado sin validar el certificado
        contexto = ssl.create_default_context()
        contexto.check_hostname = False  # Python exige apagarlo antes de poner CERT_NONE
        contexto.verify_mode = ssl.CERT_NONE
    else:
        return None
    contexto.check_hostname = modo_de_la_url == "VERIFY_IDENTITY"
    return contexto


def _argumentos_de_conexion(modo_de_la_url: str | None = None) -> dict:
    contexto = _contexto_tls(modo_de_la_url)
    return {"ssl": contexto} if contexto is not None else {}


DATABASE_URL = _url_desde_entorno()

_URL_DEL_MOTOR, _MODO_SSL_DE_LA_URL = _separar_modo_ssl(DATABASE_URL)
engine = create_engine(
    _URL_DEL_MOTOR, pool_pre_ping=True, connect_args=_argumentos_de_conexion(_MODO_SSL_DE_LA_URL)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
