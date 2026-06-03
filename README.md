# API de Gestao de Tarefas Colaborativas (FastAPI + MVC)

Implementacao da atividade de Engenharia de Software com:

- FastAPI (Python)
- Arquitetura MVC
- JWT para autenticacao
- Requisito complementar 7: Sistema de Notificacoes Internas
- Requisito complementar 8: Filtro Avancado de Tarefas

## Arquitetura MVC

- Model: `app/models`
- View (DTOs/serializacao): `app/views`
- Controller (rotas e casos de uso HTTP): `app/controllers`

## Funcionalidades implementadas

### Usuarios

- `POST /users` cria usuario
- `GET /users/{id}` busca usuario
- `PUT /users/{id}` atualiza usuario
- `DELETE /users/{id}` remove usuario (soft delete)

### Tarefas

- `POST /tasks` cria tarefa
- `GET /tasks/{id}` busca tarefa
- `GET /tasks` lista tarefas com filtros
- `PUT /tasks/{id}` atualiza tarefa
- `DELETE /tasks/{id}` remove tarefa (soft delete)

### Autenticacao

- `POST /auth/login` retorna JWT
- `POST /auth/logout` revoga token

### Requisito 7: Notificacoes internas

- Notificacao interna ao usuario quando:
  - recebe uma tarefa
  - tarefa atribuida a ele e alterada
- Envio de e-mail na criacao de tarefa atribuida (via `smtplib`)
- Endpoints:
  - `GET /notifications`
  - `PATCH /notifications/{id}/read`

### Requisito 8: Filtro avancado

Endpoint:

- `GET /tasks?status=done&priority=high&dueBefore=2026-06-01T00:00:00&assignedTo=2`

Filtros suportados:

- `assignedTo`
- `status` (`pending`, `in_progress`, `done`)
- `priority` (`low`, `medium`, `high`)
- `dueBefore` (datetime ISO)

## Como executar

1. Criar ambiente virtual e instalar dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Rodar a API:

```bash
uvicorn app.main:app --reload --env-file .env
```

3. Abrir documentacao Swagger:

- http://127.0.0.1:8000/docs

## Testes automatizados

Executar:

```bash
pytest -q
```

Os testes cobrem:

- fluxo de usuario (criar, autenticar, consultar, atualizar)
- tarefas com filtros avancados
- notificacoes internas
- logout com invalidacao de token

## Banco de dados

- Padrao: SQLite (`app.db`)
- Configuravel via variavel de ambiente `DATABASE_URL`

## Executando com Docker Compose

Subir API + SMTP (MailHog):

```bash
docker compose up --build
```

Acessos:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- SMTP UI (MailHog): http://127.0.0.1:8025

Para encerrar:

```bash
docker compose down
```

## Configuracao de e-mail (SMTP)

Para habilitar envio de e-mail na criacao de tarefas, configure:

- `SMTP_ENABLED=true`
- `SMTP_HOST=localhost`
- `SMTP_PORT=1025`
- `SMTP_SENDER=no-reply@task-api.local`
- `SMTP_USE_TLS=false`
- `SMTP_USE_SSL=false`
- `SMTP_USER=` (opcional)
- `SMTP_PASSWORD=` (opcional)

Exemplo com servidor SMTP local de desenvolvimento (MailHog/Mailpit):

```bash
docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog
```
