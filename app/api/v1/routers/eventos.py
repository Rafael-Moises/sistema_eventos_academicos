from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.db_models import EventoDB, CategoriaDB, UsuarioDB, InscricaoDB, CertificadoDB, OrganizadorDB
from app.schemas.model import Evento, Categoria, Usuario, Inscricao, Certificado, Organizador

router = APIRouter(tags=["Eventos"])

@router.get('/eventos')
def listar_eventos(db: Session = Depends(get_db)):
    eventos_db = db.query(EventoDB).all()
    return eventos_db

@router.post('/eventos', status_code=201, dependencies=[Depends(get_current_user)])
def criar_evento(evento: Evento, db: Session = Depends(get_db)):
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id == evento.categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    organizador = db.query(OrganizadorDB).filter(OrganizadorDB.id == evento.organizador_id).first()
    if organizador is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    if evento.vagas <= 0:
        raise HTTPException(status_code=400, detail="O número de vagas deve ser maior que zero.")
    try:
        data_evento = date.fromisoformat(evento.data)
    except ValueError:
        raise HTTPException(status_code=400, detail="A data deve estar no formato AAAA-MM-DD.")
    if data_evento < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido cadastrar evento com data passada.")
    novo_evento = (EventoDB
        (titulo=evento.titulo,
        descricao=evento.descricao,
        data=evento.data,
        horario=evento.horario,
        local=evento.local,
        categoria_id=evento.categoria_id,
        organizador_id=evento.organizador_id,
        vagas=evento.vagas))
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)
    return {"mensagem": "Evento criado com sucesso!", "evento": novo_evento}

@router.get('/eventos/{evento_id}')
def buscar_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(EventoDB).filter( EventoDB.id == evento_id).first()
    if evento is None:
        raise HTTPException( status_code=404, detail="Evento não encontrado.")
    return evento

@router.put('/eventos/{evento_id}')
def atualizar_evento(evento_id: int, evento: Evento, db: Session = Depends(get_db)):
    evento_db = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if evento_db is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    if evento.vagas <= 0:
        raise HTTPException(status_code=400, detail="O número de vagas deve ser maior que zero.")
    inscricoes_ativas = db.query(InscricaoDB).filter(InscricaoDB.evento_id == evento_id, InscricaoDB.status.in_(["Pendente", "Confirmada"])).count()
    if evento.vagas < inscricoes_ativas:
        raise HTTPException(status_code=400, detail="O número de vagas não pode ser menor que a quantidade de inscrições ativas.")
    try:
        data_evento = date.fromisoformat(evento.data)
    except ValueError:
        raise HTTPException(status_code=400, detail="A data deve estar no formato AAAA-MM-DD.")
    if data_evento < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido atualizar evento para uma data passada.")
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id == evento.categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == evento.organizador_id).first()
    if organizador is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    evento_db.titulo = evento.titulo
    evento_db.descricao = evento.descricao
    evento_db.data = evento.data
    evento_db.horario = evento.horario
    evento_db.local = evento.local
    evento_db.categoria_id = evento.categoria_id
    evento_db.organizador_id = evento.organizador_id
    evento_db.vagas = evento.vagas
    db.commit()
    db.refresh(evento_db)
    return {"mensagem": "Evento atualizado com sucesso!", "evento": evento_db}

@router.delete('/eventos/{evento_id}')
def excluir_evento(evento_id: int, db: Session = Depends(get_db)):
    evento_db = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if evento_db is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    inscricoes = db.query(InscricaoDB).filter(InscricaoDB.evento_id == evento_id).count()
    if inscricoes > 0:
        raise HTTPException(status_code=400, detail="Não é possível excluir um evento que possui inscrições.")
    db.delete(evento_db)
    db.commit()
    return {"mensagem": "Evento excluído com sucesso!"}
