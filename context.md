# Programa da Aula

# Atividade Acadêmica: Engenharia de Software – Arquitetura e Padrões

**Professor:** Guilherme Silva de Lacerda  
- guilhermeslacerda@gmail.com  
- gslacerda@unisinos.br  

---

# Trabalho T2

## Definição do Trabalho

O objetivo deste trabalho é que os alunos projetem, implementem e documentem uma API RESTful utilizando boas práticas de Arquitetura de Software.

O projeto deve ser realizado em equipes de até 4 pessoas e contemplar aspectos como:

- Modularização
- Padrões arquiteturais
- Testes automatizados
- Documentação adequada

---

# Descrição do Trabalho

As equipes deverão desenvolver uma API para um sistema de **Gestão de Tarefas Colaborativas**, permitindo que usuários:

- Criem tarefas
- Editem tarefas
- Atribuam tarefas
- Concluam tarefas

A API deve seguir uma arquitetura bem definida, por exemplo:

- Arquitetura Hexagonal
- Clean Architecture
- MVC

Garantindo boas práticas de:

- Desacoplamento
- Modularização

Além da implementação, é necessário entregar:

- Documentação técnica detalhando as decisões arquiteturais
- Conjunto de testes automatizados para garantir a confiabilidade da API

---

# Requisitos Funcionais

## Usuários

### Criar um novo usuário
```http
POST /users
```

### Obter informações de um usuário específico
```http
GET /users/{id}
```

### Atualizar informações do usuário
```http
PUT /users/{id}
```

### Remover um usuário
```http
DELETE /users/{id}
```

> Soft delete recomendado.

---

## Tarefas

### Criar uma nova tarefa
```http
POST /tasks
```

### Obter detalhes de uma tarefa
```http
GET /tasks/{id}
```

### Listar todas as tarefas atribuídas a um usuário
```http
GET /tasks?assignedTo={userId}
```

### Atualizar informações da tarefa
```http
PUT /tasks/{id}
```

Campos:
- título
- descrição
- status

### Remover uma tarefa
```http
DELETE /tasks/{id}
```

---

## Autenticação

### Login de usuários
```http
POST /auth/login
```

Retorna um token JWT para autenticação nas demais requisições.

### Logout do usuário
```http
POST /auth/logout
```

---

# Requisitos Complementares

Com o objetivo de aumentar o desafio técnico, a equipe pode escolher **3 dos requisitos complementares** listados a seguir para implementação.

---

# 1 - Integração com Calendários (Google Calendar, Outlook)

## Funcionalidades

- Permitir que tarefas atribuídas com datas sejam sincronizadas com o calendário do usuário
- Criar eventos automaticamente no calendário

## Exemplo

Ao criar uma tarefa com data e hora, o sistema cria um evento no Google Calendar do usuário.

---

# 2 - Webhooks para Integração com Slack/Discord

## Funcionalidades

- Disparar notificações sempre que:
  - Uma tarefa for criada
  - Uma tarefa for atribuída
  - Uma tarefa for concluída

## Observação

Pode ser implementado de forma genérica:
- Usuários configuram seus próprios webhooks

---

# 3 - Integração com Serviços de Armazenamento (Google Drive, Dropbox)

## Funcionalidades

- Permitir anexar arquivos às tarefas
- Utilizar links autenticados

---

# 4 - Visualizações de Dados e Métricas

## Dashboard de Produtividade

## Exposição de métricas por endpoint

### Exemplos de métricas

- Número de tarefas por status:
  - pendente
  - em andamento
  - concluída

- Tarefas por usuário

- Tempo médio de conclusão de tarefas

## Endpoint sugerido

```http
GET /metrics
```

## Visualização

Pode utilizar uma rota adicional consumindo dados com bibliotecas como:

- Chart.js

---

## Exportação de Relatórios (CSV/PDF)

### Funcionalidades

Permitir que os usuários exportem:

- Suas tarefas
- Atividades realizadas

## Objetivo

Ideal para times que precisam:

- Prestar contas
- Fazer retrospectivas

---

# 5 - Sistema de Permissões com Papéis

## Papéis sugeridos

- Administrador
- Usuário
- Convidado

## Exemplo

Apenas administradores podem deletar tarefas de outros usuários.

---

# 6 - Comentários em Tarefas (Sub-recursos aninhados)

## Endpoint

```http
/tasks/{id}/comments
```

## Funcionalidades

- Criação de comentários
- Leitura de comentários
- Exclusão de comentários

## Regras

- Associar comentários a usuários
- Registrar timestamps

---

# 7 - Sistema de Notificações Internas (e-mail ou push)

## Funcionalidades

Notificar usuários sobre:

- Tarefas atribuídas
- Tarefas alteradas

## Serviços sugeridos

- SendGrid
- Mailgun

Também pode ser implementado com notificações simuladas via log.

---

# 8 - Filtro Avançado de Tarefas

## Endpoint com múltiplos parâmetros

```http
GET /tasks?status=done&priority=high&dueBefore=2025-06-01
```

---

# Requisitos Não Funcionais

- Utilizar linguagem de programação à escolha da equipe

### Exemplos

- Python com FastAPI
- Java com Spring Boot
- Node.js com Express

---

- Implementar padrões arquiteturais claros

### Exemplos

- Arquitetura Hexagonal
- MVC
- Clean Architecture

---

- Utilizar banco de dados:
  - Relacional (MySQL, PostgreSQL)
  - NoSQL (MongoDB)

> A escolha deve ser justificada.

---

- Implementar testes automatizados com cobertura mínima de 60% do código da API

- Implementar logs e tratamento de erros adequados

- Documentar a API utilizando Swagger/OpenAPI

---

# Documentação

A equipe deve entregar uma documentação contendo:

---

## Visão Geral

- Objetivo do sistema
- Contexto de uso
- Instruções de instalação

---

## Decisões Arquiteturais

- Justificativa para escolha da arquitetura
- Padrões aplicados

---

## Modelagem de Dados

- Diagrama do banco de dados
- Descrição das tabelas/coleções

---

## Fluxo de Requisições

- Descrição dos principais endpoints
- Exemplos de uso

---

## Configuração e Deploy

- Guia de execução do projeto
- Dependências
- Configuração do ambiente

---

## Testes Automatizados

- Estratégia utilizada
- Métricas de cobertura

---

# Formato de Entrega

- Repositório Git público ou privado com acesso concedido ao professor

- Código-fonte estruturado seguindo boas práticas de versionamento

- Documentação em:
  - Markdown (`README.md`)
  - PDF

- Vídeo demo da solução com até 10 minutos

- Testes automatizados implementados e executáveis via terminal

## Exemplos

- `pytest` para Python
- `JUnit` para Java
- `Jest` para Node.js

---

# Critérios de Avaliação

| Critério | Peso |
|---|---|
| Arquitetura e organização do código | 25% |
| Implementação correta dos requisitos funcionais | 25% |
| Qualidade dos testes automatizados | 20% |
| Documentação técnica e justificativa de decisões | 20% |
| Uso de boas práticas de desenvolvimento (versionamento, padrões, logs, segurança) | 10% |

---

# Prazos

## Entrega

Entrega do repositório Git com código e documentação.

> Data definida pelo professor.

---

## Apresentação

Apresentação do projeto:
- Até 10 minutos por equipe

> Data definida pelo professor.