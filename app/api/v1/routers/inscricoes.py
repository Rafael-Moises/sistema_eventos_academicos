
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import exigir_perfis
from app.models.db_models import (
    EventoDB,
    UsuarioDB,
    InscricaoDB,
    CertificadoDB,
    OrganizadorDB
)
from app.schemas.model import Inscricao


router = APIRouter(tags=["Inscrições"])


def verificar_acesso_inscricao(
    inscricao: InscricaoDB,
    usuario_atual: UsuarioDB,
    db: Session
):
    perfil = (usuario_atual.tipo or "").strip().casefold()

    if perfil == "participante":
        if inscricao.usuario_id != usuario_atual.id:
            raise HTTPException(
                status_code=403,
                detail="Você só pode acessar suas próprias inscrições."
            )
        return

    if perfil == "organizador":
        evento = db.query(EventoDB).filter(
            EventoDB.id == inscricao.evento_id
        ).first()

        organizador = db.query(OrganizadorDB).filter(
            OrganizadorDB.id == evento.organizador_id
        ).first() if evento else None

        if (
            organizador is None
            or (organizador.email or "").strip().casefold()
            != (usuario_atual.email or "").strip().casefold()
        ):
            raise HTTPException(
                status_code=403,
                detail="Você só pode acessar inscrições dos seus eventos."
            )
        return

    raise HTTPException(
        status_code=403,
        detail="Perfil sem permissão para acessar inscrições."
    )


@router.get("/inscricoes")
def listar_inscricoes(
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(
        exigir_perfis("Participante", "Organizador")
    )
):
    perfil = (usuario_atual.tipo or "").strip().casefold()

    if perfil == "participante":
        return db.query(InscricaoDB).filter(
            InscricaoDB.usuario_id == usuario_atual.id
        ).all()

    eventos = db.query(EventoDB).join(
        OrganizadorDB,
        EventoDB.organizador_id == OrganizadorDB.id
    ).filter(
        OrganizadorDB.email.ilike(usuario_atual.email)
    ).all()

    ids_eventos = [evento.id for evento in eventos]

    if not ids_eventos:
        return []

    return db.query(InscricaoDB).filter(
        InscricaoDB.evento_id.in_(ids_eventos)
    ).all()


@router.get("/inscricoes/{inscricao_id}")
def buscar_inscricao(
    inscricao_id: int,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(
        exigir_perfis("Participante", "Organizador")
    )
):
    inscricao = db.query(InscricaoDB).filter(
        InscricaoDB.id == inscricao_id
    ).first()

    if inscricao is None:
        raise HTTPException(
            status_code=404,
            detail="Inscrição não encontrada."
        )

    verificar_acesso_inscricao(inscricao, usuario_atual, db)

    return inscricao


@router.post("/inscricoes", status_code=201)
def criar_inscricao(
    inscricao: Inscricao,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(
        exigir_perfis("Participante")
    )
):
    if inscricao.usuario_id != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode realizar inscrições em seu próprio nome."
        )

    if inscricao.status != "Pendente":
        raise HTTPException(
            status_code=400,
            detail="Uma nova inscrição deve ser criada com status Pendente."
        )

    evento = db.query(EventoDB).filter(
        EventoDB.id == inscricao.evento_id
    ).first()

    if evento is None:
        raise HTTPException(
            status_code=404,
            detail="Evento não encontrado."
        )

    total_inscricoes = db.query(InscricaoDB).filter(
        InscricaoDB.evento_id == inscricao.evento_id,
        InscricaoDB.status.in_(["Pendente", "Confirmada"])
    ).count()

    if total_inscricoes >= evento.vagas:
        raise HTTPException(
            status_code=400,
            detail="O evento já atingiu o limite de vagas."
        )

    inscricao_existente = db.query(InscricaoDB).filter(
        InscricaoDB.usuario_id == usuario_atual.id,
        InscricaoDB.evento_id == inscricao.evento_id
    ).first()

    if inscricao_existente:
        raise HTTPException(
            status_code=400,
            detail="Este usuário já está inscrito neste evento."
        )

    nova_inscricao = InscricaoDB(
        usuario_id=usuario_atual.id,
        evento_id=inscricao.evento_id,
        status="Pendente"
    )

    db.add(nova_inscricao)
    db.commit()
    db.refresh(nova_inscricao)

    return {
        "mensagem": "Inscrição criada com sucesso!",
        "inscricao": nova_inscricao
    }


@router.put("/inscricoes/{inscricao_id}")
def atualizar_inscricao(
    inscricao_id: int,
    inscricao: Inscricao,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(
        exigir_perfis("Participante")
    )
):
    inscricao_db = db.query(InscricaoDB).filter(
        InscricaoDB.id == inscricao_id
    ).first()

    if inscricao_db is None:
        raise HTTPException(
            status_code=404,
            detail="Inscrição não encontrada."
        )

    verificar_acesso_inscricao(inscricao_db, usuario_atual, db)

    if inscricao.status != "Cancelada":
        raise HTTPException(
            status_code=403,
            detail="O participante só pode cancelar sua própria inscrição."
        )

    if (
        inscricao.usuario_id != inscricao_db.usuario_id
        or inscricao.evento_id != inscricao_db.evento_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Não é permitido alterar o usuário ou o evento da inscrição."
        )

    inscricao_db.status = "Cancelada"

    db.commit()
    db.refresh(inscricao_db)

    return {
        "mensagem": "Inscrição cancelada com sucesso!",
        "inscricao": inscricao_db
    }


@router.delete("/inscricoes/{inscricao_id}")
def excluir_inscricao(
    inscricao_id: int,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioDB = Depends(
        exigir_perfis("Participante")
    )
):
    inscricao_db = db.query(InscricaoDB).filter(
        InscricaoDB.id == inscricao_id
    ).first()

    if inscricao_db is None:
        raise HTTPException(
            status_code=404,
            detail="Inscrição não encontrada."
        )

    verificar_acesso_inscricao(inscricao_db, usuario_atual, db)

    certificado = db.query(CertificadoDB).filter(
        CertificadoDB.inscricao_id == inscricao_id
    ).first()

    if certificado is not None:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir uma inscrição que possui certificado."
        )

    db.delete(inscricao_db)
    db.commit()

    return {"mensagem": "Inscrição excluída com sucesso!"}
