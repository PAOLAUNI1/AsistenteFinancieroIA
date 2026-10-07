from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.database import Base, engine
from backend.routers import analisis, catalogos, deudas, perfil, usuarios

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Asistente Financiero Inteligente - API",
    description="Backend del prototipo IA_FINANCIERA para ser consumido por la futura app Android.",
    version="0.1.0",
)


@app.exception_handler(RequestValidationError)
async def datos_invalidos(_: Request, exc: RequestValidationError):
    # Sin "input" ni "ctx": el valor recibido no se devuelve (puede ser una contraseña) y
    # valores como Infinity o NaN no se pueden serializar a JSON.
    errores = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errores})


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(usuarios.router)
app.include_router(catalogos.router)
app.include_router(deudas.router)
app.include_router(perfil.router)
app.include_router(analisis.router)
