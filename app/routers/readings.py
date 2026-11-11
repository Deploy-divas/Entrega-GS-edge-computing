from typing import Annotated

from fastapi import APIRouter, Query, Request, status

from app.schemas import ReadingCreate, ReadingHistoryItem, ReadingResponse
from app.services import list_readings, register_reading

router = APIRouter(prefix="/api/v1/readings", tags=["Leituras"])


@router.post("", response_model=ReadingResponse, status_code=status.HTTP_201_CREATED)
async def add_reading(data: ReadingCreate, request: Request):
    return await register_reading(request.app.state.db, data)


@router.get("", response_model=list[ReadingHistoryItem])
async def get_readings(
    request: Request,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    tag_id: str | None = None,
):
    return await list_readings(request.app.state.db, skip, limit, tag_id)
