from datetime import datetime
from typing import Literal, List, Dict, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

def normalizar_tag(valor: str | None) -> str | None:
    if valor is None:
        return None
    valor = valor.strip().upper()
    if not valor:
        raise ValueError("O ID da tag não pode ficar vazio.")
    return valor

class ConteudoAudio(BaseModel):
    audiodescricao: str = Field(min_length=1, max_length=120)

class DetalhesExtras(BaseModel):
    validade: str | None = None
    alergenicos: list[str] | None = None

class CriarItem(BaseModel):
    tag_id: str = Field(min_length=1, max_length=100)
    categoria: str = Field(min_length=1, max_length=80)
    conteudo_audio: ConteudoAudio
    detalhes_extras: DetalhesExtras | None = None

    @field_validator("categoria")
    @classmethod
    def strip_text(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("A categoria não pode ficar vazia.")
        return valor

    @field_validator("tag_id")
    @classmethod
    def clean_tag_id(cls, valor: str) -> str:
        normalizado = normalizar_tag(valor)
        if not normalizado:
            raise ValueError("Tag inválida")
        return normalizado

class AtualizarItem(BaseModel):
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    conteudo_audio: ConteudoAudio
    tag_id: str | None = Field(default=None, max_length=100)
    detalhes_extras: DetalhesExtras | None = None

    @field_validator("categoria","conteudo_audio")
    @classmethod
    def strip_text(cls, valor: str | None) -> str | None:
        if valor is None:
            raise ValueError("Este campo não pode ficar vazio.")
        valor = valor.strip()
        if not valor:
            raise ValueError("Este campo não pode ficar vazio.")
        return valor

    @field_validator("tag_id")
    @classmethod
    def clean_tag_id(cls, valor: str | None) -> str | None:
        return normalizar_tag(valor)

    @model_validator(mode="after")
    def reenviar_campos(self):
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        return self


class RespostaItem(BaseModel):
    id: str | None = None
    tag_id: str
    categoria: str
    conteudo_audio: ConteudoAudio
    detalhes_extras: DetalhesExtras | None = None


class CriarLeitura(BaseModel):
    tag_id: str = Field(min_length=1, max_length=100)
    leitor_id: str = Field(min_length=1, max_length=100)

    @field_validator("tag_id")
    @classmethod
    def limpar_tag(cls, valor: str) -> str:
        normalizado = normalizar_tag(valor)
        assert normalizado is not None
        return normalizado

    @field_validator("leitor_id", check_fields=False)
    @classmethod
    def limpar_leitor_id(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        valor = valor.strip()
        if not valor:
            raise ValueError("O ID do leitor, quando informado, não pode ficar vazio.")
        return valor


class RespostaLeitura(BaseModel):
    id: str
    tag_id: str
    leitor_id: str | None = None
    status: Literal["encontrada", "desconhecida"]
    item_id: str | None = None
    audiodescricao: str | None = None
    leitura_em: datetime

class HistoricoLeitura(BaseModel):
    id: str
    tag_id: str
    leitor_id: str | None = None
    status: Literal["encontrada", "desconhecida"]
    item_id: str | None = None
    leitura_em: datetime

class NotificacaoOrion(BaseModel):
    subscriptionId: str
    data: List[Dict[str, Any]]

class RespostaOrion(BaseModel):
    id_tag_lida: str
    id_entidade: str
    status: str