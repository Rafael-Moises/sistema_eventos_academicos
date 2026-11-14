
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class Evento(SchemaBase):
    id: Optional[int] = Field(default=None, gt=0)
    titulo: str = Field(min_length=3, max_length=150)
    descricao: str = Field(min_length=1)
    data: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    horario: str = Field(
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    )
    local: str = Field(min_length=1, max_length=150)
    categoria_id: int = Field(gt=0)
    organizador_id: int = Field(gt=0)
    vagas: int = Field(gt=0)


class Categoria(SchemaBase):
    id: Optional[int] = Field(default=None, gt=0)
    nome: str = Field(min_length=1, max_length=100)


class Usuario(SchemaBase):
    id: Optional[int] = Field(default=None, gt=0)
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    tipo: str = Field(min_length=1, max_length=50)


class Inscricao(SchemaBase):
    id: Optional[int] = Field(default=None, gt=0)
    usuario_id: int = Field(gt=0)
    evento_id: int = Field(gt=0)
    status: str = Field(min_length=1, max_length=50)


class Certificado(SchemaBase):
    id: Optional[int] = Field(default=None, gt=0)
    inscricao_id: int = Field(gt=0)
    codigo: str = Field(min_length=1, max_length=100)
    data_emissao: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class Organizador(SchemaBase):
    id: Optional[int] = Field(default=None, gt=0)
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    tipo: str = Field(min_length=1, max_length=50)


class UsuarioCadastro(SchemaBase):
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class LoginRequest(SchemaBase):
    email: EmailStr
    senha: str
