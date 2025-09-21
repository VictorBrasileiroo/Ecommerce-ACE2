from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import Base, Usuario, Produto, Venda, Forecast
from .auth import router as auth_router, get_current_user, get_password_hash
from .database import get_db, engine, SessionLocal
import pandas as pd
import io
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/import")
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))
    for _, row in df.iterrows():
        produto = db.query(Produto).filter_by(nome=row['produto']).first()
        if not produto:
            produto = Produto(nome=row['produto'], categoria=row.get('categoria', ''), preco=row.get('preco', 0))
            db.add(produto)
            db.commit()
            db.refresh(produto)
        venda = Venda(
            data=datetime.strptime(row['data'], '%Y-%m-%d'),
            produto_id=produto.id,
            usuario_id=current_user.id,  # Associar ao usuário logado
            quantidade=row['quantidade'],
            valor_total=row['valor_total']
        )
        db.add(venda)
    db.commit()
    return {"status": "Importação realizada"}

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # Filtrar todas as consultas por usuário
    receita_total = db.query(func.sum(Venda.valor_total)).filter(Venda.usuario_id == current_user.id).scalar() or 0
    ticket_medio = db.query(func.avg(Venda.valor_total)).filter(Venda.usuario_id == current_user.id).scalar() or 0
    
    # Produto mais vendido do usuário
    produto_mais_vendido = db.query(Produto.nome, func.sum(Venda.quantidade).label('qtd'))\
        .join(Venda).filter(Venda.usuario_id == current_user.id)\
        .group_by(Produto.id).order_by(func.sum(Venda.quantidade).desc()).first()
    
    # Evolução mensal do usuário
    evolucao = db.query(func.strftime('%Y-%m', Venda.data).label('mes'), func.sum(Venda.valor_total))\
        .filter(Venda.usuario_id == current_user.id)\
        .group_by('mes').order_by('mes').all()
    
    # Top 5 produtos por receita do usuário
    top_produtos = db.query(
        Produto.nome, 
        func.sum(Venda.valor_total).label('receita'),
        func.sum(Venda.quantidade).label('quantidade')
    ).join(Venda).filter(Venda.usuario_id == current_user.id)\
     .group_by(Produto.id).order_by(func.sum(Venda.valor_total).desc()).limit(5).all()
    
    # Vendas por categoria do usuário
    vendas_categoria = db.query(
        Produto.categoria,
        func.sum(Venda.valor_total).label('receita'),
        func.count(Venda.id).label('num_vendas')
    ).join(Venda).filter(Venda.usuario_id == current_user.id)\
     .group_by(Produto.categoria).all()
    
    # Estatísticas gerais do usuário
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

@app.get("/forecast")
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

@app.post("/run-ml")
def run_ml_forecast(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    try:
        # Limpar previsões antigas
        db.query(Forecast).delete()
        db.commit()
        
        # Executar ML
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

# Criação de usuário admin padrão (apenas para protótipo)
@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    if not db.query(Usuario).filter_by(email="admin@admin.com").first():
        user = Usuario(email="admin@admin.com", senha_hash=get_password_hash("admin"))
        db.add(user)
        db.commit()
    db.close()
