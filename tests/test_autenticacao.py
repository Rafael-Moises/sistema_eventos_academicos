
from app.models.db_models import UsuarioDB


def obter_token(client, email, senha):
    resposta = client.post(
        "/auth/login",
        json={
            "email": email,
            "senha": senha
        }
    )

    return resposta.json()["access_token"]


def test_cadastrar_usuario_com_sucesso(client):
    resposta = client.post(
        "/auth/register",
        json={
            "nome": "Novo Participante",
            "email": "novo@example.com",
            "senha": "Senha123!"
        }
    )

    assert resposta.status_code == 201
    assert resposta.json()["usuario"]["tipo"] == "Participante"


def test_impedir_cadastro_com_email_existente(client):
    resposta = client.post(
        "/auth/register",
        json={
            "nome": "Participante Duplicado",
            "email": "participante@example.com",
            "senha": "Senha123!"
        }
    )

    assert resposta.status_code == 409


def test_login_com_credenciais_validas(client):
    resposta = client.post(
        "/auth/login",
        json={
            "email": "participante@example.com",
            "senha": "Senha123!"
        }
    )

    assert resposta.status_code == 200
    assert "access_token" in resposta.json()
    assert resposta.json()["token_type"] == "bearer"


def test_login_com_senha_incorreta(client):
    resposta = client.post(
        "/auth/login",
        json={
            "email": "participante@example.com",
            "senha": "SenhaErrada123!"
        }
    )

    assert resposta.status_code == 401


def test_bloquear_acesso_sem_token(client):
    resposta = client.post(
        "/eventos",
        json={
            "titulo": "Novo Evento",
            "descricao": "Evento de teste",
            "data": "2026-12-15",
            "horario": "15:00",
            "local": "Auditório",
            "categoria_id": 1,
            "organizador_id": 1,
            "vagas": 30
        }
    )

    assert resposta.status_code == 401


def test_bloquear_acesso_com_token_invalido(client):
    resposta = client.post(
        "/eventos",
        headers={
            "Authorization": "Bearer token-invalido"
        },
        json={
            "titulo": "Novo Evento",
            "descricao": "Evento de teste",
            "data": "2026-12-15",
            "horario": "15:00",
            "local": "Auditório",
            "categoria_id": 1,
            "organizador_id": 1,
            "vagas": 30
        }
    )

    assert resposta.status_code == 401


def test_participante_nao_pode_criar_evento(client):
    token = obter_token(
        client,
        "participante@example.com",
        "Senha123!"
    )

    resposta = client.post(
        "/eventos",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "titulo": "Evento não autorizado",
            "descricao": "Teste de permissão",
            "data": "2026-12-15",
            "horario": "15:00",
            "local": "Auditório",
            "categoria_id": 1,
            "organizador_id": 1,
            "vagas": 30
        }
    )

    assert resposta.status_code == 403


def test_organizador_nao_pode_criar_inscricao(client):
    token = obter_token(
        client,
        "admin.teste@example.com",
        "Admin123!"
    )

    resposta = client.post(
        "/inscricoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "usuario_id": 1,
            "evento_id": 1,
            "status": "Pendente"
        }
    )

    assert resposta.status_code == 403


# TESTES DE AUTORIZAÇÃO E CONTROLE DE ACESSO


def test_participante_nao_pode_listar_todos_os_usuarios(
    client
):
    token = obter_token(
        client,
        "participante@example.com",
        "Senha123!"
    )

    resposta = client.get(
        "/usuarios",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert resposta.status_code == 403


def test_organizador_pode_listar_usuarios(client):
    token = obter_token(
        client,
        "admin.teste@example.com",
        "Admin123!"
    )

    resposta = client.get(
        "/usuarios",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert resposta.status_code == 200


def test_participante_pode_consultar_proprio_usuario(
    client,
    db_session
):
    participante = db_session.query(UsuarioDB).filter(
        UsuarioDB.email == "participante@example.com"
    ).first()

    token = obter_token(
        client,
        "participante@example.com",
        "Senha123!"
    )

    resposta = client.get(
        f"/usuarios/{participante.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert resposta.status_code == 200


def test_participante_nao_pode_consultar_outro_usuario(
    client,
    db_session
):
    outro_usuario = db_session.query(UsuarioDB).filter(
        UsuarioDB.email == "admin.teste@example.com"
    ).first()

    token = obter_token(
        client,
        "participante@example.com",
        "Senha123!"
    )

    resposta = client.get(
        f"/usuarios/{outro_usuario.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert resposta.status_code == 403


def test_listagem_de_eventos_sem_login(client):
    resposta = client.get("/eventos")

    assert resposta.status_code == 200


def test_listagem_de_categorias_sem_login(client):
    resposta = client.get("/categorias")

    assert resposta.status_code == 200
