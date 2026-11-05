from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.db_models import EventoDB, CategoriaDB, UsuarioDB, InscricaoDB, CertificadoDB, OrganizadorDB
from app.schemas.model import Evento, Categoria, Usuario, Inscricao, Certificado, Organizador

router = APIRouter(tags=["Usuarios"])

@router.get('/usuarios')
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios_db = db.query(UsuarioDB).all()
    return usuarios_db



@router.get("/me")
def usuario_atual(usuario: UsuarioDB = Depends(get_current_user)):
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email, "tipo": usuario.tipo}


@router.get('/usuarios/{usuario_id}')
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario_db = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if usuario_db is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return usuario_db

@router.post('/usuarios', status_code=201)
def criar_usuario(usuario: Usuario, db: Session = Depends(get_db)):
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Já existe um usuário com este e-mail.")
    novo_usuario = UsuarioDB(
        nome=usuario.nome,
        email=usuario.email,
        tipo=usuario.tipo
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"mensagem": "Usuário criado com sucesso!", "usuario": novo_usuario}

@router.put('/usuarios/{usuario_id}')
def atualizar_usuario(usuario_id: int, usuario: Usuario, db: Session = Depends(get_db)):
    usuario_db = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if usuario_db is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    usuario_email = db.query(UsuarioDB).filter( UsuarioDB.email == usuario.email, UsuarioDB.id != usuario_id).first()
    if usuario_email:
        raise HTTPException(status_code=400, detail="Já existe outro usuário com este e-mail.")
    usuario_db.nome = usuario.nome
    usuario_db.email = usuario.email
    usuario_db.tipo = usuario.tipo
    db.commit()
    db.refresh(usuario_db)
    return {"mensagem": "Usuário atualizado com sucesso!", "usuario": usuario_db}

@router.delete('/usuarios/{usuario_id}')
def excluir_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario_db = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if usuario_db is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    inscricoes = db.query(InscricaoDB).filter(InscricaoDB.usuario_id == usuario_id).count()
    if inscricoes > 0:
        raise HTTPException(status_code=400, detail="Não é possível excluir um usuário que possui inscrições.")
    db.delete(usuario_db)
    db.commit()
    return {"mensagem": "Usuário excluído com sucesso!"}
