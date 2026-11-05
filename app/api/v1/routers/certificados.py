from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.db_models import EventoDB, CategoriaDB, UsuarioDB, InscricaoDB, CertificadoDB, OrganizadorDB
from app.schemas.model import Evento, Categoria, Usuario, Inscricao, Certificado, Organizador

router = APIRouter(tags=["Certificados"])

@router.get('/certificados')
def listar_certificados(db: Session = Depends(get_db)):
    certificados_db = db.query(CertificadoDB).all()
    return certificados_db

@router.get('/certificados/{certificado_id}')
def buscar_certificado(certificado_id: int, db: Session = Depends(get_db)):
    certificado_db = db.query(CertificadoDB).filter(CertificadoDB.id == certificado_id).first()
    if certificado_db is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado.")
    return certificado_db

@router.post('/certificados', status_code=201)
def criar_certificado(certificado: Certificado, db: Session = Depends(get_db)):
    inscricao = db.query(InscricaoDB).filter(InscricaoDB.id == certificado.inscricao_id).first()
    if inscricao is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    if inscricao.status != "Confirmada":
        raise HTTPException(status_code=400, detail="O certificado só pode ser emitido para uma inscrição confirmada.")
    try:
        data_emissao = date.fromisoformat(certificado.data_emissao)
    except ValueError:
        raise HTTPException(status_code=400, detail="A data de emissão deve estar no formato AAAA-MM-DD.")
    if data_emissao > date.today():
        raise HTTPException(status_code=400, detail="A data de emissão não pode ser futura.")
    certificado_existente = db.query(CertificadoDB).filter(CertificadoDB.inscricao_id == certificado.inscricao_id).first()
    if certificado_existente:
        raise HTTPException(status_code=400, detail="Já existe um certificado para esta inscrição.")
    novo_certificado = CertificadoDB(
        inscricao_id=certificado.inscricao_id,
        codigo=certificado.codigo,
        data_emissao=certificado.data_emissao
    )
    db.add(novo_certificado)
    db.commit()
    db.refresh(novo_certificado)
    return {"mensagem": "Certificado emitido com sucesso!", "certificado": novo_certificado}


@router.put('/certificados/{certificado_id}')
def atualizar_certificado(certificado_id: int, certificado: Certificado, db: Session = Depends(get_db)):
    certificado_db = db.query(CertificadoDB).filter(CertificadoDB.id == certificado_id).first()
    if certificado_db is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado.")
    inscricao = db.query(InscricaoDB).filter(InscricaoDB.id == certificado.inscricao_id).first()
    if inscricao is None:
        raise HTTPException(
            status_code=404, detail="Inscrição não encontrada.")
    if inscricao.status != "Confirmada":
        raise HTTPException(status_code=400, detail="O certificado só pode ser associado a uma inscrição confirmada.")
    certificado_outro = db.query(CertificadoDB).filter(CertificadoDB.inscricao_id == certificado.inscricao_id, CertificadoDB.id != certificado_id).first()
    if certificado_outro:
        raise HTTPException(
            status_code=400, detail="Já existe outro certificado para esta inscrição.")
    codigo_existente = db.query(CertificadoDB).filter(CertificadoDB.codigo == certificado.codigo, CertificadoDB.id != certificado_id).first()
    if codigo_existente:
        raise HTTPException(status_code=400, detail="Já existe outro certificado com este código.")
    certificado_db.inscricao_id = certificado.inscricao_id
    certificado_db.codigo = certificado.codigo
    certificado_db.data_emissao = certificado.data_emissao
    db.commit()
    db.refresh(certificado_db)
    return {"mensagem": "Certificado atualizado com sucesso!", "certificado": certificado_db}

@router.delete('/certificados/{certificado_id}')
def excluir_certificado(certificado_id: int, db: Session = Depends(get_db)):
    certificado_db = db.query(CertificadoDB).filter(CertificadoDB.id == certificado_id).first()
    if certificado_db is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado.")
    db.delete(certificado_db)
    db.commit()
    return {"mensagem": "Certificado excluído com sucesso!"}
