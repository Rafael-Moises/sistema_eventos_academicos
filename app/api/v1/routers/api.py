from fastapi import APIRouter
from app.api.v1.routers import eventos, categorias, usuarios, inscricoes, certificados, organizadores, auth

api_router = APIRouter()
for modulo in (eventos, categorias, usuarios, inscricoes, certificados, organizadores, auth):
    api_router.include_router(modulo.router)
