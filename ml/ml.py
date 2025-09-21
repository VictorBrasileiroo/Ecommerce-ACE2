import pandas as pd
from sqlalchemy import create_engine
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import sys
import os
import numpy as np
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Base, Produto, Venda, Forecast, Usuario
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./db.sqlite3')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def gerar_forecast():
    print("🚀 Iniciando geração de previsões ML para RECEITA e TOP PRODUTOS...")
    db = SessionLocal()
    
    try:
        db.query(Forecast).delete()
        db.commit()
        print("🗑️ Previsões antigas removidas")
        
        print("� Gerando previsão de receita total...")
        
        vendas_mensais = db.query(
            func.strftime('%Y-%m', Venda.data).label('mes'),
            func.sum(Venda.valor_total).label('receita_total')
        ).group_by('mes').order_by('mes').all()
        
        if len(vendas_mensais) >= 2:
            df_receita = pd.DataFrame([
                {'mes': mes, 'receita': float(receita)} 
                for mes, receita in vendas_mensais
            ])
            
            print(f"📊 Encontrados {len(df_receita)} meses de dados de receita")
            
            if len(df_receita) >= 3:
                model = ExponentialSmoothing(
                    df_receita['receita'], 
                    trend='add',
                    seasonal=None,
                    initialization_method='estimated'
                )
                fit = model.fit(optimized=True)
                receita_forecast = fit.forecast(3)
            else:
                crescimento = (df_receita['receita'].iloc[-1] - df_receita['receita'].iloc[0]) / len(df_receita)
                ultima_receita = df_receita['receita'].iloc[-1]
                receita_forecast = [ultima_receita + crescimento * (i+1) for i in range(3)]
            
            print(f"✅ Previsões de receita geradas: {receita_forecast}")
        
        print("🏆 Analisando produtos para prever TOP vendedores...")
        
        produtos = db.query(Produto).all()
        total_forecasts = 0
        
        produto_scores = {}
        
        for produto in produtos:
            vendas = db.query(Venda).filter(Venda.produto_id == produto.id).all()
            
            if not vendas:
                produto_scores[produto.id] = 0
                continue
                
            df_produto = pd.DataFrame([
                {'data': v.data, 'receita': v.valor_total, 'quantidade': v.quantidade} 
                for v in vendas
            ])
            
            df_produto['data'] = pd.to_datetime(df_produto['data'])
            df_mensal = df_produto.groupby(pd.Grouper(key='data', freq='ME')).agg({
                'receita': 'sum',
                'quantidade': 'sum'
            }).reset_index()
            
            df_mensal = df_mensal[df_mensal['receita'] > 0]
            
            if len(df_mensal) == 0:
                produto_scores[produto.id] = 0
                continue
            
            # Calcular score baseado em:
            # 1. Receita média
            # 2. Tendência de crescimento
            # 3. Consistência (menos variação = melhor)
            
            receita_media = df_mensal['receita'].mean()
            
            if len(df_mensal) >= 2:
                # Tendência de crescimento
                crescimento = (df_mensal['receita'].iloc[-1] - df_mensal['receita'].iloc[0]) / df_mensal['receita'].iloc[0]
                # Consistência (inverso do coeficiente de variação)
                consistencia = 1 / (df_mensal['receita'].std() / df_mensal['receita'].mean() + 0.1)
            else:
                crescimento = 0
                consistencia = 1
            
            # Score composto
            score = receita_media * (1 + crescimento) * consistencia
            produto_scores[produto.id] = max(0, score)
            
            print(f"📈 {produto.nome}: Score = {score:.2f} (Receita: R${receita_media:.2f}, Crescimento: {crescimento:.1%})")
        
        # Normalizar scores para probabilidades
        total_score = sum(produto_scores.values())
        if total_score > 0:
            for produto_id in produto_scores:
                produto_scores[produto_id] = produto_scores[produto_id] / total_score
        
        # Gerar previsões para os próximos 3 meses
        for i in range(3):
            data_prevista = datetime.now() + timedelta(days=30*(i+1))
            
            # Receita prevista para o mês (se temos dados)
            if 'receita_forecast' in locals() and i < len(receita_forecast):
                receita_mes = max(0, float(receita_forecast.iloc[i]))  # Usar .iloc para pandas Series
            else:
                # Fallback: usar média das vendas passadas
                receita_media = db.query(func.avg(Venda.valor_total)).scalar() or 1000
                receita_mes = receita_media * 30  # Estimativa mensal
            
            # Distribuir a receita entre produtos baseado nas probabilidades
            for produto_id, probabilidade in produto_scores.items():
                if probabilidade > 0:
                    receita_produto = receita_mes * probabilidade
                    
                    # Intervalo de confiança
                    intervalo_inf = receita_produto * 0.7
                    intervalo_sup = receita_produto * 1.3
                    intervalo_conf = f"R$ {intervalo_inf:.2f} - R$ {intervalo_sup:.2f}"
                    
                    forecast = Forecast(
                        produto_id=produto_id,
                        data_prevista=data_prevista.date(),
                        qtd_prevista=receita_produto,  # Usando campo existente para receita
                        intervalo_conf=intervalo_conf
                    )
                    db.add(forecast)
                    total_forecasts += 1
        
        db.commit()
        
        # Mostrar TOP 3 produtos previstos
        top_produtos = sorted(produto_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"\n🏆 TOP 3 produtos previstos para próximos meses:")
        for i, (produto_id, prob) in enumerate(top_produtos, 1):
            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            print(f"   {i}º {produto.nome}: {prob:.1%} de probabilidade")
        
        print(f"\n✅ ML executado com sucesso! {total_forecasts} previsões de receita geradas")
        
    except Exception as e:
        print(f"❌ Erro geral no ML: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    gerar_forecast()
