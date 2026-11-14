
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import exigir_perfis
from app.models.db_models import (
    EventoDB,
    CategoriaDB,
    UsuarioDB,
    InscricaoDB,
    OrganizadorDB
)
from app.schemas.model import Evento


router = APIRouter(tags=["Eventos"])


def normalizar_email(email: str) -> str:
    """Padroniza o e-mail para comparação."""
    return email.strip().casefold()


def validar_data_evento(data: str, mensagem_data_passada: str):
    """Valida o formato e impede eventos com datas anteriores a hoje."""
    try:
        data_evento = date.fromisoformat(data)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="A data deve estar no formato AAAA-MM-DD."
        )

    if data_evento < date.today():
        raise HTTPException(
            status_code=400,
            detail=mensagem_data_passada
        )


def verificar_dono_evento(
    evento_db: EventoDB,
    usuario: UsuarioDB,
    db: Session
):
    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == evento_db.organizador_id
    ).first()

    if (
        organizador is None
        or normalizar_email(organizador.email)
        != normalizar_email(usuario.email)
    ):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para administrar este evento."
        )


@router.get("/eventos")
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(EventoDB).all()


@router.post("/eventos", status_code=201)
def criar_evento(
    evento: Evento,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(exigir_perfis("Organizador"))
):
    categoria = db.query(CategoriaDB).filter(
        CategoriaDB.id == evento.categoria_id
    ).first()

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada."
        )

    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == evento.organizador_id
    ).first()

    if organizador is None:
        raise HTTPException(
            status_code=404,
            detail="Organizador não encontrado."
        )

    if normalizar_email(organizador.email) != normalizar_email(usuario_atual.email):
        raise HTTPException(
            status_code=403,
            detail="Você só pode criar eventos vinculados à sua conta."
        )

    if evento.vagas <= 0:
        raise HTTPException(
            status_code=400,
            detail="O número de vagas deve ser maior que zero."
        )

    validar_data_evento(
        evento.data,
        "Não é permitido cadastrar evento com data passada."
    )

    novo_evento = EventoDB(
        titulo=evento.titulo,
        descricao=evento.descricao,
        data=evento.data,
        horario=evento.horario,
        local=evento.local,
        categoria_id=evento.categoria_id,
        organizador_id=evento.organizador_id,
        vagas=evento.vagas
    )

    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)

    return {
        "mensagem": "Evento criado com sucesso!",
        "evento": novo_evento
    }


@router.get("/eventos/{evento_id}")
def buscar_evento(
    evento_id: int,
    db: Session = Depends(get_db)
):
    evento = db.query(EventoDB).filter(
        EventoDB.id == evento_id
    ).first()

    if evento is None:
        raise HTTPException(
            status_code=404,
            detail="Evento não encontrado."
        )

    return evento


@router.put("/eventos/{evento_id}")
def atualizar_evento(
    evento_id: int,
    evento: Evento,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(exigir_perfis("Organizador"))
):
    evento_db = db.query(EventoDB).filter(
        EventoDB.id == evento_id
    ).first()

    if evento_db is None:
        raise HTTPException(
            status_code=404,
            detail="Evento não encontrado."
        )

    verificar_dono_evento(evento_db, usuario_atual, db)

    categoria = db.query(CategoriaDB).filter(
        CategoriaDB.id == evento.categoria_id
    ).first()

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada."
        )

    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == evento.organizador_id
    ).first()

    if organizador is None:
        raise HTTPException(
            status_code=404,
            detail="Organizador não encontrado."
        )

    if normalizar_email(organizador.email) != normalizar_email(usuario_atual.email):
        raise HTTPException(
            status_code=403,
            detail="Você não pode transferir o evento para outro organizador."
        )

    if evento.vagas <= 0:
        raise HTTPException(
            status_code=400,
            detail="O número de vagas deve ser maior que zero."
        )

    inscricoes_ativas = db.query(InscricaoDB).filter(
        InscricaoDB.evento_id == evento_id,
        InscricaoDB.status.in_(["Pendente", "Confirmada"])
    ).count()

    if evento.vagas < inscricoes_ativas:
        raise HTTPException(
            status_code=400,
            detail="O número de vagas não pode ser menor que a quantidade de inscrições ativas."
        )

    validar_data_evento(
        evento.data,
        "Não é permitido atualizar evento para uma data passada."
    )

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

    return {
        "mensagem": "Evento atualizado com sucesso!",
        "evento": evento_db
    }


@router.delete("/eventos/{evento_id}")
def excluir_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(exigir_perfis("Organizador"))
):
    evento_db = db.query(EventoDB).filter(
        EventoDB.id == evento_id
    ).first()

    if evento_db is None:
        raise HTTPException(
            status_code=404,
            detail="Evento não encontrado."
        )

    verificar_dono_evento(evento_db, usuario_atual, db)

    inscricoes = db.query(InscricaoDB).filter(
        InscricaoDB.evento_id == evento_id
    ).count()

    if inscricoes > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir um evento que possui inscrições."
        )

    db.delete(evento_db)
    db.commit()

    return {"mensagem": "Evento excluído com sucesso!"}
