
from app.database.database import Base, engine
from app.models import db_models


def inicializar_banco():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    inicializar_banco()
