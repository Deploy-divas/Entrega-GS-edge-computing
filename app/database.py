import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    cliente = AsyncMongoClient(
        os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        serverSelectionTimeoutMS=5000,
    )
    try:
        await cliente.admin.command("ping")
        app.state.mongo_client = cliente
        app.state.db = cliente[os.getenv("MONGODB_DATABASE", "cadastrar_leituras")]
        await app.state.db.itens.create_index(
            "tag_id",
            unique=True,
            partialFilterExpression={"tag_id": {"$type": "string"}},
        )
        await app.state.db.leituras.create_index([("leitura_em", -1)])
        yield
    finally:
        await cliente.close()
