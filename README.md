
# Sistema de Gestão de Eventos Acadêmicos

API REST desenvolvida com Python e FastAPI para gerenciamento de eventos acadêmicos, incluindo usuários, categorias, inscrições, certificados e organizadores, com autenticação JWT, autorização e regras de negócio.

## Equipe

- Rafael Moisés Ferreira Santiago
- Elizeu da Silva Joaquin
- Mayk Dias de Oliveira Magalhães
- Anderson trindade
- Jose rennan

## Objetivo

Centralizar o gerenciamento de eventos acadêmicos, permitindo cadastro, consulta, atualização e exclusão de informações, aplicação de regras de negócio, integração com PostgreSQL e controle de acesso.

## Tecnologias utilizadas

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Uvicorn
- Psycopg
- PyJWT
- Argon2
- Python-dotenv
- Pytest
- HTTPX

## Funcionalidades

### Gerenciamento

- Cadastro, consulta, atualização e exclusão de eventos.
- Gerenciamento de categorias.
- Gerenciamento de usuários.
- Gerenciamento de organizadores.
- Controle de inscrições.
- Emissão e gerenciamento de certificados.

### Autenticação e segurança

- Cadastro de usuários com credenciais.
- Armazenamento de senhas com hash Argon2.
- Login por e-mail e senha.
- Geração e validação de tokens JWT.
- Expiração configurável dos tokens.
- Proteção de rotas.
- Consulta do usuário autenticado pelo endpoint `/me`.
- Respostas HTTP 401 para autenticação inválida ou ausente.
- Respostas HTTP 403 para operações sem permissão.

### Perfis de acesso

**Participante**
- Consultar eventos e categorias.
- Realizar inscrições.
- Consultar e gerenciar suas próprias inscrições, respeitando as regras de negócio.
- Consultar seus próprios dados e certificados.

**Organizador**
- Cadastrar, atualizar e excluir seus próprios eventos.
- Gerenciar categorias.
- Consultar inscrições dos próprios eventos.
- Emitir e gerenciar certificados dos próprios eventos.
- Administrar usuários e seu próprio registro de organizador, conforme as permissões implementadas.

## Regras de negócio

- E-mails de usuários devem ser únicos.
- E-mails de organizadores devem ser únicos.
- Nomes de categorias devem ser únicos.
- Eventos devem possuir pelo menos uma vaga.
- Eventos não podem possuir data passada.
- Um usuário não pode se inscrever duas vezes no mesmo evento.
- Inscrições ativas não podem ultrapassar o número de vagas.
- Inscrições canceladas não ocupam vagas.
- Certificados só podem ser emitidos para inscrições confirmadas.
- Uma inscrição não pode possuir mais de um certificado.
- O código do certificado deve ser único.
- Eventos com inscrições não podem ser excluídos.
- Inscrições com certificados não podem ser excluídas.
- Participantes só podem gerenciar suas próprias inscrições.
- Organizadores só podem administrar seus próprios eventos e certificados relacionados.

## Banco de dados

O projeto utiliza PostgreSQL e SQLAlchemy.

Principais tabelas:

- `usuarios`
- `eventos`
- `categorias`
- `inscricoes`
- `certificados`
- `organizadores`

As relações são estabelecidas por chaves estrangeiras e restrições de integridade.

## Endpoints principais

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/auth/register` | Cadastro de usuário |
| POST | `/auth/login` | Login e geração de token |
| GET | `/me` | Dados do usuário autenticado |
| GET | `/eventos` | Listagem de eventos |
| POST | `/eventos` | Cadastro de evento |
| GET | `/categorias` | Listagem de categorias |
| GET | `/usuarios` | Consulta de usuários |
| GET | `/inscricoes` | Consulta de inscrições |
| POST | `/inscricoes` | Realização de inscrição |
| GET | `/certificados` | Consulta de certificados |
| POST | `/certificados` | Emissão de certificado |
| GET | `/organizadores` | Consulta de organizadores |

A documentação interativa do Swagger apresenta todos os endpoints disponíveis e seus respectivos parâmetros e respostas.

## Autenticação da API

A autenticação utiliza JWT (JSON Web Token).

Após realizar o login, o token recebido deve ser enviado no cabeçalho:

`Authorization: Bearer SEU_TOKEN`

As rotas protegidas exigem autenticação válida e respeitam as permissões de cada perfil.

## Testes automatizados

O projeto utiliza Pytest e HTTPX para verificar o funcionamento da API e suas regras de negócio.

A suíte atual possui **41 testes automatizados**, abrangendo:

- Cadastro e autenticação.
- Validação de credenciais.
- Proteção de rotas.
- Controle de permissões.
- Inscrições.
- Validação de eventos.
- Emissão e gerenciamento de certificados.
- Restrições de acesso entre usuários.

Os testes utilizam banco SQLite em memória, isolado do banco PostgreSQL de desenvolvimento.

### Executar os testes

Na raiz do projeto:

```bash
PYTHONPATH=. ./venv/bin/pytest -v
```

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/Rafael-Moises/sistema_eventos_academicos.git
cd sistema_eventos_academicos
```

### 2. Criar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Criar o banco PostgreSQL

Crie um banco de dados PostgreSQL chamado:

`eventos_academicos`

Configure também um usuário com permissões de acesso ao banco.

### 5. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto.

Exemplo:

```env
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/eventos_academicos

JWT_SECRET_KEY=SUBSTITUA_POR_UMA_CHAVE_SEGURA
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

SQL_ECHO=false
```

- `DATABASE_URL`: endereço de conexão com PostgreSQL.
- `JWT_SECRET_KEY`: chave privada para assinatura dos tokens.
- `JWT_ALGORITHM`: algoritmo utilizado pelo JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: tempo de validade do token.
- `SQL_ECHO`: ativa ou desativa a exibição das consultas SQL no terminal.

**Importante:** não compartilhe o arquivo `.env` nem envie credenciais reais ao GitHub. Utilize `.env.example` para documentar as variáveis necessárias.

### 6. Executar a aplicação

```bash
./venv/bin/uvicorn app.main:app --reload
```

### 7. Acessar o Swagger

Abra:

http://127.0.0.1:8000/docs

## Estrutura do projeto

```text
sistema_eventos_academicos/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           ├── api.py
│   │           ├── auth.py
│   │           ├── categorias.py
│   │           ├── certificados.py
│   │           ├── eventos.py
│   │           ├── inscricoes.py
│   │           ├── organizadores.py
│   │           └── usuarios.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── permissions.py
│   │   └── security.py
│   │
│   ├── database/
│   │   └── database.py
│   │
│   ├── models/
│   │   └── db_models.py
│   │
│   ├── schemas/
│   │   └── model.py
│   │
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_autenticacao.py
│   └── test_regras_negocio.py
│
├── docs/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Documentação interativa

A API utiliza Swagger UI, disponibilizado pelo FastAPI:

http://127.0.0.1:8000/docs

A documentação permite consultar os endpoints, visualizar os esquemas de dados e testar as operações da API.

---

Projeto acadêmico desenvolvido como parte das atividades da graduação em Análise e Desenvolvimento de Sistemas.
