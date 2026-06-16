# 🎓 Plataforma EdTech API (RESTful)
🟢 **Status:** Online | **Acesse a API ao vivo:** [EdTech API - Swagger UI](https://edtech-5f6u.onrender.com)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)

Uma API robusta e escalável desenvolvida para atuar como o motor (Back-End) de uma plataforma de cursos online (EAD). O sistema gerencia matrículas, hospedagem de arquivos e possui um sistema de segurança rigoroso baseado em níveis de acesso.

## 📖 Sobre o Projeto

O grande diferencial desta arquitetura é o seu sistema de **Controle de Acesso Baseado em Cargos (RBAC)** protegido por tokens JWT. A plataforma divide as regras de negócio em três perfis isolados:

* 👨‍🎓 **Alunos:** Podem navegar pelo catálogo, realizar matrículas em cursos e realizar o download seguro dos materiais de aula.
* 👨‍🏫 **Instrutores:** Possuem um painel de permissões para criar novos cursos e realizar o upload de videoaulas e PDFs preservando a performance do servidor.
* 🛡️ **Administradores:** Gerenciam a integridade do sistema e possuem a chave de permissão exclusiva para cadastrar novos instrutores na plataforma.

## 🚀 Features Técnicas (Under the Hood)

* **Autenticação e Segurança:** Implementação de JWT (JSON Web Tokens) para proteção de rotas privadas e criptografia de senhas (hashing) no banco de dados.
* **Upload de Arquivos Otimizado:** Uso de transferência em *chunks* (`shutil.copyfileobj`) para processar arquivos pesados (como videoaulas) sem sobrecarregar a memória RAM do servidor.
* **ORM e Banco de Dados Relacional:** Modelagem de dados avançada utilizando **SQLAlchemy**, com controle de versão do banco gerenciado pelo **Alembic**. O banco de dados primário (PostgreSQL) é provisionado de forma isolada via **Docker**.
* **Validação Estrita:** Utilização do **Pydantic** para garantir que todas as requisições e respostas (JSON) sigam moldes rígidos de tipagem.

---

## ⚙️ Como executar o projeto localmente

### 1. Pré-requisitos
* Python 3.11+
* Docker Desktop (para rodar o banco de dados)

### 2. Passo a Passo

Clone este repositório e acesse a pasta do projeto:
```bash
git clone https://github.com/RyusakiRL/EdTech.git
cd EdTech
### 1. Ativar o ambiente virtual
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

### 2. Instalar bibliotecas necessarias
pip install -r requirements.txt

### 3. Ligar o banco de dados em segundo plano usando o Docker
docker-compose up -d

### 4. Criar as tabelas no PostgreSQL executando as migrações
alembic upgrade head

### 5. Ligar o sistema a API
uvicorn main:app --reload