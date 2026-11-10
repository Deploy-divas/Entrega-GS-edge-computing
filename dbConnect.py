import os

from pymongo import AsyncMongoClient

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

MONGODB_URI = "mongodb+srv://laueducacao_db_user:<db_password>@fiware.wv8hmwq.mongodb.net/"

@app.on_event("startup")
async def startup_event():
    app.mongodb_client = AsyncMongoClient(MONGODB_URI)

@app.on_event("shutdown")
async def shutdown_event():
    await app.mongodb_client.close()

@app.get("/")
async def root():
    return {"message": "FastAPI + AsyncMongoClient is running. Try GET /ping-db"}

@app.get("/ping-db")
async def ping_db():
    try:
        await app.mongodb_client.admin.command("ping")
        return {"ok": True, "message": "MongoDB is reachable"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})