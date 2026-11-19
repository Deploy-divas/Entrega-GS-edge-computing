from typing import Annotated

from fastapi import APIRouter, Query, Request, status

from app.schemas import NotificacaoOrion, RespostaOrion, CriarLeitura, HistoricoLeitura, RespostaLeitura
from app.services import listar_leituras, registrar_leitura

router = APIRouter(prefix="/api/v1/notificacao", tags=["Notificação"])

@router.post("", response_model=RespostaOrion, status_code=status.HTTP_201_CREATED)
async def receber_notificacao_fiware(payload: NotificacaoOrion):
    entidade = payload.data[0]

    id_entidade = entidade.get("id")
    tipo_entidade = entidade.get("type")

    # valor tag_lida do FIWARE
    tag_rfid = entidade.get("tag_lida", {}).get("value")

    print(f"Notificação recebida da entidade {id_entidade}!")
    print(f"Tag lida: {tag_rfid}")

    return {"id_tag_lida":{tag_rfid}, "id_entidade": {id_entidade},"status": "sucesso"}
