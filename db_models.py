from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

# EVENTOS

class EventoDB(Base):
    __tablename__ = "eventos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[str] = mapped_column(String(10), nullable=False)
    horario: Mapped[str] = mapped_column(String(5), nullable=False)
    local: Mapped[str] = mapped_column(String(150), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    organizador_id: Mapped[int] = mapped_column(ForeignKey("organizadores.id"), nullable=False)
    vagas: Mapped[int] = mapped_column(Integer, nullable=False)


# CATEGORIAS

class CategoriaDB(Base):
    __tablename__ = "categorias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

# USUÁRIOS

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)

# INSCRIÇÕES

class InscricaoDB(Base):
    __tablename__ = "inscricoes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

# CERTIFICADOS

class CertificadoDB(Base):
    __tablename__ = "certificados"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inscricao_id: Mapped[int] = mapped_column(ForeignKey("inscricoes.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(100), nullable=False)
    data_emissao: Mapped[str] = mapped_column(String(10), nullable=False)

# ORGANIZADORES

class OrganizadorDB(Base):
    __tablename__ = "organizadores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)