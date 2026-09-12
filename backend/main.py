from fastapi import FastAPI

from backend.database import Base, engine
from backend.routers import analisis, deudas, perfil

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Asistente Financiero Inteligente - API",
    description="Backend del prototipo IA_FINANCIERA para ser consumido por la futura app Android.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(deudas.router)
app.include_router(perfil.router)
app.include_router(analisis.router)
