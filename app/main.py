from fastapi import FastAPI

from app.database import lifespan
from app.routers import itens, leituras, notificacao

app = FastAPI(
    title="API de áudio descrição",
    description=(
        """Catálogo de itens identificados por tag e histórico de leituras 
        para fornecer áudio descrições."""
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(itens.router)
app.include_router(leituras.router)
app.include_router(notificacao.router)


@app.get("/", tags=["CitizenTech"])
async def root():
    return {"message": "API de acessibilidade", "docs": "/docs"}

