from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.schemas import ProductCreate, AtualizarProduto, ReadingCreate


def serialize_product(product: dict) -> dict:
    product["_id"] = str(product["_id"])
    return product


def serialize_reading(reading: dict) -> dict:
    reading["id"] = str(reading.pop("_id"))
    if reading.get("product_id") is not None:
        reading["product_id"] = str(reading["product_id"])
    return reading


async def create_product(db, data: ProductCreate) -> dict:
    product = data.model_dump()
    try:
        result = await db.products.insert_one(product)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta tag já está associada a outro produto.",
        ) from exc
    product["_id"] = result.inserted_id
    return serialize_product(product)


async def get_product(db, product_id: str) -> dict:
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return serialize_product(product)


async def list_products(db, skip: int, limit: int) -> list[dict]:
    products = await db.products.find().sort("name", 1).skip(skip).limit(limit).to_list()
    return [serialize_product(product) for product in products]


async def update_product(db, product_id: str, data: AtualizarProduto) -> dict:
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    updates = data.model_dump(exclude_unset=True)
    try:
        product = await db.products.find_one_and_update(
            {"_id": ObjectId(product_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta tag já está associada a outro produto.",
        ) from exc
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return serialize_product(product)


async def delete_product(db, product_id: str) -> None:
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")


async def register_reading(db, data: ReadingCreate) -> dict:
    product = await db.products.find_one({"tag_id": data.tag_id})
    reading = {
        "tag_id": data.tag_id,
        "reader_id": data.reader_id,
        "read_at": datetime.now(timezone.utc),
        "status": "matched" if product else "unknown",
        "product_id": product["_id"] if product else None,
        "product_name": product["name"] if product else None,
    }
    result = await db.readings.insert_one(reading)
    response = {
        **reading,
        "_id": result.inserted_id,
        "audio_description": product["audio_description"] if product else None,
    }
    return serialize_reading(response)


async def list_readings(db, skip: int, limit: int, tag_id: str | None) -> list[dict]:
    query = {}
    if tag_id:
        query["tag_id"] = tag_id
    readings = (
        await db.readings.find(query)
        .sort("read_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return [serialize_reading(reading) for reading in readings]
