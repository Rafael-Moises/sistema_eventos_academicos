
from fastapi import FastAPI

from app.api.v1.routers.api import api_router


openapi_tags = [
    {
        "name": "Início",
        "description": "Informações gerais sobre o funcionamento da API."
    },
    {
        "name": "Autenticação",
        "description": "Cadastro de usuários, login e geração de tokens JWT."
    },
    {
        "name": "Usuários",
        "description": "Gerenciamento e consulta de usuários."
    },
    {
        "name": "Eventos",
        "description": "Cadastro, consulta, atualização e exclusão de eventos acadêmicos."
    },
    {
        "name": "Categorias",
        "description": "Gerenciamento das categorias dos eventos."
    },
    {
        "name": "Organizadores",
        "description": "Gerenciamento dos organizadores de eventos."
    },
    {
        "name": "Inscrições",
        "description": "Gerenciamento das inscrições dos participantes."
    },
    {
        "name": "Certificados",
        "description": "Emissão, consulta, atualização e exclusão de certificados."
    }
]


app = FastAPI(
    title="Sistema de Gestão de Eventos Acadêmicos",
    description="""
API REST para gerenciamento de eventos acadêmicos.

### Funcionalidades
- Cadastro e autenticação de usuários.
- Autenticação utilizando JWT.
- Gerenciamento de eventos e categorias.
- Gerenciamento de organizadores.
- Controle de inscrições.
- Emissão e gerenciamento de certificados.

### Segurança
Os endpoints protegidos exigem autenticação por token Bearer JWT.
""",
    version="3.0.0",
    openapi_tags=openapi_tags
)


@app.get(
    "/",
    tags=["Início"],
    summary="Verificar funcionamento da API",
    description="Retorna uma mensagem indicando que a API está funcionando."
)
def inicio():
    return {
        "mensagem": "API do Sistema de Gestão de Eventos Acadêmicos em funcionamento!"
    }


app.include_router(api_router)
