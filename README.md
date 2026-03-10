# 🌿 Projeto Acadêmico - Brotinho

Aplicação web fullstack desenvolvida com Flask, SQLAlchemy, Flask-Login e Python. O objetivo era criar uma plataforma de jardinagem que permite que os usuários gerenciem seu jardim 
e interajam com outros usuários por meio de trocas de plantas e sementes.

Por ser um projeto para o meio acadêmico, deixarei o passo a passo de utilização e algumas observações abaixo:
---

## 🛠️ Configuração do Ambiente

### 1. Criar e ativar o ambiente virtual

```bash
# Criar o ambiente virtual
py -m venv venv

# Permitir execução de scripts (necessário no Windows, apenas uma vez)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ativar o ambiente virtual
.\venv\Scripts\activate
```

---

## 📦 Instalação das Dependências

> **Dica:** Atualize o pip apenas se o terminal solicitar após instalar o Flask.

```bash
# Atualizar pip (somente se necessário)
python.exe -m pip install --upgrade pip

# Instalar pacotes
pip install flask
pip install ipython
pip install flask-wtf
pip install flask-sqlalchemy
pip install flask-migrate
pip install flask-login
pip install email-validator
```

Ou, se houver um `requirements.txt` disponível:

```bash
pip install -r requirements.txt
```

---

## 🗄️ Configuração do Banco de Dados

### Inicializar as migrações

> Execute este comando **apenas uma vez**. Ele cria a pasta `migrations/` com os arquivos essenciais.

```bash
flask db init
```

### Criar as tabelas

```bash
flask db migrate -m "users table"
flask db migrate -m "plants table"
flask db migrate -m "tarefas table"
flask db migrate -m "trocas table"
```

### Aplicar as migrações ao banco

```bash
flask db upgrade
```

---

## ▶️ Executando a Aplicação

```bash
set FLASK_APP=projeto_prog_avan.py
set DEBUG=1
$ENV:FLASK_DEBUG=1
flask run
```

---

## 🔍 Consultas via Flask Shell

Para acessar o shell interativo do Flask e realizar consultas ao banco:

```bash
flask shell
```

---

## 🧪 Resetar Dados de Teste

Após uma sessão de testes, para apagar os dados e recriar o banco do zero:

```bash
flask db downgrade base
flask db upgrade
```

---

## 📁 Estrutura do Projeto

```
projeto/
├── app/                  # Código principal da aplicação
├── migrations/           # Scripts de migração do banco de dados
├── config.py             # Configurações da aplicação
├── projeto_prog_avan.py  # Ponto de entrada da aplicação
├── requirements.txt      # Dependências do projeto
├── .gitignore            # Arquivos ignorados pelo Git
└── README.md             # Este arquivo
```

---

## 🚫 Arquivos ignorados pelo Git (`.gitignore`)

```
__pycache__/
*.pyc
venv/
*.db
*.sqlite3
.env
```
