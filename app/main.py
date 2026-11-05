from fastapi import FastAPI
from app.api.v1.routers.api import api_router

app = FastAPI(
    title="Sistema de Gestão de Eventos Acadêmicos",
    description="API para gerenciamento de eventos acadêmicos, inscrições, certificados e organizadores, com autenticação JWT.",
    version="2.0.0"
)

@app.get("/", tags=["Início"])
def inicio():
    return {"mensagem": "API do Sistema de Gestão de Eventos Acadêmicos em funcionamento!"}

app.include_router(api_router)

