from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.schemas import CriarItem, AtualizarItem, CriarLeitura


def serializar_item(item: dict) -> dict:
    item["_id"] = str(item["_id"])
    return item


def serializar_leitura(leitura: dict) -> dict:
    leitura["id"] = str(leitura.pop("_id"))
    if leitura.get("item_id") is not None:
        leitura["item_id"] = str(leitura["item_id"])
    return leitura


async def criar_item(db, data: CriarItem) -> dict:
    item = data.model_dump()
    try:
        result = await db.items.insert_one(item)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta tag já está associada a outro item.",
        ) from exc
    item["_id"] = result.inserted_id
    return serializar_item(item)


async def buscar_item(db, item_id: str) -> dict:
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    item = await db.items.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    return serializar_item(item)

async def listar_itens(db, skip: int, limit: int) -> list[dict]:
    itens = await db.items.find().sort("nome", 1).skip(skip).limit(limit).to_list()
    return [serializar_item(item) for item in itens]


async def atualizar_item(db, item_id: str, data: AtualizarItem) -> dict:
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    updates = data.model_dump(exclude_unset=True)
    try:
        item = await db.items.find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta tag já está associada a outro item.",
        ) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    return serializar_item(item)


async def deletar_item(db, item_id: str) -> None:
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    resultado = await db.items.delete_one({"_id": ObjectId(item_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item não encontrado.")


async def registrar_leitura(db, data: CriarLeitura) -> dict:
    item = await db.items.find_one({"tag_id": data.tag_id})
    leitura = {
        "tag_id": data.tag_id,
        "leitor_id": data.reader_id,
        "leitura_em": datetime.now(timezone.utc),
        "status": "matched" if item else "unknown",
        "item_id": item["_id"] if item else None,
        "nome_item": item["name"] if item else None,
    }
    result = await db.readings.insert_one(leitura)
    resposta = {
        **leitura,
        "_id": result.inserted_id,
        "audio_descricao": item["audio_descricao"] if item else None,
    }
    return serializar_leitura(resposta)


async def listar_leituras(db, skip: int, limit: int, tag_id: str | None) -> list[dict]:
    query = {}
    if tag_id:
        query["tag_id"] = tag_id
    leituras = (
        await db.readings.find(query)
        .sort("read_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return [serializar_leitura(leitura) for leitura in leituras]
