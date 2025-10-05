from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import Base, Usuario, Produto, Venda, Forecast
from .auth import router as auth_router, get_current_user, get_password_hash
from .database import get_db, engine, SessionLocal
from .schemas import MetricsResponse, ForecastOut, ImportResponse, MLResponse, ErrorResponse
from typing import List
import csv
import io
import os
from datetime import datetime

# Criar diretório data se não existir
os.makedirs("data", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Vendas & Previsões ML",
    description="""
## 🚀 API para análise de vendas com Machine Learning

Esta API oferece funcionalidades completas para:
- **Autenticação JWT**: Login seguro e gestão de usuários
- **Importação de dados**: Upload de CSV com dados de vendas  
- **Métricas avançadas**: KPIs, evolução mensal, top produtos
- **Machine Learning**: Previsões automáticas de demanda e receita

### 🔐 Como usar:
1. Faça login em `/auth/login` ou registre-se em `/auth/register`
2. Use o token JWT no header: `Authorization: Bearer <token>`
3. Importe dados via `/import` com arquivo CSV
4. Execute o ML via `/run-ml` para gerar previsões
5. Visualize métricas em `/metrics` e previsões em `/forecast`

### 📊 Formato CSV esperado:
```csv
data,produto,categoria,preco,quantidade,valor_total
2024-01-15,Notebook Dell,Eletrônicos,2500.00,2,5000.00
```

### 🔗 Links úteis:
- **Frontend**: Execute localmente com Streamlit
- **Repositório**: [GitHub](https://github.com/VictorBrasileiroo/Ecommerce-ACE2)
""",
    version="1.0.0",
    contact={
        "name": "Victor Brasileiro",
        "url": "https://github.com/VictorBrasileiroo",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "Autenticação",
            "description": "Endpoints para login e registro de usuários",
        },
        {
            "name": "Dados",
            "description": "Importação e gestão de dados de vendas",
        },
        {
            "name": "Métricas",
            "description": "Análises e KPIs de vendas",
        },
        {
            "name": "Machine Learning",
            "description": "Previsões e algoritmos de ML",
        },
    ],
)
app.include_router(auth_router, tags=["Autenticação"])

# Configuração CORS para produção
origins = [
    "http://localhost:8501",
    "http://localhost:3000", 
    "https://*.onrender.com",
    "https://ace2-frontend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if os.getenv("ENVIRONMENT") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/import", 
         response_model=ImportResponse,
         tags=["Dados"],
         summary="Importar dados de vendas via CSV",
         description="""Upload de arquivo CSV com dados de vendas. O arquivo deve conter as colunas:
         - data (formato: YYYY-MM-DD)
         - produto (nome do produto)
         - categoria (categoria do produto)
         - preco (preço unitário)
         - quantidade (quantidade vendida)
         - valor_total (valor total da venda)
         
         Exemplo de CSV válido:
         ```
         data,produto,categoria,preco,quantidade,valor_total
         2024-01-15,Notebook Dell,Eletrônicos,2500.00,2,5000.00
         2024-01-20,Mouse Logitech,Periféricos,150.00,5,750.00
         ```""",
         responses={
             200: {
                 "description": "Importação realizada com sucesso",
                 "content": {
                     "application/json": {
                         "example": {"status": "Importação realizada"}
                     }
                 }
             },
             400: {
                 "description": "Erro na validação ou processamento do arquivo",
                 "model": ErrorResponse,
                 "content": {
                     "application/json": {
                         "examples": {
                             "invalid_format": {
                                 "summary": "Formato inválido",
                                 "value": {"detail": "Arquivo deve ser CSV"}
                             },
                             "parse_error": {
                                 "summary": "Erro no processamento",
                                 "value": {"detail": "Erro ao processar CSV: invalid literal for int()"}
                             }
                         }
                     }
                 }
             },
             401: {
                 "description": "Token de autenticação inválido",
                 "model": ErrorResponse
             }
         })
def import_csv(file: UploadFile = File(..., description="Arquivo CSV com dados de vendas"), db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    try:
        # Ler conteúdo do arquivo
        content = file.file.read()
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in csv_reader:
            # Verificar se produto existe
            produto = db.query(Produto).filter(Produto.nome == row['produto']).first()
            if not produto:
                produto = Produto(
                    nome=row['produto'], 
                    categoria=row.get('categoria', ''), 
                    preco=float(row.get('preco', 0))
                )
                db.add(produto)
                db.flush()  # Para obter o ID
            
            # Criar venda
            venda = Venda(
                data=datetime.strptime(row['data'], '%Y-%m-%d').date(),
                produto_id=produto.id,
                usuario_id=current_user.id,
                quantidade=int(row['quantidade']),
                valor_total=float(row['valor_total'])
            )
            db.add(venda)
        
        db.commit()
        return {"status": "Importação realizada"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao processar CSV: {str(e)}")

@app.get("/metrics",
         response_model=MetricsResponse,
         tags=["Métricas"],
         summary="Obter métricas de vendas do usuário",
         description="""Retorna métricas consolidadas das vendas do usuário logado:
         - Receita total acumulada
         - Ticket médio por venda
         - Produto mais vendido (por quantidade)
         - Evolução mensal da receita
         - Top 5 produtos por receita
         - Vendas agrupadas por categoria
         - Total de vendas realizadas
         - Quantidade de produtos únicos vendidos
         
         Todas as métricas são filtradas pelos dados do usuário autenticado.""",
         responses={
             401: {
                 "description": "Token de autenticação inválido",
                 "model": ErrorResponse
             }
         })
def get_metrics(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    receita_total = db.query(func.sum(Venda.valor_total)).filter(Venda.usuario_id == current_user.id).scalar() or 0
    ticket_medio = db.query(func.avg(Venda.valor_total)).filter(Venda.usuario_id == current_user.id).scalar() or 0
    
    produto_mais_vendido = db.query(Produto.nome, func.sum(Venda.quantidade).label('qtd'))\
        .join(Venda).filter(Venda.usuario_id == current_user.id)\
        .group_by(Produto.id).order_by(func.sum(Venda.quantidade).desc()).first()
    
    evolucao = db.query(func.strftime('%Y-%m', Venda.data).label('mes'), func.sum(Venda.valor_total))\
        .filter(Venda.usuario_id == current_user.id)\
        .group_by('mes').order_by('mes').all()
    
    top_produtos = db.query(
        Produto.nome, 
        func.sum(Venda.valor_total).label('receita'),
        func.sum(Venda.quantidade).label('quantidade')
    ).join(Venda).filter(Venda.usuario_id == current_user.id)\
     .group_by(Produto.id).order_by(func.sum(Venda.valor_total).desc()).limit(5).all()
    
    vendas_categoria = db.query(
        Produto.categoria,
        func.sum(Venda.valor_total).label('receita'),
        func.count(Venda.id).label('num_vendas')
    ).join(Venda).filter(Venda.usuario_id == current_user.id)\
     .group_by(Produto.categoria).all()
    
    total_vendas = db.query(func.count(Venda.id)).filter(Venda.usuario_id == current_user.id).scalar() or 0
    produtos_unicos = db.query(func.count(func.distinct(Produto.id)))\
        .join(Venda).filter(Venda.usuario_id == current_user.id).scalar() or 0
    
    return {
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "produto_mais_vendido": produto_mais_vendido[0] if produto_mais_vendido else None,
        "evolucao_mensal": [{"mes": m, "receita": v} for m, v in evolucao],
        "top_produtos": [{"nome": nome, "receita": rec, "quantidade": qtd} for nome, rec, qtd in top_produtos],
        "vendas_categoria": [{"categoria": cat, "receita": rec, "num_vendas": num} for cat, rec, num in vendas_categoria],
        "total_vendas": total_vendas,
        "produtos_unicos": produtos_unicos
    }

@app.get("/forecast",
         response_model=List[ForecastOut],
         tags=["Machine Learning"],
         summary="Obter previsões de Machine Learning",
         description="""Retorna as previsões geradas pelo modelo de Machine Learning.
         
         As previsões incluem:
         - ID e nome do produto
         - Data prevista para a demanda
         - Quantidade/receita prevista (qtd_prevista representa receita)
         - Intervalo de confiança da previsão
         
         **Importante**: Execute '/run-ml' antes para gerar novas previsões.
         Retorna apenas previsões para produtos que o usuário já vendeu.""",
         responses={
             200: {
                 "description": "Lista de previsões encontradas",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "produto_id": 1,
                                 "produto_nome": "Notebook Dell",
                                 "data_prevista": "2025-01-01",
                                 "qtd_prevista": 3000.0,
                                 "intervalo_conf": "[2500.0,3500.0]"
                             },
                             {
                                 "produto_id": 2,
                                 "produto_nome": "Mouse Logitech",
                                 "data_prevista": "2025-01-01",
                                 "qtd_prevista": 900.0,
                                 "intervalo_conf": "[800.0,1000.0]"
                             }
                         ]
                     }
                 }
             },
             401: {
                 "description": "Token de autenticação inválido",
                 "model": ErrorResponse
             }
         })
def get_forecast(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    forecasts = (
        db.query(Forecast, Produto.nome.label("produto_nome"))
          .join(Produto, Forecast.produto_id == Produto.id)
          .join(Venda, Venda.produto_id == Produto.id)
          .filter(Venda.usuario_id == current_user.id)
          .all()
    )
    return [
        {
            "produto_id": f.Forecast.produto_id if hasattr(f, 'Forecast') else f[0].produto_id,
            "produto_nome": (f.produto_nome if hasattr(f, 'produto_nome') else f[1]),
            "data_prevista": (f.Forecast.data_prevista if hasattr(f, 'Forecast') else f[0].data_prevista),
            "qtd_prevista": (f.Forecast.qtd_prevista if hasattr(f, 'Forecast') else f[0].qtd_prevista),
            "intervalo_conf": (f.Forecast.intervalo_conf if hasattr(f, 'Forecast') else f[0].intervalo_conf)
        }
        for f in forecasts
    ]

@app.post("/run-ml",
         response_model=MLResponse,
         tags=["Machine Learning"],
         summary="Executar modelo de Machine Learning",
         description="""Executa o algoritmo de Machine Learning para gerar previsões de demanda.
         
         O processo:
         1. Remove previsões antigas do banco de dados
         2. Executa o script ML (ml/ml.py) via subprocess
         3. O script analisa os dados de vendas e gera novas previsões
         4. As previsões são salvas automaticamente no banco
         
         **Tempo estimado**: 30-60 segundos
         **Pré-requisito**: Ter dados de vendas importados
         
         Após a execução, use GET /forecast para visualizar os resultados.""",
         responses={
             200: {
                 "description": "Resultado da execução do ML",
                 "content": {
                     "application/json": {
                         "examples": {
                             "success": {
                                 "summary": "Execução bem-sucedida",
                                 "value": {
                                     "status": "success",
                                     "message": "ML executado com sucesso"
                                 }
                             },
                             "error": {
                                 "summary": "Erro na execução",
                                 "value": {
                                     "status": "error",
                                     "message": "Erro: Dados insuficientes para treinamento"
                                 }
                             }
                         }
                     }
                 }
             },
             401: {
                 "description": "Token de autenticação inválido",
                 "model": ErrorResponse
             }
         })
def run_ml_forecast(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    try:
        db.query(Forecast).delete()
        db.commit()
        
        import subprocess
        import sys
        import os
        
        ml_script = os.path.join(os.path.dirname(__file__), "..", "ml", "ml.py")
        result = subprocess.run([sys.executable, ml_script], capture_output=True, text=True)
        
        if result.returncode == 0:
            return {"status": "success", "message": "ML executado com sucesso"}
        else:
            return {"status": "error", "message": f"Erro: {result.stderr}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    if not db.query(Usuario).filter(Usuario.email == "admin@admin.com").first():
        user = Usuario(email="admin@admin.com", senha_hash=get_password_hash("admin"))
        db.add(user)
        db.commit()
    db.close()