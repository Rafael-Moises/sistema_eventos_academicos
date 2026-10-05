from fastapi import FastAPI, HTTPException, Depends
from model import Evento, Categoria, Usuario, Inscricao, Certificado, Organizador
from sqlalchemy.orm import Session
from database import SessionLocal
from db_models import EventoDB, CategoriaDB, UsuarioDB, InscricaoDB, CertificadoDB, OrganizadorDB
from datetime import date

app = FastAPI(
    title="Sistema de Gestão de Eventos Acadêmicos",
    description="API para gerenciamento de eventos acadêmicos, inscrições, certificados e organizadores.",
    version="1.0.0"
)

# CONEXÃO COM O BANCO

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mensagem de inicio

@app.get("/")
def inicio():
    return {"mensagem": "API do Sistema de Gestão de Eventos Acadêmicos em funcionamento!"}

# Classe de Eventos

@app.get("/eventos")
def listar_eventos(db: Session = Depends(get_db)):
    eventos_db = db.query(EventoDB).all()
    return eventos_db

@app.post("/eventos", status_code=201)
def criar_evento(evento: Evento, db: Session = Depends(get_db)):
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id == evento.categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    organizador = db.query(OrganizadorDB).filter(OrganizadorDB.id == evento.organizador_id).first()
    if organizador is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    if evento.vagas <= 0:
        raise HTTPException(status_code=400, detail="O número de vagas deve ser maior que zero.")
    try:
        data_evento = date.fromisoformat(evento.data)
    except ValueError:
        raise HTTPException(status_code=400, detail="A data deve estar no formato AAAA-MM-DD.")
    if data_evento < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido cadastrar evento com data passada.")
    novo_evento = (EventoDB
        (titulo=evento.titulo,
        descricao=evento.descricao,
        data=evento.data,
        horario=evento.horario,
        local=evento.local,
        categoria_id=evento.categoria_id,
        organizador_id=evento.organizador_id,
        vagas=evento.vagas))
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)
    return {"mensagem": "Evento criado com sucesso!", "evento": novo_evento}

@app.get("/eventos/{evento_id}")
def buscar_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(EventoDB).filter( EventoDB.id == evento_id).first()
    if evento is None:
        raise HTTPException( status_code=404, detail="Evento não encontrado.")
    return evento

@app.put("/eventos/{evento_id}")
def atualizar_evento(evento_id: int, evento: Evento, db: Session = Depends(get_db)):
    evento_db = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if evento_db is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    if evento.vagas <= 0:
        raise HTTPException(status_code=400, detail="O número de vagas deve ser maior que zero.")
    inscricoes_ativas = db.query(InscricaoDB).filter(InscricaoDB.evento_id == evento_id, InscricaoDB.status.in_(["Pendente", "Confirmada"])).count()
    if evento.vagas < inscricoes_ativas:
        raise HTTPException(status_code=400, detail="O número de vagas não pode ser menor que a quantidade de inscrições ativas.")
    try:
        data_evento = date.fromisoformat(evento.data)
    except ValueError:
        raise HTTPException(status_code=400, detail="A data deve estar no formato AAAA-MM-DD.")
    if data_evento < date.today():
        raise HTTPException(status_code=400, detail="Não é permitido atualizar evento para uma data passada.")
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id == evento.categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    organizador = db.query(OrganizadorDB).filter(
        OrganizadorDB.id == evento.organizador_id).first()
    if organizador is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    evento_db.titulo = evento.titulo
    evento_db.descricao = evento.descricao
    evento_db.data = evento.data
    evento_db.horario = evento.horario
    evento_db.local = evento.local
    evento_db.categoria_id = evento.categoria_id
    evento_db.organizador_id = evento.organizador_id
    evento_db.vagas = evento.vagas
    db.commit()
    db.refresh(evento_db)
    return {"mensagem": "Evento atualizado com sucesso!", "evento": evento_db}

@app.delete("/eventos/{evento_id}")
def excluir_evento(evento_id: int, db: Session = Depends(get_db)):
    evento_db = db.query(EventoDB).filter(EventoDB.id == evento_id).first()
    if evento_db is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    inscricoes = db.query(InscricaoDB).filter(InscricaoDB.evento_id == evento_id).count()
    if inscricoes > 0:
        raise HTTPException(status_code=400, detail="Não é possível excluir um evento que possui inscrições.")
    db.delete(evento_db)
    db.commit()
    return {"mensagem": "Evento excluído com sucesso!"}

# Classe de Categoria

@app.get("/categorias")
def listar_categorias(
    db: Session = Depends(get_db)):
    categorias_db = db.query(CategoriaDB).all()
    return categorias_db

@app.post("/categorias", status_code=201)
def criar_categoria(categoria: Categoria, db: Session = Depends(get_db)):
    categoria_existente = db.query(CategoriaDB).filter(CategoriaDB.nome == categoria.nome).first()
    if categoria_existente:
        raise HTTPException(status_code=400, detail="Já existe uma categoria com este nome.")
    nova_categoria = CategoriaDB(nome=categoria.nome)
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return {"mensagem": "Categoria criada com sucesso!", "categoria": nova_categoria}

@app.put("/categorias/{categoria_id}")
def atualizar_categoria(categoria_id: int, categoria: Categoria, db: Session = Depends(get_db)):
    categoria_db = db.query(CategoriaDB).filter(CategoriaDB.id == categoria_id).first()
    if categoria_db is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    categoria_existente = db.query(CategoriaDB).filter(CategoriaDB.nome == categoria.nome, CategoriaDB.id != categoria_id).first()
    if categoria_existente:
        raise HTTPException(status_code=400, detail="Já existe outra categoria com este nome.")
    categoria_db.nome = categoria.nome
    db.commit()
    db.refresh(categoria_db)
    return {"mensagem": "Categoria atualizada com sucesso!", "categoria": categoria_db}

@app.delete("/categorias/{categoria_id}")
def excluir_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria_db = db.query(CategoriaDB).filter(CategoriaDB.id == categoria_id).first()
    if categoria_db is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    eventos = db.query(EventoDB).filter(EventoDB.categoria_id == categoria_id).count()
    if eventos > 0:
        raise HTTPException(status_code=400, detail="Não é possível excluir uma categoria que está vinculada a eventos.")
    db.delete(categoria_db)
    db.commit()
    return {"mensagem": "Categoria excluída com sucesso!"}

# Classe de Usuario

@app.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios_db = db.query(UsuarioDB).all()
    return usuarios_db

@app.get("/usuarios/{usuario_id}")
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario_db = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if usuario_db is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return usuario_db

@app.post("/usuarios", status_code=201)
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

@app.put("/usuarios/{usuario_id}")
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

@app.delete("/usuarios/{usuario_id}")
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

# Classes de Inscrição

@app.get("/inscricoes")
def listar_inscricoes(db: Session = Depends(get_db)):
    inscricoes_db = db.query(InscricaoDB).all()
    return inscricoes_db

@app.get("/inscricoes/{inscricao_id}")
def buscar_inscricao(inscricao_id: int, db: Session = Depends(get_db)):
    inscricao_db = db.query(InscricaoDB).filter(InscricaoDB.id == inscricao_id).first()
    if inscricao_db is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    return inscricao_db

@app.post("/inscricoes", status_code=201)
def criar_inscricao(inscricao: Inscricao, db: Session = Depends(get_db)):
    status_validos = ["Pendente", "Confirmada", "Cancelada"]
    if inscricao.status not in status_validos:
        raise HTTPException(status_code=400, detail="Status inválido. Use Pendente, Confirmada ou Cancelada.")
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == inscricao.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    evento = db.query(EventoDB).filter(EventoDB.id == inscricao.evento_id).first()
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    total_inscricoes = db.query(InscricaoDB).filter(InscricaoDB.evento_id == inscricao.evento_id, InscricaoDB.status.in_(["Pendente", "Confirmada"])).count()
    if total_inscricoes >= evento.vagas:
        raise HTTPException(status_code=400, detail="O evento já atingiu o limite de vagas.")
    inscricao_existente = db.query(InscricaoDB).filter(InscricaoDB.usuario_id == inscricao.usuario_id, InscricaoDB.evento_id == inscricao.evento_id).first()
    if inscricao_existente:
        raise HTTPException(status_code=400, detail="Este usuário já está inscrito neste evento.")
    nova_inscricao = InscricaoDB(
        usuario_id=inscricao.usuario_id,
        evento_id=inscricao.evento_id,
        status=inscricao.status)
    db.add(nova_inscricao)
    db.commit()
    db.refresh(nova_inscricao)
    return {"mensagem": "Inscrição criada com sucesso!", "inscricao": nova_inscricao}

@app.put("/inscricoes/{inscricao_id}")
def atualizar_inscricao(inscricao_id: int, inscricao: Inscricao, db: Session = Depends(get_db)):
    status_validos = ["Pendente", "Confirmada", "Cancelada"]
    if inscricao.status not in status_validos:
        raise HTTPException(status_code=400, detail="Status inválido. Use Pendente, Confirmada ou Cancelada.")
    inscricao_db = db.query(InscricaoDB).filter(InscricaoDB.id == inscricao_id).first()
    if inscricao_db is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == inscricao.usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    evento = db.query(EventoDB).filter(EventoDB.id == inscricao.evento_id).first()
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    if inscricao_db.evento_id != inscricao.evento_id:
        total_inscricoes = db.query(InscricaoDB).filter(InscricaoDB.evento_id == inscricao.evento_id, InscricaoDB.status.in_(["Pendente", "Confirmada"])).count()
        if total_inscricoes >= evento.vagas:
            raise HTTPException(status_code=400, detail="O evento já atingiu o limite de vagas.")
        inscricao_existente = db.query(InscricaoDB).filter(InscricaoDB.usuario_id == inscricao.usuario_id, InscricaoDB.evento_id == inscricao.evento_id, InscricaoDB.id != inscricao_id).first()
        if inscricao_existente:
            raise HTTPException(status_code=400, detail="Este usuário já está inscrito neste evento.")
    inscricao_db.usuario_id = inscricao.usuario_id
    inscricao_db.evento_id = inscricao.evento_id
    inscricao_db.status = inscricao.status
    db.commit()
    db.refresh(inscricao_db)
    return {"mensagem": "Inscrição atualizada com sucesso!", "inscricao": inscricao_db}

@app.delete("/inscricoes/{inscricao_id}")
def excluir_inscricao(inscricao_id: int, db: Session = Depends(get_db)):
    inscricao_db = db.query(InscricaoDB).filter(InscricaoDB.id == inscricao_id).first()
    if inscricao_db is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    certificado = db.query(CertificadoDB).filter(CertificadoDB.inscricao_id == inscricao_id).first()
    if certificado is not None:
        raise HTTPException(status_code=400, detail="Não é possível excluir uma inscrição que possui certificado.")
    db.delete(inscricao_db)
    db.commit()
    return {"mensagem": "Inscrição excluída com sucesso!"}

# Classe de Certificados

@app.get("/certificados")
def listar_certificados(db: Session = Depends(get_db)):
    certificados_db = db.query(CertificadoDB).all()
    return certificados_db

@app.get("/certificados/{certificado_id}")
def buscar_certificado(certificado_id: int, db: Session = Depends(get_db)):
    certificado_db = db.query(CertificadoDB).filter(CertificadoDB.id == certificado_id).first()
    if certificado_db is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado.")
    return certificado_db

@app.post("/certificados", status_code=201)
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

@app.put("/certificados/{certificado_id}")
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

@app.delete("/certificados/{certificado_id}")
def excluir_certificado(certificado_id: int, db: Session = Depends(get_db)):
    certificado_db = db.query(CertificadoDB).filter(CertificadoDB.id == certificado_id).first()
    if certificado_db is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado.")
    db.delete(certificado_db)
    db.commit()
    return {"mensagem": "Certificado excluído com sucesso!"}

# Classe de Organizadores

@app.get("/organizadores")
def listar_organizadores(db: Session = Depends(get_db)):
    organizadores_db = db.query(OrganizadorDB).all()
    return organizadores_db

@app.get("/organizadores/{organizador_id}")
def buscar_organizador(organizador_id: int, db: Session = Depends(get_db)):
    organizador_db = db.query(OrganizadorDB).filter(OrganizadorDB.id == organizador_id).first()
    if organizador_db is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    return organizador_db

@app.post("/organizadores", status_code=201)
def criar_organizador(organizador: Organizador, db: Session = Depends(get_db)):
    organizador_existente = db.query(OrganizadorDB).filter(OrganizadorDB.email == organizador.email).first()
    if organizador_existente:
        raise HTTPException(status_code=400, detail="Já existe um organizador com este e-mail.")
    novo_organizador = OrganizadorDB(nome=organizador.nome, email=organizador.email, tipo=organizador.tipo)
    db.add(novo_organizador)
    db.commit()
    db.refresh(novo_organizador)
    return {"mensagem": "Organizador criado com sucesso!", "organizador": novo_organizador}

@app.put("/organizadores/{organizador_id}")
def atualizar_organizador(organizador_id: int, organizador: Organizador, db: Session = Depends(get_db)):
    organizador_db = db.query(OrganizadorDB).filter(OrganizadorDB.id == organizador_id).first()
    if organizador_db is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    email_existente = db.query(OrganizadorDB).filter(OrganizadorDB.email == organizador.email, OrganizadorDB.id != organizador_id).first()
    if email_existente:
        raise HTTPException(status_code=400, detail="Já existe outro organizador com este e-mail.")
    organizador_db.nome = organizador.nome
    organizador_db.email = organizador.email
    organizador_db.tipo = organizador.tipo
    db.commit()
    db.refresh(organizador_db)
    return {"mensagem": "Organizador atualizado com sucesso!", "organizador": organizador_db}

@app.delete("/organizadores/{organizador_id}")
def excluir_organizador(organizador_id: int, db: Session = Depends(get_db)):
    organizador_db = db.query(OrganizadorDB).filter(OrganizadorDB.id == organizador_id).first()
    if organizador_db is None:
        raise HTTPException(status_code=404, detail="Organizador não encontrado.")
    eventos = db.query(EventoDB).filter(EventoDB.organizador_id == organizador_id).count()
    if eventos > 0:
        raise HTTPException(status_code=400, detail="Não é possível excluir um organizador que está vinculado a eventos.")
    db.delete(organizador_db)
    db.commit()
    return {"mensagem": "Organizador excluído com sucesso!"}