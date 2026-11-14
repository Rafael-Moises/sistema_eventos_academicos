
from datetime import date

from app.models.db_models import (
    UsuarioDB,
    EventoDB,
    OrganizadorDB,
    InscricaoDB,
    CertificadoDB
)


def obter_token(client, email, senha):
    resposta = client.post(
        "/auth/login",
        json={"email": email, "senha": senha}
    )
    return resposta.json()["access_token"]


def obter_token_organizador(client):
    return obter_token(
        client,
        "admin.teste@example.com",
        "Admin123!"
    )


def obter_token_participante(client):
    return obter_token(
        client,
        "participante@example.com",
        "Senha123!"
    )


def dados_evento_validos(**alteracoes):
    dados = {
        "titulo": "Novo Evento de Tecnologia",
        "descricao": "Evento criado para testar as regras da API.",
        "data": "2099-12-10",
        "horario": "14:00",
        "local": "Auditorio Principal",
        "categoria_id": 1,
        "organizador_id": 1,
        "vagas": 50
    }
    dados.update(alteracoes)
    return dados


def criar_inscricao_confirmada(db_session):
    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()

    inscricao = InscricaoDB(
        usuario_id=usuario.id,
        evento_id=evento.id,
        status="Confirmada"
    )

    db_session.add(inscricao)
    db_session.commit()
    db_session.refresh(inscricao)

    return inscricao


def criar_certificado(db_session, inscricao, codigo):
    certificado = CertificadoDB(
        inscricao_id=inscricao.id,
        codigo=codigo,
        data_emissao=date.today().isoformat()
    )

    db_session.add(certificado)
    db_session.commit()
    db_session.refresh(certificado)

    return certificado


# ==========================================
# TESTES DE AUTENTICACAO E ACESSO
# ==========================================

def test_acessar_me_sem_token(client):
    resposta = client.get("/me")
    assert resposta.status_code == 401


def test_acessar_me_com_token_valido(client):
    token = obter_token_participante(client)

    resposta = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 200


# ==========================================
# TESTES DE INSCRICOES
# ==========================================

def test_criar_inscricao_com_sucesso(client, db_session):
    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()
    token = obter_token_participante(client)

    resposta = client.post(
        "/inscricoes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": usuario.id,
            "evento_id": evento.id,
            "status": "Pendente"
        }
    )

    assert resposta.status_code == 201
    assert resposta.json()["inscricao"]["status"] == "Pendente"


def test_impedir_inscricao_em_nome_de_outro_usuario(
    client,
    db_session
):
    outro_usuario = db_session.query(UsuarioDB).filter_by(
        email="admin.teste@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()
    token = obter_token_participante(client)

    resposta = client.post(
        "/inscricoes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": outro_usuario.id,
            "evento_id": evento.id,
            "status": "Pendente"
        }
    )

    assert resposta.status_code == 403


def test_impedir_inscricao_em_evento_inexistente(
    client,
    db_session
):
    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    token = obter_token_participante(client)

    resposta = client.post(
        "/inscricoes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": usuario.id,
            "evento_id": 999999,
            "status": "Pendente"
        }
    )

    assert resposta.status_code == 404


def test_impedir_inscricao_duplicada(client, db_session):
    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()
    token = obter_token_participante(client)

    dados = {
        "usuario_id": usuario.id,
        "evento_id": evento.id,
        "status": "Pendente"
    }

    headers = {"Authorization": f"Bearer {token}"}

    primeira = client.post(
        "/inscricoes",
        headers=headers,
        json=dados
    )

    segunda = client.post(
        "/inscricoes",
        headers=headers,
        json=dados
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 400


def test_consultar_inscricao_inexistente(client):
    token = obter_token_participante(client)

    resposta = client.get(
        "/inscricoes/999999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 404


def test_cancelar_propria_inscricao(client, db_session):
    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()
    token = obter_token_participante(client)

    headers = {"Authorization": f"Bearer {token}"}

    criacao = client.post(
        "/inscricoes",
        headers=headers,
        json={
            "usuario_id": usuario.id,
            "evento_id": evento.id,
            "status": "Pendente"
        }
    )

    inscricao_id = criacao.json()["inscricao"]["id"]

    cancelamento = client.put(
        f"/inscricoes/{inscricao_id}",
        headers=headers,
        json={
            "usuario_id": usuario.id,
            "evento_id": evento.id,
            "status": "Cancelada"
        }
    )

    assert criacao.status_code == 201
    assert cancelamento.status_code == 200
    assert cancelamento.json()["inscricao"]["status"] == "Cancelada"


# ==========================================
# TESTES DE EVENTOS
# ==========================================

def test_organizador_pode_criar_evento(client):
    token = obter_token_organizador(client)

    resposta = client.post(
        "/eventos",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_evento_validos()
    )

    assert resposta.status_code == 201
    assert resposta.json()["evento"]["titulo"] == "Novo Evento de Tecnologia"


def test_impedir_evento_com_zero_vagas(client):
    token = obter_token_organizador(client)

    resposta = client.post(
        "/eventos",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_evento_validos(vagas=0)
    )

    assert resposta.status_code == 422


def test_impedir_evento_com_horario_invalido(client):
    token = obter_token_organizador(client)

    resposta = client.post(
        "/eventos",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_evento_validos(horario="25:90")
    )

    assert resposta.status_code == 422


def test_impedir_evento_com_categoria_inexistente(client):
    token = obter_token_organizador(client)

    resposta = client.post(
        "/eventos",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_evento_validos(categoria_id=999999)
    )

    assert resposta.status_code == 404


def test_impedir_evento_com_data_passada(client):
    token = obter_token_organizador(client)

    resposta = client.post(
        "/eventos",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_evento_validos(data="2020-01-01")
    )

    assert resposta.status_code == 400


def test_impedir_organizador_de_criar_evento_para_outro(
    client,
    db_session
):
    outro_organizador = OrganizadorDB(
        nome="Outro Organizador",
        email="outro@example.com",
        tipo="Organizador"
    )

    db_session.add(outro_organizador)
    db_session.commit()
    db_session.refresh(outro_organizador)

    token = obter_token_organizador(client)

    resposta = client.post(
        "/eventos",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_evento_validos(
            organizador_id=outro_organizador.id
        )
    )

    assert resposta.status_code == 403


def test_impedir_reducao_de_vagas_abaixo_das_inscricoes_ativas(
    client,
    db_session
):
    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()

    db_session.add_all([
        InscricaoDB(
            usuario_id=usuario.id,
            evento_id=evento.id,
            status="Pendente"
        ),
        InscricaoDB(
            usuario_id=usuario.id,
            evento_id=evento.id,
            status="Confirmada"
        )
    ])

    db_session.commit()
    token = obter_token_organizador(client)

    resposta = client.put(
        f"/eventos/{evento.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_evento_validos(vagas=1)
    )

    assert resposta.status_code == 400


# ==========================================
# TESTES DE CERTIFICADOS
# ==========================================

def test_organizador_pode_emitir_certificado(client, db_session):
    inscricao = criar_inscricao_confirmada(db_session)
    token = obter_token_organizador(client)

    resposta = client.post(
        "/certificados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": inscricao.id,
            "codigo": "CERT-TESTE-001",
            "data_emissao": date.today().isoformat()
        }
    )

    assert resposta.status_code == 201
    assert resposta.json()["certificado"]["codigo"] == "CERT-TESTE-001"


def test_impedir_certificado_para_inscricao_pendente(
    client,
    db_session
):
    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()

    inscricao = InscricaoDB(
        usuario_id=usuario.id,
        evento_id=evento.id,
        status="Pendente"
    )

    db_session.add(inscricao)
    db_session.commit()
    db_session.refresh(inscricao)

    token = obter_token_organizador(client)

    resposta = client.post(
        "/certificados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": inscricao.id,
            "codigo": "CERT-PENDENTE",
            "data_emissao": date.today().isoformat()
        }
    )

    assert resposta.status_code == 400


def test_impedir_certificado_com_data_futura(client, db_session):
    inscricao = criar_inscricao_confirmada(db_session)
    token = obter_token_organizador(client)

    resposta = client.post(
        "/certificados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": inscricao.id,
            "codigo": "CERT-FUTURO",
            "data_emissao": "2099-12-10"
        }
    )

    assert resposta.status_code == 400


def test_impedir_certificado_com_inscricao_inexistente(client):
    token = obter_token_organizador(client)

    resposta = client.post(
        "/certificados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": 999999,
            "codigo": "CERT-INEXISTENTE",
            "data_emissao": date.today().isoformat()
        }
    )

    assert resposta.status_code == 404


def test_impedir_emissao_de_certificado_duplicado(
    client,
    db_session
):
    inscricao = criar_inscricao_confirmada(db_session)
    token = obter_token_organizador(client)

    headers = {"Authorization": f"Bearer {token}"}

    dados = {
        "inscricao_id": inscricao.id,
        "codigo": "CERT-DUPLICADO",
        "data_emissao": date.today().isoformat()
    }

    primeira = client.post(
        "/certificados",
        headers=headers,
        json=dados
    )

    segunda = client.post(
        "/certificados",
        headers=headers,
        json={
            **dados,
            "codigo": "CERT-DUPLICADO-2"
        }
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 400


def test_participante_nao_pode_emitir_certificado(
    client,
    db_session
):
    inscricao = criar_inscricao_confirmada(db_session)
    token = obter_token_participante(client)

    resposta = client.post(
        "/certificados",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": inscricao.id,
            "codigo": "CERT-SEM-PERMISSAO",
            "data_emissao": date.today().isoformat()
        }
    )

    assert resposta.status_code == 403


def test_participante_pode_consultar_proprio_certificado(
    client,
    db_session
):
    inscricao = criar_inscricao_confirmada(db_session)

    certificado = criar_certificado(
        db_session,
        inscricao,
        "CERT-CONSULTA"
    )

    token = obter_token_participante(client)

    resposta = client.get(
        f"/certificados/{certificado.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 200
    assert resposta.json()["codigo"] == "CERT-CONSULTA"


def test_impedir_participante_de_consultar_certificado_de_outro(
    client,
    db_session
):
    inscricao = criar_inscricao_confirmada(db_session)

    outro_usuario = UsuarioDB(
        nome="Outro Participante",
        email="outro.participante@example.com",
        tipo="Participante",
        senha_hash=None
    )

    db_session.add(outro_usuario)
    db_session.commit()
    db_session.refresh(outro_usuario)

    inscricao_outro = InscricaoDB(
        usuario_id=outro_usuario.id,
        evento_id=inscricao.evento_id,
        status="Confirmada"
    )

    db_session.add(inscricao_outro)
    db_session.commit()
    db_session.refresh(inscricao_outro)

    certificado = criar_certificado(
        db_session,
        inscricao_outro,
        "CERT-OUTRO"
    )

    token = obter_token_participante(client)

    resposta = client.get(
        f"/certificados/{certificado.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 403


def test_organizador_pode_atualizar_certificado(
    client,
    db_session
):
    inscricao = criar_inscricao_confirmada(db_session)

    certificado = criar_certificado(
        db_session,
        inscricao,
        "CERT-ANTES"
    )

    token = obter_token_organizador(client)

    resposta = client.put(
        f"/certificados/{certificado.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": inscricao.id,
            "codigo": "CERT-ATUALIZADO",
            "data_emissao": date.today().isoformat()
        }
    )

    assert resposta.status_code == 200
    assert resposta.json()["certificado"]["codigo"] == "CERT-ATUALIZADO"


def test_organizador_pode_excluir_certificado(
    client,
    db_session
):
    inscricao = criar_inscricao_confirmada(db_session)

    certificado = criar_certificado(
        db_session,
        inscricao,
        "CERT-EXCLUIR"
    )

    token = obter_token_organizador(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta = client.delete(
        f"/certificados/{certificado.id}",
        headers=headers
    )

    consulta = client.get(
        f"/certificados/{certificado.id}",
        headers=headers
    )

    assert resposta.status_code == 200
    assert consulta.status_code == 404


def test_impedir_atualizacao_para_inscricao_pendente(
    client,
    db_session
):
    inscricao_confirmada = criar_inscricao_confirmada(db_session)

    certificado = criar_certificado(
        db_session,
        inscricao_confirmada,
        "CERT-VALIDO"
    )

    usuario = db_session.query(UsuarioDB).filter_by(
        email="participante@example.com"
    ).first()

    evento = db_session.query(EventoDB).first()

    inscricao_pendente = InscricaoDB(
        usuario_id=usuario.id,
        evento_id=evento.id,
        status="Pendente"
    )

    db_session.add(inscricao_pendente)
    db_session.commit()
    db_session.refresh(inscricao_pendente)

    token = obter_token_organizador(client)

    resposta = client.put(
        f"/certificados/{certificado.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": inscricao_pendente.id,
            "codigo": "CERT-NOVO",
            "data_emissao": date.today().isoformat()
        }
    )

    assert resposta.status_code == 400


def test_impedir_atualizacao_com_codigo_ja_utilizado(
    client,
    db_session
):
    primeira_inscricao = criar_inscricao_confirmada(db_session)
    segunda_inscricao = criar_inscricao_confirmada(db_session)

    primeiro_certificado = criar_certificado(
        db_session,
        primeira_inscricao,
        "CERT-PRIMEIRO"
    )

    criar_certificado(
        db_session,
        segunda_inscricao,
        "CERT-SEGUNDO"
    )

    token = obter_token_organizador(client)

    resposta = client.put(
        f"/certificados/{primeiro_certificado.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "inscricao_id": primeira_inscricao.id,
            "codigo": "CERT-SEGUNDO",
            "data_emissao": date.today().isoformat()
        }
    )

    assert resposta.status_code == 400
