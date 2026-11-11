
# Sistema de Gestão de Eventos Acadêmicos

API REST desenvolvida com **Python e FastAPI** para o gerenciamento de eventos acadêmicos. O sistema permite administrar eventos, categorias, usuários, inscrições, certificados e organizadores, contando também com mecanismos de autenticação, autorização e segurança.

## Equipe

**Integrantes do projeto:**

- Rafael Moisés Ferreira Santiago
- Elizeu da Silva Joaquin
- Mayk Dias de Oliveira Magalhães
- Anderson trindade
- Jose rennan

## Objetivo

O objetivo do projeto é disponibilizar uma API para centralizar e organizar o gerenciamento de eventos acadêmicos, permitindo o cadastro, consulta, atualização e exclusão de informações, além da aplicação de regras de negócio, integração com banco de dados PostgreSQL e controle de acesso por autenticação e autorização.

## Tecnologias utilizadas

- Python
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

### Gerenciamento de eventos acadêmicos

A API disponibiliza operações de cadastro, consulta, atualização e exclusão para:

- Eventos
- Categorias
- Usuários
- Inscrições
- Certificados
- Organizadores

Também possui validações de regras de negócio, controle de capacidade dos eventos, prevenção de inscrições duplicadas e gerenciamento de certificados.

### Autenticação e segurança

Foram implementados mecanismos de autenticação e proteção da aplicação:

- Cadastro de usuários com credenciais de acesso.
- Armazenamento de senhas utilizando hash seguro com Argon2.
- Autenticação por e-mail e senha.
- Geração de tokens JWT (JSON Web Token).
- Definição de tempo de expiração dos tokens.
- Validação de tokens JWT.
- Proteção de rotas que exigem autenticação.
- Consulta dos dados do usuário autenticado.
- Retorno HTTP 401 para tentativas de acesso sem autenticação válida.
- Configuração da chave JWT por variável de ambiente.

### Autorização e controle de acesso

O sistema possui dois perfis de usuário com permissões distintas:

**Participante:**

- Consultar eventos e categorias.
- Realizar inscrições em eventos.
- Consultar suas próprias inscrições.
- Atualizar ou cancelar suas próprias inscrições.
- Excluir suas próprias inscrições, respeitando as regras de negócio.
- Consultar seus próprios dados e certificados.

**Organizador:**

- Consultar eventos e categorias.
- Cadastrar, atualizar e excluir seus próprios eventos.
- Gerenciar categorias.
- Consultar inscrições vinculadas aos seus eventos.
- Emitir, consultar, atualizar e excluir certificados dos seus eventos.
- Consultar e administrar registros de usuários.
- Gerenciar seu próprio registro de organizador.

O sistema também verifica a propriedade dos recursos, impedindo que participantes acessem inscrições e certificados de outros usuários ou que organizadores administrem eventos de outros organizadores.

### Matriz de permissões
| Recurso / Operação | Endpoint | Participante | Organizador |
|---|---|---|---|
| Consultar eventos | GET `/eventos` e `/eventos/{id}` | Permitido | Permitido |
| Criar eventos | POST `/eventos` | Negado | Permitido |
| Atualizar eventos | PUT `/eventos/{id}` | Negado | Somente próprios |
| Excluir eventos | DELETE `/eventos/{id}` | Negado | Somente próprios |
| Consultar categorias | GET `/categorias` | Permitido | Permitido |
| Criar categorias | POST `/categorias` | Negado | Permitido |
| Atualizar categorias | PUT `/categorias/{id}` | Negado | Permitido |
| Excluir categorias | DELETE `/categorias/{id}` | Negado | Permitido |
| Consultar inscrições | GET `/inscricoes` e `/inscricoes/{id}` | Somente próprias | Somente dos próprios eventos |
| Criar inscrições | POST `/inscricoes` | Permitido | Negado |
| Atualizar inscrições | PUT `/inscricoes/{id}` | Somente próprias | Negado |
| Excluir inscrições | DELETE `/inscricoes/{id}` | Somente próprias | Negado |
| Consultar certificados | GET `/certificados` e `/certificados/{id}` | Somente próprios | Somente dos próprios eventos |
| Emitir certificados | POST `/certificados` | Negado | Somente dos próprios eventos |
| Atualizar certificados | PUT `/certificados/{id}` | Negado | Somente dos próprios eventos |
| Excluir certificados | DELETE `/certificados/{id}` | Negado | Somente dos próprios eventos |
| Consultar usuários | GET `/usuarios` e `/usuarios/{id}` | Somente próprios dados | Permitido |
| Gerenciar usuários | POST, PUT e DELETE `/usuarios` | Negado | Permitido, conforme regras |
| Consultar organizadores | GET `/organizadores` e `/organizadores/{id}` | Permitido | Permitido |
| Gerenciar organizadores | POST, PUT e DELETE `/organizadores` | Negado | Somente próprio registro |
| Consultar perfil | GET `/me` | Permitido | Permitido |
### Tratamento de permissões

O controle de acesso utiliza dependências para verificar o perfil do usuário autenticado.

- **HTTP 401 Unauthorized:** token ausente, inválido ou expirado.
- **HTTP 403 Forbidden:** usuário autenticado, mas sem permissão para executar a operação.
- **HTTP 404 Not Found:** recurso solicitado não encontrado.

## Entidades

O sistema possui as seguintes entidades:

- Usuário
- Evento
- Categoria
- Inscrição
- Certificado
- Organizador

## Relacionamentos

As principais relações entre as entidades são:

- Um usuário pode possuir várias inscrições.
- Um evento pode possuir várias inscrições.
- Uma categoria pode estar relacionada a vários eventos.
- Um organizador pode estar relacionado a vários eventos.
- Uma inscrição pode possuir um certificado.

## Banco de dados

O projeto utiliza **PostgreSQL** como sistema de gerenciamento de banco de dados e **SQLAlchemy** para realizar a comunicação entre a aplicação e o banco.

As principais tabelas são:

- `usuarios`
- `eventos`
- `categorias`
- `inscricoes`
- `certificados`
- `organizadores`

As relações entre as tabelas são estabelecidas por meio de chaves estrangeiras e restrições de integridade.

## Regras de negócio

Entre as principais regras implementadas estão:

- O e-mail de usuário deve ser único.
- O e-mail de organizador deve ser único.
- O nome da categoria deve ser único.
- Um evento deve possuir pelo menos uma vaga.
- Eventos não podem possuir data anterior à data atual.
- Um usuário não pode realizar duas inscrições no mesmo evento.
- A quantidade de inscrições ativas não pode ultrapassar a quantidade de vagas.
- Inscrições canceladas não ocupam vaga.
- Um certificado somente pode ser emitido para uma inscrição confirmada.
- Uma inscrição não pode possuir mais de um certificado.
- O código do certificado deve ser único.
- Eventos com inscrições não podem ser excluídos.
- Categorias vinculadas a eventos não podem ser excluídas.
- Usuários com inscrições não podem ser excluídos.
- Organizadores vinculados a eventos não podem ser excluídos.
- Inscrições que possuem certificado não podem ser excluídas.
- Participantes somente podem gerenciar suas próprias inscrições.
- Organizadores somente podem gerenciar seus próprios eventos e os certificados relacionados a eles.

## Autenticação da API

A autenticação utiliza tokens JWT para controlar o acesso aos endpoints protegidos.

Principais endpoints de autenticação:

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/auth/register` | Cadastro de usuário com credenciais |
| POST | `/auth/login` | Autenticação e geração de token JWT |
| GET | `/me` | Consulta dos dados do usuário autenticado |

Após realizar o login, o usuário recebe um token JWT que deve ser enviado no cabeçalho `Authorization` no formato `Bearer` para acessar as rotas protegidas.

As senhas não são armazenadas em texto puro, sendo protegidas por hash Argon2.

A chave utilizada para assinatura dos tokens é configurada por variável de ambiente.

## Testes automatizados

O projeto utiliza **Pytest** e **HTTPX** para a execução de testes automatizados da API.

Os testes verificam:

- Cadastro de usuários.
- Impedimento de cadastro com e-mail já existente.
- Login com credenciais válidas.
- Bloqueio de login com senha incorreta.
- Bloqueio de acesso sem token.
- Bloqueio de acesso com token inválido.
- Restrição de operações incompatíveis com o perfil Participante.
- Restrição de operações incompatíveis com o perfil Organizador.

Atualmente, a suíte possui 14 testes automatizados aprovados.

### Executar os testes

Na raiz do projeto, execute:

```bash
./venv/bin/python -m pytest -v
```

## Documentação da API

A documentação interativa é disponibilizada automaticamente pelo Swagger UI.

Com a aplicação em execução, acesse:

**http://127.0.0.1:8000/docs**

O Swagger permite visualizar, testar e executar os endpoints, incluindo as operações de autenticação e as rotas protegidas.

## Como executar a API

### 1. Clonar o repositório

```bash
git clone https://github.com/Rafael-Moises/sistema_eventos_academicos.git
cd sistema_eventos_academicos
```

### 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Configure o arquivo `.env` com os dados de conexão do banco de dados e as variáveis necessárias para autenticação JWT.

Exemplo das variáveis JWT:

```env
JWT_SECRET_KEY=sua_chave_secreta
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Importante:** o arquivo `.env` contém informações privadas e não deve ser enviado ao GitHub.

### 5. Executar a aplicação

Na raiz do projeto, execute:

```bash
uvicorn app.main:app --reload
```

### 6. Acessar a documentação

Abra o navegador e acesse:

http://127.0.0.1:8000/docs

### 7. Encerrar a aplicação

No terminal, pressione:

```text
Ctrl + C
```

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
│   └── test_autenticacao.py
│
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

---

**Projeto acadêmico desenvolvido como parte das atividades da graduação em Análise e Desenvolvimento de Sistemas.**
