from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

def normalizar_tag(valor: str | None) -> str | None:
    if valor is None:
        return None
    valor = valor.strip().upper()
    if not valor:
        raise ValueError("O ID da tag não pode ficar vazio.")
    return valor

class CriarItem(BaseModel):
    nome: str = Field(min_length=6, max_length=120)
    categoria: str = Field(min_length=6, max_length=80)
    comodo_da_casa: str = Field(min_length=6, max_length=1000)
    descricao: str = Field(min_length=6, max_length=1000)
    audio_descricao: str = Field(min_length=6, max_length=3000)
    tag_id: str | None = Field(default=None, max_length=100)

    @field_validator("nome", "categoria", "descricao", "audio_descricao")
    @classmethod
    def strip_text(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("Este campo não pode ficar vazio.")
        return valor

    @field_validator("tag_id")
    @classmethod
    def clean_tag_id(cls, valor: str | None) -> str | None:
        return normalizar_tag(valor)


class AtualizarItem(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    comodo_da_casa: str | None = Field(default=None, min_length=1, max_length=80)
    descricao: str | None = Field(default=None, min_length=1, max_length=1000)
    audio_descricao: str | None = Field(default=None, min_length=1, max_length=3000)
    tag_id: str | None = Field(default=None, max_length=100)

    @field_validator("name", "categoria", "descricao", "audio_descricao")
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
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    nome: str
    categoria: str
    comodo_da_casa: str
    descricao: str
    audio_descricao: str
    tag_id: str | None = None


class CriarLeitura(BaseModel):
    tag_id: str = Field(min_length=1, max_length=100)
    reader_id: str | None = Field(default=None, max_length=100)

    @field_validator("tag_id")
    @classmethod
    def limpar_tag(cls, valor: str) -> str:
        normalizado = normalizar_tag(valor)
        assert normalizado is not None
        return normalizado

    @field_validator("reader_id")
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
    status: Literal["matched", "unknown"]
    item_id: str | None = None
    nome_item: str | None = None
    comodo_da_casa: str | None = None
    audio_descricao: str | None = None
    leitura_em: datetime


class HistoricoLeitura(BaseModel):
    id: str
    tag_id: str
    leitor_id: str | None = None
    status: Literal["matched", "unknown"]
    item_id: str | None = None
    nome_item: str | None = None
    leitura_em: datetime
