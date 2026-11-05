from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.db_models import EventoDB, CategoriaDB, UsuarioDB, InscricaoDB, CertificadoDB, OrganizadorDB
from app.schemas.model import Evento, Categoria, Usuario, Inscricao, Certificado, Organizador

router = APIRouter(tags=["Inscricoes"])

@router.get('/inscricoes')
def listar_inscricoes(db: Session = Depends(get_db)):
    inscricoes_db = db.query(InscricaoDB).all()
    return inscricoes_db

@router.get('/inscricoes/{inscricao_id}')
def buscar_inscricao(inscricao_id: int, db: Session = Depends(get_db)):
    inscricao_db = db.query(InscricaoDB).filter(InscricaoDB.id == inscricao_id).first()
    if inscricao_db is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    return inscricao_db

@router.post('/inscricoes', status_code=201, dependencies=[Depends(get_current_user)])
def criar_inscricao(inscricao: Inscricao, db: Session = Depends(get_db)):
    status_validos = ["Pendente", "Confirmada", "Cancelada"]
    if inscricao.status not in status_validos:
        raise HTTPException(status_code=400, detail="Status inválido. Use Pendente, Confirmada ou Cancelada.")
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == inscricao.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    evento = db.query(EventoDB).filter(EventoDB.id == inscricao.evento_id).first()
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    total_inscricoes = db.query(InscricaoDB).filter(InscricaoDB.evento_id == inscricao.evento_id, InscricaoDB.status.in_(["Pendente", "Confirmada"])).count()
    if total_inscricoes >= evento.vagas:
        raise HTTPException(status_code=400, detail="O evento já atingiu o limite de vagas.")
    inscricao_existente = db.query(InscricaoDB).filter(InscricaoDB.usuario_id == inscricao.usuario_id, InscricaoDB.evento_id == inscricao.evento_id).first()
    if inscricao_existente:
        raise HTTPException(status_code=400, detail="Este usuário já está inscrito neste evento.")
    nova_inscricao = InscricaoDB(
        usuario_id=inscricao.usuario_id,
        evento_id=inscricao.evento_id,
        status=inscricao.status)
    db.add(nova_inscricao)
    db.commit()
    db.refresh(nova_inscricao)
    return {"mensagem": "Inscrição criada com sucesso!", "inscricao": nova_inscricao}

@router.put('/inscricoes/{inscricao_id}')
def atualizar_inscricao(inscricao_id: int, inscricao: Inscricao, db: Session = Depends(get_db)):
    status_validos = ["Pendente", "Confirmada", "Cancelada"]
    if inscricao.status not in status_validos:
        raise HTTPException(status_code=400, detail="Status inválido. Use Pendente, Confirmada ou Cancelada.")
    inscricao_db = db.query(InscricaoDB).filter(InscricaoDB.id == inscricao_id).first()
    if inscricao_db is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == inscricao.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    evento = db.query(EventoDB).filter(EventoDB.id == inscricao.evento_id).first()
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    if inscricao_db.evento_id != inscricao.evento_id:
        total_inscricoes = db.query(InscricaoDB).filter(InscricaoDB.evento_id == inscricao.evento_id, InscricaoDB.status.in_(["Pendente", "Confirmada"])).count()
        if total_inscricoes >= evento.vagas:
            raise HTTPException(status_code=400, detail="O evento já atingiu o limite de vagas.")
        inscricao_existente = db.query(InscricaoDB).filter(InscricaoDB.usuario_id == inscricao.usuario_id, InscricaoDB.evento_id == inscricao.evento_id, InscricaoDB.id != inscricao_id).first()
        if inscricao_existente:
            raise HTTPException(status_code=400, detail="Este usuário já está inscrito neste evento.")
    inscricao_db.usuario_id = inscricao.usuario_id
    inscricao_db.evento_id = inscricao.evento_id
    inscricao_db.status = inscricao.status
    db.commit()
    db.refresh(inscricao_db)
    return {"mensagem": "Inscrição atualizada com sucesso!", "inscricao": inscricao_db}

@router.delete('/inscricoes/{inscricao_id}')
def excluir_inscricao(inscricao_id: int, db: Session = Depends(get_db)):
    inscricao_db = db.query(InscricaoDB).filter(InscricaoDB.id == inscricao_id).first()
    if inscricao_db is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    certificado = db.query(CertificadoDB).filter(CertificadoDB.inscricao_id == inscricao_id).first()
    if certificado is not None:
        raise HTTPException(status_code=400, detail="Não é possível excluir uma inscrição que possui certificado.")
    db.delete(inscricao_db)
    db.commit()
    return {"mensagem": "Inscrição excluída com sucesso!"}
