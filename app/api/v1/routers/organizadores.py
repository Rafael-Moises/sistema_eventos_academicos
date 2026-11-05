from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.db_models import EventoDB, CategoriaDB, UsuarioDB, InscricaoDB, CertificadoDB, OrganizadorDB
from app.schemas.model import Evento, Categoria, Usuario, Inscricao, Certificado, Organizador

router = APIRouter(tags=["Organizadores"])

@router.get('/organizadores')
def listar_organizadores(db: Session = Depends(get_db)):
    organizadores_db = db.query(OrganizadorDB).all()
    return organizadores_db

@router.get('/organizadores/{organizador_id}')
def buscar_organizador(organizador_id: int, db: Session = Depends(get_db)):
    organizador_db = db.query(OrganizadorDB).filter(OrganizadorDB.id == organizador_id).first()
    if organizador_db is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    return organizador_db

@router.post('/organizadores', status_code=201)
def criar_organizador(organizador: Organizador, db: Session = Depends(get_db)):
    organizador_existente = db.query(OrganizadorDB).filter(OrganizadorDB.email == organizador.email).first()
    if organizador_existente:
        raise HTTPException(status_code=400, detail="Já existe um organizador com este e-mail.")
    novo_organizador = OrganizadorDB(nome=organizador.nome, email=organizador.email, tipo=organizador.tipo)
    db.add(novo_organizador)
    db.commit()
    db.refresh(novo_organizador)
    return {"mensagem": "Organizador criado com sucesso!", "organizador": novo_organizador}

@router.put('/organizadores/{organizador_id}')
def atualizar_organizador(organizador_id: int, organizador: Organizador, db: Session = Depends(get_db)):
    organizador_db = db.query(OrganizadorDB).filter(OrganizadorDB.id == organizador_id).first()
    if organizador_db is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    email_existente = db.query(OrganizadorDB).filter(OrganizadorDB.email == organizador.email, OrganizadorDB.id != organizador_id).first()
    if email_existente:
        raise HTTPException(status_code=400, detail="Já existe outro organizador com este e-mail.")
    organizador_db.nome = organizador.nome
    organizador_db.email = organizador.email
    organizador_db.tipo = organizador.tipo
    db.commit()
    db.refresh(organizador_db)
    return {"mensagem": "Organizador atualizado com sucesso!", "organizador": organizador_db}

@router.delete('/organizadores/{organizador_id}')
def excluir_organizador(organizador_id: int, db: Session = Depends(get_db)):
    organizador_db = db.query(OrganizadorDB).filter(OrganizadorDB.id == organizador_id).first()
    if organizador_db is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    eventos = db.query(EventoDB).filter(EventoDB.organizador_id == organizador_id).count()
    if eventos > 0:
        raise HTTPException(status_code=400, detail="Não é possível excluir um organizador que está vinculado a eventos.")
    db.delete(organizador_db)
    db.commit()
    return {"mensagem": "Organizador excluído com sucesso!"}
