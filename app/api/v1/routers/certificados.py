
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import exigir_perfis
from app.models.db_models import (
    EventoDB,
    InscricaoDB,
    CertificadoDB,
    OrganizadorDB,
    UsuarioDB
)
from app.schemas.model import Certificado

router = APIRouter(tags=["Certificados"])


def verificar_acesso_inscricao(
    inscricao: InscricaoDB,
    usuario: UsuarioDB,
    db: Session
):
    perfil = (usuario.tipo or "").strip().casefold()

    if perfil == "participante":
        if inscricao.usuario_id != usuario.id:
            raise HTTPException(
                status_code=403,
                detail="Você só pode acessar seus próprios certificados."
            )
        return inscricao

    if perfil == "organizador":
        evento = db.query(EventoDB).filter(
            EventoDB.id == inscricao.evento_id
        ).first()

        organizador = db.query(OrganizadorDB).filter(
            OrganizadorDB.id == evento.organizador_id
        ).first() if evento else None

        email_organizador = (
            (organizador.email or "").strip().casefold()
            if organizador else ""
        )
        email_usuario = (usuario.email or "").strip().casefold()

        if not organizador or email_organizador != email_usuario:
            raise HTTPException(
                status_code=403,
                detail="Você só pode acessar certificados dos seus eventos."
            )
        return inscricao

    raise HTTPException(
        status_code=403,
        detail="Perfil sem permissão para acessar certificados."
    )


def buscar_inscricao_do_certificado(
    certificado: CertificadoDB,
    usuario: UsuarioDB,
    db: Session
):
    inscricao = db.query(InscricaoDB).filter(
        InscricaoDB.id == certificado.inscricao_id
    ).first()

    if inscricao is None:
        raise HTTPException(
            status_code=404,
            detail="Inscrição não encontrada."
        )

    verificar_acesso_inscricao(inscricao, usuario, db)
    return inscricao


def validar_data_emissao(data):
    try:
        data_emissao = date.fromisoformat(data)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="A data de emissão deve estar no formato AAAA-MM-DD."
        )

    if data_emissao > date.today():
        raise HTTPException(
            status_code=400,
            detail="A data de emissão não pode ser futura."
        )


@router.get("/certificados")
def listar_certificados(
    db: Session = Depends(get_db),
    usuario: UsuarioDB = Depends(
        exigir_perfis("Participante", "Organizador")
    )
):
    consulta = db.query(CertificadoDB).join(
        InscricaoDB,
        CertificadoDB.inscricao_id == InscricaoDB.id
    )

    perfil = (usuario.tipo or "").strip().casefold()

    if perfil == "participante":
        consulta = consulta.filter(
            InscricaoDB.usuario_id == usuario.id
        )
    else:
        consulta = consulta.join(
            EventoDB,
            InscricaoDB.evento_id == EventoDB.id
        ).join(
            OrganizadorDB,
            EventoDB.organizador_id == OrganizadorDB.id
        ).filter(
            func.lower(func.trim(OrganizadorDB.email))
            == (usuario.email or "").strip().casefold()
        )

    return consulta.all()


@router.get("/certificados/{certificado_id}")
def buscar_certificado(
    certificado_id: int,
    db: Session = Depends(get_db),
    usuario: UsuarioDB = Depends(
        exigir_perfis("Participante", "Organizador")
    )
):
    certificado = db.query(CertificadoDB).filter(
        CertificadoDB.id == certificado_id
    ).first()

    if certificado is None:
        raise HTTPException(
            status_code=404,
            detail="Certificado não encontrado."
        )

    buscar_inscricao_do_certificado(certificado, usuario, db)

    return certificado


@router.post("/certificados", status_code=201)
def criar_certificado(
    certificado: Certificado,
    db: Session = Depends(get_db),
    usuario: UsuarioDB = Depends(
        exigir_perfis("Organizador")
    )
):
    inscricao = db.query(InscricaoDB).filter(
        InscricaoDB.id == certificado.inscricao_id
    ).first()

    if inscricao is None:
        raise HTTPException(
            status_code=404,
            detail="Inscrição não encontrada."
        )

    verificar_acesso_inscricao(inscricao, usuario, db)

    if inscricao.status != "Confirmada":
        raise HTTPException(
            status_code=400,
            detail="O certificado só pode ser emitido para uma inscrição confirmada."
        )

    validar_data_emissao(certificado.data_emissao)

    existente = db.query(CertificadoDB).filter(
        CertificadoDB.inscricao_id == certificado.inscricao_id
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um certificado para esta inscrição."
        )

    codigo_existente = db.query(CertificadoDB).filter(
        CertificadoDB.codigo == certificado.codigo
    ).first()

    if codigo_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um certificado com este código."
        )

    novo_certificado = CertificadoDB(
        inscricao_id=certificado.inscricao_id,
        codigo=certificado.codigo,
        data_emissao=certificado.data_emissao
    )

    db.add(novo_certificado)
    db.commit()
    db.refresh(novo_certificado)

    return {
        "mensagem": "Certificado emitido com sucesso!",
        "certificado": novo_certificado
    }


@router.put("/certificados/{certificado_id}")
def atualizar_certificado(
    certificado_id: int,
    certificado: Certificado,
    db: Session = Depends(get_db),
    usuario: UsuarioDB = Depends(
        exigir_perfis("Organizador")
    )
):
    certificado_db = db.query(CertificadoDB).filter(
        CertificadoDB.id == certificado_id
    ).first()

    if certificado_db is None:
        raise HTTPException(
            status_code=404,
            detail="Certificado não encontrado."
        )

    buscar_inscricao_do_certificado(certificado_db, usuario, db)

    inscricao = db.query(InscricaoDB).filter(
        InscricaoDB.id == certificado.inscricao_id
    ).first()

    if inscricao is None:
        raise HTTPException(
            status_code=404,
            detail="Inscrição não encontrada."
        )

    verificar_acesso_inscricao(inscricao, usuario, db)

    if inscricao.status != "Confirmada":
        raise HTTPException(
            status_code=400,
            detail="O certificado só pode ser associado a uma inscrição confirmada."
        )

    outro = db.query(CertificadoDB).filter(
        CertificadoDB.inscricao_id == certificado.inscricao_id,
        CertificadoDB.id != certificado_id
    ).first()

    if outro:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro certificado para esta inscrição."
        )

    codigo_existente = db.query(CertificadoDB).filter(
        CertificadoDB.codigo == certificado.codigo,
        CertificadoDB.id != certificado_id
    ).first()

    if codigo_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro certificado com este código."
        )

    validar_data_emissao(certificado.data_emissao)

    certificado_db.inscricao_id = certificado.inscricao_id
    certificado_db.codigo = certificado.codigo
    certificado_db.data_emissao = certificado.data_emissao

    db.commit()
    db.refresh(certificado_db)

    return {
        "mensagem": "Certificado atualizado com sucesso!",
        "certificado": certificado_db
    }


@router.delete("/certificados/{certificado_id}")
def excluir_certificado(
    certificado_id: int,
    db: Session = Depends(get_db),
    usuario: UsuarioDB = Depends(
        exigir_perfis("Organizador")
    )
):
    certificado = db.query(CertificadoDB).filter(
        CertificadoDB.id == certificado_id
    ).first()

    if certificado is None:
        raise HTTPException(
            status_code=404,
            detail="Certificado não encontrado."
        )

    buscar_inscricao_do_certificado(certificado, usuario, db)

    db.delete(certificado)
    db.commit()

    return {"mensagem": "Certificado excluído com sucesso!"}
