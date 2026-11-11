
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import exigir_perfis
from app.models.db_models import CategoriaDB, EventoDB
from app.schemas.model import Categoria

router = APIRouter(tags=["Categorias"])


@router.get("/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(CategoriaDB).all()


@router.post("/categorias", status_code=201)
def criar_categoria(
    categoria: Categoria,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Organizador"))
):
    categoria_existente = db.query(CategoriaDB).filter(
        CategoriaDB.nome == categoria.nome
    ).first()

    if categoria_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma categoria com este nome."
        )

    nova_categoria = CategoriaDB(nome=categoria.nome)
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)

    return {
        "mensagem": "Categoria criada com sucesso!",
        "categoria": nova_categoria
    }


@router.put("/categorias/{categoria_id}")
def atualizar_categoria(
    categoria_id: int,
    categoria: Categoria,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Organizador"))
):
    categoria_db = db.query(CategoriaDB).filter(
        CategoriaDB.id == categoria_id
    ).first()

    if categoria_db is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada."
        )

    categoria_existente = db.query(CategoriaDB).filter(
        CategoriaDB.nome == categoria.nome,
        CategoriaDB.id != categoria_id
    ).first()

    if categoria_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe outra categoria com este nome."
        )

    categoria_db.nome = categoria.nome
    db.commit()
    db.refresh(categoria_db)

    return {
        "mensagem": "Categoria atualizada com sucesso!",
        "categoria": categoria_db
    }


@router.delete("/categorias/{categoria_id}")
def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_perfis("Organizador"))
):
    categoria_db = db.query(CategoriaDB).filter(
        CategoriaDB.id == categoria_id
    ).first()

    if categoria_db is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada."
        )

    eventos = db.query(EventoDB).filter(
        EventoDB.categoria_id == categoria_id
    ).count()

    if eventos > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir uma categoria que está vinculada a eventos."
        )

    db.delete(categoria_db)
    db.commit()

    return {"mensagem": "Categoria excluída com sucesso!"}
