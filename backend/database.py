import os
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from sqlalchemy import create_engine
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


DATABASE_URL = _url_desde_entorno()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
