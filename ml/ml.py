from sqlalchemy import create_engine
import sys
import os
from datetime import datetime, timedelta
import random
import math
from collections import defaultdict
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
            receitas = [float(receita) for mes, receita in vendas_mensais]
            
            print(f"📊 Encontrados {len(receitas)} meses de dados de receita")
            
            if len(receitas) >= 3:
                # Algoritmo simples de suavização exponencial
                alpha = 0.3  # Fator de suavização
                forecast = []
                s = receitas[0]  # Valor inicial
                
                # Calcular suavização para dados históricos
                for r in receitas[1:]:
                    s = alpha * r + (1 - alpha) * s
                
                # Gerar previsões futuras
                tendencia = (receitas[-1] - receitas[0]) / len(receitas)
                for i in range(3):
                    projecao = s + tendencia * (i + 1)
                    forecast.append(max(0, projecao))
                
                receita_forecast = forecast
            else:
                # Previsão simples baseada em crescimento linear
                crescimento = (receitas[-1] - receitas[0]) / len(receitas)
                ultima_receita = receitas[-1]
                receita_forecast = [max(0, ultima_receita + crescimento * (i+1)) for i in range(3)]
            
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
                
            # Processar vendas sem pandas - agrupar por mês
            vendas_mensais = defaultdict(lambda: {'receita': 0, 'quantidade': 0})
            
            for venda in vendas:
                mes_key = f"{venda.data.year}-{venda.data.month:02d}"
                vendas_mensais[mes_key]['receita'] += venda.valor_total
                vendas_mensais[mes_key]['quantidade'] += venda.quantidade
            
            # Converter para lista ordenada
            meses_ordenados = sorted(vendas_mensais.keys())
            receitas_mensais = [vendas_mensais[mes]['receita'] for mes in meses_ordenados if vendas_mensais[mes]['receita'] > 0]
            
            if len(receitas_mensais) == 0:
                produto_scores[produto.id] = 0
                continue
            
            # Calcular score baseado em:
            # 1. Receita média
            # 2. Tendência de crescimento
            # 3. Consistência (menos variação = melhor)
            
            receita_media = sum(receitas_mensais) / len(receitas_mensais)
            
            if len(receitas_mensais) >= 2:
                # Tendência de crescimento
                crescimento = (receitas_mensais[-1] - receitas_mensais[0]) / receitas_mensais[0]
                # Consistência (inverso do coeficiente de variação)
                variancia = sum((x - receita_media) ** 2 for x in receitas_mensais) / len(receitas_mensais)
                desvio_padrao = math.sqrt(variancia)
                coef_variacao = desvio_padrao / receita_media if receita_media > 0 else 1
                consistencia = 1 / (coef_variacao + 0.1)
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
                receita_mes = max(0, float(receita_forecast[i]))  # Usar índice da lista
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
