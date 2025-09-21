# Sistema de Vendas com Previsão (FastAPI + Streamlit)

## Arquitetura
- **Backend/API:** FastAPI
- **Banco de Dados:** SQLAlchemy + SQLite
- **Machine Learning:** Python (Holt-Winters/ETS)
- **Frontend:** Streamlit

```
Planilha CSV → API FastAPI → DB SQLite → ML (Forecast) → Dashboard Streamlit
```

## Como rodar o projeto

### Opção 1: Scripts automáticos (Recomendado)
1. **Backend:** Execute `run_backend.bat`
2. **Frontend:** Execute `run_frontend.bat`
3. **ML:** Execute `run_ml.bat`

### Opção 2: Comandos manuais

1. **Backend (Terminal 1):**
```bash
cd c:\Users\victo\Desktop\ACE2
C:/Users/victo/Desktop/ACE2/.venv/Scripts/python.exe -m uvicorn backend.main:app --reload
```

2. **Frontend (Terminal 2):**
```bash
cd c:\Users\victo\Desktop\ACE2
C:/Users/victo/Desktop/ACE2/.venv/Scripts/streamlit.exe run frontend/app.py
```

3. **ML (quando necessário):**
```bash
cd c:\Users\victo\Desktop\ACE2
C:/Users/victo/Desktop/ACE2/.venv/Scripts/python.exe ml/ml.py
```

## URLs de acesso
- **API Documentation:** http://127.0.0.1:8000/docs
- **Dashboard:** http://localhost:8501

## Como usar o sistema
1. **Acesse o dashboard:** http://localhost:8501
2. **Primeira vez?** Use a aba "Cadastro" para criar sua conta
3. **Já tem conta?** Use a aba "Login" 
4. **Login padrão (admin):** admin@admin.com / admin
5. **Importe dados:** Use o arquivo `exemplo_vendas.csv`
6. **Gere previsões:** Execute `run_ml.bat`

## Endpoints da API
- `POST /auth/login` — autenticação JWT
- `POST /auth/register` — cadastro de novos usuários
- `POST /import` — upload de planilha CSV de vendas
- `GET /metrics` — retorna KPIs (receita total, ticket médio, produto mais vendido, evolução mensal)
- `GET /forecast` — retorna previsões salvas no DB

## Estrutura do Banco de Dados

- **usuarios** (id, email, senha_hash)
- **produtos** (id, nome, categoria, preco)
- **vendas** (id, data, produto_id, quantidade, valor_total)
- **forecast** (id, produto_id, data_prevista, qtd_prevista, intervalo_conf)

## Fluxo de dados

1. Usuário faz login no dashboard (JWT)
2. Faz upload da planilha de vendas (CSV)
3. API importa dados para o banco
4. Script ML gera previsões e salva no banco
5. Dashboard exibe KPIs, gráficos e previsões

## Arquivos de exemplo

- `exemplo_vendas.csv` — planilha de exemplo para testar o sistema

---

> Protótipo para análise de vendas e previsão de demanda.
