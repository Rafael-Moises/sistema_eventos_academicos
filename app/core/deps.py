from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from app.database.database import SessionLocal
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.models.db_models import UsuarioDB

bearer_scheme = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> UsuarioDB:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente, inválido ou expirado.", headers={"WWW-Authenticate": "Bearer"})
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub", ""))
    except (InvalidTokenError, ValueError, TypeError):
        raise unauthorized
    user = db.query(UsuarioDB).filter(UsuarioDB.id == user_id).first()
    if user is None:
        raise unauthorized
    return user
