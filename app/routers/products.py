from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status

from app.schemas import ProductCreate, ProductResponse, AtualizarProduto
from app.services import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)

router = APIRouter(prefix="/api/v1/products", tags=["Produtos"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(data: ProductCreate, request: Request):
    return await create_product(request.app.state.db, data)


@router.get("", response_model=list[ProductResponse])
async def get_products(
    request: Request,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await list_products(request.app.state.db, skip, limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: str, request: Request):
    return await get_product(request.app.state.db, product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
async def edit_product(product_id: str, data: AtualizarProduto, request: Request):
    return await update_product(request.app.state.db, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(product_id: str, request: Request):
    await delete_product(request.app.state.db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
