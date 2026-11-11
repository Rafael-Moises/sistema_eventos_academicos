
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.permissions import exigir_perfis
from app.models.db_models import UsuarioDB, InscricaoDB
from app.schemas.model import Usuario

router = APIRouter(tags=["Usuarios"])


@router.get("/me")
def usuario_atual(
    usuario: UsuarioDB = Depends(get_current_user)
):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo": usuario.tipo
    }


@router.get("/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Organizador"))
):
    return db.query(UsuarioDB).all()


@router.get("/usuarios/{usuario_id}")
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Participante", "Organizador"))
):
    usuario_db = db.query(UsuarioDB).filter(
        UsuarioDB.id == usuario_id
    ).first()

    if usuario_db is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    if usuario.tipo.casefold() == "participante" and usuario.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode consultar seu próprio cadastro."
        )

    return usuario_db


@router.post("/usuarios", status_code=201)
def criar_usuario(
    dados: Usuario,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Organizador"))
):
    if dados.tipo.strip().casefold() not in ("participante", "organizador"):
        raise HTTPException(
            status_code=400,
            detail="Perfil de usuário inválido."
        )

    existente = db.query(UsuarioDB).filter(
        UsuarioDB.email == dados.email
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com este e-mail."
        )

    novo_usuario = UsuarioDB(
        nome=dados.nome,
        email=dados.email,
        tipo=dados.tipo.strip().capitalize(),
        senha_hash=None
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Usuário criado com sucesso!",
        "usuario": novo_usuario
    }


@router.put("/usuarios/{usuario_id}")
def atualizar_usuario(
    usuario_id: int,
    dados: Usuario,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Organizador"))
):
    usuario_db = db.query(UsuarioDB).filter(
        UsuarioDB.id == usuario_id
    ).first()

    if usuario_db is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    if usuario_db.id == usuario.id and dados.tipo.casefold() != usuario_db.tipo.casefold():
        raise HTTPException(
            status_code=403,
            detail="Não é permitido alterar o próprio perfil."
        )

    email_existente = db.query(UsuarioDB).filter(
        UsuarioDB.email == dados.email,
        UsuarioDB.id != usuario_id
    ).first()

    if email_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro usuário com este e-mail."
        )

    if dados.tipo.strip().casefold() not in ("participante", "organizador"):
        raise HTTPException(
            status_code=400,
            detail="Perfil de usuário inválido."
        )

    usuario_db.nome = dados.nome
    usuario_db.email = dados.email
    usuario_db.tipo = dados.tipo.strip().capitalize()

    db.commit()
    db.refresh(usuario_db)

    return {
        "mensagem": "Usuário atualizado com sucesso!",
        "usuario": usuario_db
    }


@router.delete("/usuarios/{usuario_id}")
def excluir_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Organizador"))
):
    if usuario_id == usuario.id:
        raise HTTPException(
            status_code=403,
            detail="Não é permitido excluir o próprio usuário."
        )

    usuario_db = db.query(UsuarioDB).filter(
        UsuarioDB.id == usuario_id
    ).first()

    if usuario_db is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    inscricoes = db.query(InscricaoDB).filter(
        InscricaoDB.usuario_id == usuario_id
    ).count()

    if inscricoes > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir um usuário que possui inscrições."
        )

    db.delete(usuario_db)
    db.commit()

    return {"mensagem": "Usuário excluído com sucesso!"}
