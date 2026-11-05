from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.db_models import UsuarioDB
from app.schemas.model import UsuarioCadastro, LoginRequest

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def registrar_usuario(dados: UsuarioCadastro, db: Session = Depends(get_db)):
    existente = db.query(UsuarioDB).filter(UsuarioDB.email == dados.email).first()
    if existente:
        raise HTTPException(status_code=409, detail="Já existe um usuário com este e-mail.")
    usuario = UsuarioDB(nome=dados.nome, email=dados.email, tipo="Participante", senha_hash=hash_password(dados.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"mensagem": "Usuário cadastrado com sucesso!", "usuario": {"id": usuario.id, "nome": usuario.nome, "email": usuario.email, "tipo": usuario.tipo}}

@router.post("/login")
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == dados.email).first()
    if usuario is None or not usuario.senha_hash or not verify_password(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos.", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(usuario.id)
    return {"access_token": token, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}
