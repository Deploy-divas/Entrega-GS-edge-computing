from typing import Annotated

from fastapi import APIRouter, Query, Request, status

from app.schemas import CriarLeitura, HistoricoLeitura, RespostaLeitura
from app.services import listar_leituras, registrar_leitura

router = APIRouter(prefix="/api/v1/readings", tags=["Leituras"])

@router.post("", response_model=RespostaLeitura, status_code=status.HTTP_201_CREATED)
async def add_reading(data: CriarLeitura, request: Request):
    return await registrar_leitura(request.app.state.db, data)

@router.get("", response_model=list[HistoricoLeitura])
async def get_readings(
    request: Request,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    tag_id: str | None = None,
):
    return await listar_leituras(request.app.state.db, skip, limit, tag_id)
