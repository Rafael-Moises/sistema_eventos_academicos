
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base
from app.core.deps import get_db
from app.core.security import hash_password
from app.models.db_models import (
    UsuarioDB,
    CategoriaDB,
    OrganizadorDB,
    EventoDB
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    db = TestingSessionLocal()

    categoria = CategoriaDB(nome="Tecnologia")

    organizador = OrganizadorDB(
        nome="Organizador Teste",
        email="admin.teste@example.com",
        tipo="Organizador"
    )

    participante = UsuarioDB(
        nome="Participante Teste",
        email="participante@example.com",
        tipo="Participante",
        senha_hash=hash_password("Senha123!")
    )

    usuario_organizador = UsuarioDB(
        nome="Organizador Teste",
        email="admin.teste@example.com",
        tipo="Organizador",
        senha_hash=hash_password("Admin123!")
    )

    db.add_all([
        categoria,
        organizador,
        participante,
        usuario_organizador
    ])

    db.commit()

    evento = EventoDB(
        titulo="Evento de Teste",
        descricao="Evento utilizado nos testes automatizados",
        data="2026-12-10",
        horario="14:00",
        local="Sala de Testes",
        categoria_id=categoria.id,
        organizador_id=organizador.id,
        vagas=50
    )

    db.add(evento)
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
