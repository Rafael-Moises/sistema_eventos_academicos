
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import exigir_perfis
from app.models.db_models import EventoDB, OrganizadorDB
from app.schemas.model import Organizador

router = APIRouter(tags=["Organizadores"])


def verificar_dono(organizador, usuario):
    email_organizador = (
        (organizador.email or "").strip().casefold()
    )
    email_usuario = (
        (usuario.email or "").strip().casefold()
    )

    if email_organizador != email_usuario:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para acessar este organizador."
        )


@router.get("/organizadores")
def listar_organizadores(
    db: Session = Depends(get_db),
    usuario=Depends(
        exigir_perfis("Participante", "Organizador")
    )
):
    return db.query(OrganizadorDB).all()


@router.get("/organizadores/{organizador_id}")
def buscar_organizador(
    organizador_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(
        exigir_perfis("Participante", "Organizador")
    )
):
    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == organizador_id
    ).first()

    if organizador is None:
        raise HTTPException(
            status_code=404,
            detail="Organizador não encontrado."
        )

    return organizador


@router.post("/organizadores", status_code=201)
def criar_organizador(
    organizador: Organizador,
    db: Session = Depends(get_db),
    usuario=Depends(
        exigir_perfis("Organizador")
    )
):
    email_solicitado = (
        (organizador.email or "").strip().casefold()
    )
    email_usuario = (
        (usuario.email or "").strip().casefold()
    )

    if email_solicitado != email_usuario:
        raise HTTPException(
            status_code=403,
            detail="Você só pode cadastrar seu próprio e-mail."
        )

    existente = db.query(OrganizadorDB).filter(
        func.lower(func.trim(OrganizadorDB.email))
        == email_usuario
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um organizador com este e-mail."
        )

    novo = OrganizadorDB(
        nome=organizador.nome,
        email=usuario.email,
        tipo="Organizador"
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "mensagem": "Organizador criado com sucesso!",
        "organizador": novo
    }


@router.put("/organizadores/{organizador_id}")
def atualizar_organizador(
    organizador_id: int,
    dados: Organizador,
    db: Session = Depends(get_db),
    usuario=Depends(
        exigir_perfis("Organizador")
    )
):
    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == organizador_id
    ).first()

    if organizador is None:
        raise HTTPException(
            status_code=404,
            detail="Organizador não encontrado."
        )

    verificar_dono(organizador, usuario)

    email_solicitado = (
        (dados.email or "").strip().casefold()
    )
    email_usuario = (
        (usuario.email or "").strip().casefold()
    )

    if email_solicitado != email_usuario:
        raise HTTPException(
            status_code=403,
            detail="Não é permitido alterar o e-mail do organizador."
        )

    organizador.nome = dados.nome
    organizador.tipo = "Organizador"

    db.commit()
    db.refresh(organizador)

    return {
        "mensagem": "Organizador atualizado com sucesso!",
        "organizador": organizador
    }


@router.delete("/organizadores/{organizador_id}")
def excluir_organizador(
    organizador_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(
        exigir_perfis("Organizador")
    )
):
    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == organizador_id
    ).first()

    if organizador is None:
        raise HTTPException(
            status_code=404,
            detail="Organizador não encontrado."
        )

    verificar_dono(organizador, usuario)

    eventos = db.query(EventoDB).filter(
        EventoDB.organizador_id == organizador_id
    ).count()

    if eventos > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir um organizador vinculado a eventos."
        )

    db.delete(organizador)
    db.commit()

    return {
        "mensagem": "Organizador excluído com sucesso!"
    }
