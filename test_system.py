#!/usr/bin/env python3
"""
Script para testar o sistema completo
"""
import requests
import json
import time

API_URL = "http://localhost:8000"

def test_system():
    print("🔧 Testando Sistema de Vendas e ML")
    print("=" * 50)
    
    # 1. Testar login
    print("🔐 Testando login...")
    try:
        login_response = requests.post(f"{API_URL}/auth/login", 
                                     data={"username": "admin@admin.com", "password": "admin"})
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print("✅ Login funcionando!")
        else:
            print("❌ Erro no login")
            return
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # 2. Testar métricas
    print("\n📊 Testando métricas...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        metrics_response = requests.get(f"{API_URL}/metrics", headers=headers)
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            print("✅ Métricas funcionando!")
            print(f"   💰 Receita Total: R$ {metrics.get('receita_total', 0):,.2f}")
            print(f"   🛒 Total Vendas: {metrics.get('total_vendas', 0)}")
            print(f"   📦 Produtos Únicos: {metrics.get('produtos_unicos', 0)}")
        else:
            print("❌ Erro nas métricas")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Testar previsões
    print("\n🔮 Testando previsões...")
    try:
        forecast_response = requests.get(f"{API_URL}/forecast", headers=headers)
        if forecast_response.status_code == 200:
            forecasts = forecast_response.json()
            print(f"✅ Previsões funcionando! {len(forecasts)} previsões encontradas")
            if forecasts:
                print("   Exemplo de previsão:")
                for i, f in enumerate(forecasts[:3]):
                    print(f"   📅 {f['data_prevista']}: {f['qtd_prevista']:.2f} unidades")
        else:
            print("❌ Erro nas previsões")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 4. Testar ML
    print("\n🤖 Testando execução do ML...")
    try:
        ml_response = requests.post(f"{API_URL}/run-ml", headers=headers)
        if ml_response.status_code == 200:
            result = ml_response.json()
            if result["status"] == "success":
                print("✅ ML executado com sucesso!")
            else:
                print(f"❌ Erro no ML: {result['message']}")
        else:
            print("❌ Erro na requisição ML")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n🎯 Teste concluído!")
    print("🌐 Frontend: http://localhost:8502")
    print("📖 API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    test_system()
