from pydantic import BaseModel
from typing import Optional
class Evento(BaseModel):
    id: Optional[int] = None
    titulo: str
    descricao: str
    data: str
    horario: str
    local: str
    categoria_id: int
    organizador_id: int
    vagas: int

class Categoria(BaseModel):
        id: Optional[int] = None
        nome: str

class Usuario(BaseModel):
    id: Optional[int] = None
    nome: str
    email: str
    tipo: str

class Inscricao(BaseModel):
    id: Optional[int] = None
    usuario_id: int
    evento_id: int
    status: str

class Certificado(BaseModel):
    id: Optional[int] = None
    inscricao_id: int
    codigo: str
    data_emissao: str

class Organizador(BaseModel):
    id: Optional[int] = None
    nome: str
    email: str
    tipo: str