# Sistema de Gestão de Eventos Acadêmicos
API REST desenvolvida para gerenciamento de eventos acadêmicos.

## Objetivo
O sistema tem como objetivo permitir o gerenciamento de eventos acadêmicos, usuários, categorias, inscrições, certificados e organizadores.

## Tecnologias utilizadas
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Uvicorn

## Funcionalidades
- Cadastro de eventos
- Consulta de eventos
- Atualização de eventos
- Exclusão de eventos
- Cadastro de categorias
- Cadastro de usuários
- Cadastro de inscrições
- Cadastro de certificados
- Cadastro de organizadores
- Validação de regras de negócio
- Controle de capacidade dos eventos
- Controle de inscrições duplicadas
- Integração com PostgreSQL
- Documentação automática através do Swagger

## Entidades
O sistema possui as seguintes entidades:
- Usuário
- Evento
- Categoria
- Inscrição
- Certificado
- Organizador

## Banco de dados
O projeto utiliza PostgreSQL como banco de dados e SQLAlchemy para realizar a comunicação entre a aplicação e o banco.
As principais relações são:
- Usuários → Inscrições
- Eventos → Inscrições
- Categorias → Eventos
- Organizadores → Eventos
- Inscrições → Certificados

## API
A API foi desenvolvida utilizando FastAPI.
A documentação interativa é disponibilizada pelo Swagger através da rota: `/docs`
Com a aplicação executando localmente:
`http://127.0.0.1:8000/docs`

## Estrutura do projeto
```text
sistema_eventos_academicos/
├── main.py
├── model.py
├── db_models.py
├── database.py
├── requirements.txt
└── .gitignore



## Comandos para executar a API
`uvicorn main:app --reload` → executa a API  
 
### 1. Instalar as bibliotecas
`pip install -r requirements.txt` → instala as bibliotecas  
Após baixar/clonar o projeto, execute:
```bash
venv/bin/python -m pip install -r requirements.txt


