
## Equipe
**Integrantes do projeto:**
- Rafael Moisés Ferreira Santiago
- Elizeu da Silva Joaquin
- Mayk Dias de Oliveira Magalhães

# Sistema de Gestão de Eventos Acadêmicos
API REST desenvolvida para o gerenciamento de eventos acadêmicos, permitindo controlar eventos, categorias, usuários, inscrições, certificados e organizadores.

## Objetivo
O sistema tem como objetivo disponibilizar uma API para centralizar e organizar o gerenciamento de eventos acadêmicos, permitindo o cadastro, consulta, atualização e exclusão de informações, além da aplicação de regras de negócio e integração com banco de dados PostgreSQL.

## Tecnologias utilizadas
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Uvicorn
- Psycopg

## Funcionalidades
A API possui funcionalidades para:
- Cadastro, consulta, atualização e exclusão de eventos
- Cadastro, consulta, atualização e exclusão de categorias
- Cadastro, consulta, atualização e exclusão de usuários
- Cadastro, consulta, atualização e exclusão de inscrições
- Cadastro, consulta, atualização e exclusão de certificados
- Cadastro, consulta, atualização e exclusão de organizadores
- Validação de regras de negócio
- Controle de capacidade dos eventos
- Controle de inscrições duplicadas
- Controle de certificados vinculados às inscrições
- Validação de datas
- Integração com banco de dados PostgreSQL
- Documentação e testes através do Swagger

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
O projeto utiliza PostgreSQL como banco de dados e SQLAlchemy para realizar a comunicação entre a aplicação e o banco.
As tabelas principais são:
- `usuarios`
- `eventos`
- `categorias`
- `inscricoes`
- `certificados`
- `organizadores`
As relações entre as tabelas são estabelecidas através de chaves estrangeiras e restrições de integridade.

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

## API
A API foi desenvolvida utilizando o framework FastAPI.
A documentação interativa da API é disponibilizada automaticamente através do Swagger.
Com a aplicação em execução, acesse:
`http://127.0.0.1:8000/docs`
O Swagger permite visualizar, testar e executar os endpoints da API.

## Como executar a API
1. Instalar bibliotecas
        ↓
venv/bin/python -m pip install -r requirements.txt
2. Executar a API
        ↓
venv/bin/python -m uvicorn main:app --reload
3. Abrir o Swagger
        ↓
http://127.0.0.1:8000/docs
4. Encerrar
        ↓
Ctrl + C
