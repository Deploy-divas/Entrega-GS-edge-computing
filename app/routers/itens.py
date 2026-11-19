from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status

from app.schemas import CriarItem, RespostaItem, AtualizarItem
from app.services import (
    criar_item,
    deletar_item,
    buscar_item,
    listar_itens,
    atualizar_item,
)

router = APIRouter(prefix="/api/v1/itens", tags=["Itens"])
#
# como o meu criar item está em routers/itens.py
@router.post("", response_model=RespostaItem, status_code=status.HTTP_201_CREATED)
async def adicionar_item(data: CriarItem, request: Request):
    return await criar_item(request.app.state.db, data)


@router.get("", response_model=list[RespostaItem])
async def buscar_itens(
    request: Request,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await listar_itens(request.app.state.db, skip, limit)


@router.get("/{item_id}", response_model=RespostaItem)
async def buscar_item_by_id(item_id: str, request: Request):
    return await buscar_item(request.app.state.db, item_id)


@router.patch("/{item_id}", response_model=RespostaItem)
async def editar_item(item_id: str, data: AtualizarItem, request: Request):
    return await atualizar_item(request.app.state.db, item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_item(item_id: str, request: Request):
    await deletar_item(request.app.state.db, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
