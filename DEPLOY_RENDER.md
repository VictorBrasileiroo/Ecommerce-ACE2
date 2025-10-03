# Deploy no Render - Guia Completo

## 🚀 Passo a Passo para Deploy

### 1. Preparar o Repositório GitHub

1. **Criar repositório no GitHub**:
   - Vá para github.com
   - Clique em "New repository"
   - Nome: `ace2-vendas-ml`
   - Público ou privado (sua escolha)
   - NÃO marque "Initialize with README"

2. **Fazer push do código**:
   ```bash
   git init
   git add .
   git commit -m "Deploy: Sistema ACE2 - Vendas e ML"
   git branch -M main
   git remote add origin https://github.com/VictorBrasileiroo/ace2-vendas-ml.git
   git push -u origin main
   ```

### 2. Deploy do Backend no Render

1. **Acessar render.com** e fazer login
2. **Criar novo Web Service**:
   - Clique "New +" → "Web Service"
   - Conecte seu repositório GitHub
   - Selecione o repositório `ace2-vendas-ml`

3. **Configurações do Backend**:
   ```
   Name: ace2-backend
   Root Directory: (deixar vazio)
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Variáveis de Ambiente**:
   - `SECRET_KEY`: (clique "Generate" para gerar automaticamente)
   - `DATABASE_URL`: `sqlite:///./data/db.sqlite3`
   - `PYTHONPATH`: `/opt/render/project/src`

5. **Adicionar Persistent Disk**:
   - Name: `data`
   - Mount Path: `/opt/render/project/src/data`
   - Size: 1 GB

6. **Clique "Create Web Service"**

### 3. Deploy do Frontend no Render

1. **Criar segundo Web Service**:
   - "New +" → "Web Service"
   - Mesmo repositório GitHub

2. **Configurações do Frontend**:
   ```
   Name: ace2-frontend
   Root Directory: (deixar vazio)
   Environment: Python 3
   Build Command: pip install streamlit plotly requests pandas
   Start Command: streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
   ```

3. **Variáveis de Ambiente**:
   - `API_URL`: `https://ace2-backend.onrender.com` (substitua pelo URL do seu backend)

4. **Clique "Create Web Service"**

### 4. Atualizar API_URL no Frontend

Após o backend estar rodando, você precisará:

1. Copiar a URL do backend (ex: `https://ace2-backend.onrender.com`)
2. Atualizar a variável `API_URL` no frontend service
3. O frontend será redployado automaticamente

### 5. Testar o Sistema

1. **Acesse o frontend** na URL fornecida pelo Render
2. **Faça login** com: `admin@admin.com` / `admin`
3. **Teste as funcionalidades**:
   - Upload de CSV
   - Visualização de métricas
   - Execução do ML

## 🔧 Arquivos de Configuração

O projeto já inclui:
- ✅ `requirements.txt` - Dependências Python
- ✅ `render.yaml` - Configuração automática
- ✅ Código preparado para produção

## ⚠️ Importante

### Limitações do Plano Gratuito:
- Services "dormem" após 15 min de inatividade
- Cold start pode levar 30-60 segundos
- 750 horas/mês de uso gratuito

### Primeiro Acesso:
- Backend pode demorar 1-2 minutos para inicializar
- Frontend pode demorar 30-60 segundos
- Isso é normal no plano gratuito

## 🎯 URLs Finais

Após o deploy, você terá:
- **Backend API**: `https://ace2-backend.onrender.com`
- **Frontend**: `https://ace2-frontend.onrender.com`
- **API Docs**: `https://ace2-backend.onrender.com/docs`

## 🆘 Solução de Problemas

### Se o deploy falhar:
1. Verifique os logs no Render Dashboard
2. Certifique-se que o `requirements.txt` está correto
3. Verifique se as variáveis de ambiente estão configuradas

### Se o frontend não conectar:
1. Verifique se a `API_URL` está correta
2. Aguarde o backend "acordar" (pode demorar)
3. Verifique os logs de ambos os services

### Para forçar redesploy:
1. Faça um commit vazio: `git commit --allow-empty -m "trigger deploy"`
2. Push: `git push`
3. O Render fará novo deploy automaticamente