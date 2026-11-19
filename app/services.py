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
        result = await db.itens.insert_one(item)
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
    item = await db.itens.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    return serializar_item(item)

async def listar_itens(db, skip: int, limit: int) -> list[dict]:
    itens = await db.itens.find().sort("id_tag", 1).skip(skip).limit(limit).to_list()
    return [serializar_item(item) for item in itens]


async def atualizar_item(db, item_id: str, data: AtualizarItem) -> dict:
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    updates = data.model_dump(exclude_unset=True)
    try:
        item = await db.itens.find_one_and_update(
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
    resultado = await db.itens.delete_one({"_id": ObjectId(item_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item não encontrado.")


async def registrar_leitura(db, data: CriarLeitura) -> dict:
    item = await db.items.find_one({"tag_id": data.tag_id})

    if item:
        status_leitura = "encontrada"
        item_id = str(item["_id"])

        conteudo = item.get("conteudo_audio", {})
        audio = conteudo.get("audiodescricao")
    else:
        status_leitura = "desconhecida"
        item_id = None
        audio = None
    nova_leitura = {
        "tag_id": data.tag_id,
        "leitor_id": data.leitor_id,
        "status": status_leitura,
        "item_id": item_id,
        "audiodescricao": audio,  # Mapeia para o schema
        "leitura_em": datetime.now(timezone.utc)
    }

    nova_leitura_salva = await db.leituras.insert_one(nova_leitura)
    nova_leitura["id"] = str(nova_leitura_salva.inserted_id)

    return nova_leitura


async def listar_leituras(db, skip: int, limit: int, tag_id: str | None) -> list[dict]:
    query = {}
    if tag_id:
        query["tag_id"] = tag_id
    leituras = (
        await db.leituras.find(query)
        .sort("leitura_em", -1)
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return [serializar_leitura(leitura) for leitura in leituras]

