import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time
import os

# Configuração da API baseada no ambiente
API_URL = os.getenv("API_URL", "http://localhost:8001")  

def format_number(value, decimals=2):
    """Formatar números no padrão brasileiro (ponto para milhares, vírgula para decimais)"""
    if value is None:
        return "0,00"
    if decimals == 0:
        return f"{value:,.0f}".replace(',', '.')
    else:
        return f"{value:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def login():
    st.title("🚀 Sistema de Vendas e Previsões")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Cadastro"])
    
    with tab1:
        st.subheader("Entrar no sistema")
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔒 Senha", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Entrar", key="login_btn", type="primary"):
                try:
                    resp = requests.post(f"{API_URL}/auth/login", data={"username": email, "password": password})
                    if resp.status_code == 200:
                        st.session_state['token'] = resp.json()['access_token']
                        st.success("✅ Login realizado!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha inválidos")
                except Exception as e:
                    st.error(f"❌ Erro de conexão: {str(e)}")
        
        with col2:
            st.info("**Admin padrão:**\n📧 admin@admin.com\n🔒 admin")
    
    with tab2:
        st.subheader("Criar nova conta")
        new_email = st.text_input("📧 Email", key="register_email")
        new_password = st.text_input("🔒 Senha", type="password", key="register_password")
        confirm_password = st.text_input("🔒 Confirmar senha", type="password", key="confirm_password")
        
        if st.button("📝 Cadastrar", key="register_btn", type="primary"):
            if new_password != confirm_password:
                st.error("❌ Senhas não coincidem!")
            elif len(new_password) < 4:
                st.error("❌ Senha deve ter pelo menos 4 caracteres!")
            else:
                try:
                    resp = requests.post(f"{API_URL}/auth/register", json={"email": new_email, "password": new_password})
                    if resp.status_code == 200:
                        st.success("✅ Usuário cadastrado com sucesso! Faça login.")
                    else:
                        st.error("❌ Erro ao cadastrar usuário. Email pode já estar em uso.")
                except Exception as e:
                    st.error(f"❌ Erro de conexão: {str(e)}")

def upload_csv(token):
    st.header("📊 Importar Dados de Vendas")
    
    st.info("📋 **Formato esperado do CSV:**\n`data, produto, categoria, preco, quantidade, valor_total`")
    
    with st.expander("📄 Ver exemplo de dados"):
        exemplo_data = {
            'data': ['2024-01-15', '2024-01-20', '2024-02-10'],
            'produto': ['Notebook Dell', 'Mouse Logitech', 'Teclado Mecânico'],
            'categoria': ['Eletrônicos', 'Periféricos', 'Periféricos'],
            'preco': [2500.00, 150.00, 300.00],
            'quantidade': [2, 5, 3],
            'valor_total': [5000.00, 750.00, 900.00]
        }
        st.dataframe(pd.DataFrame(exemplo_data))
    
    file = st.file_uploader("📁 Escolha o arquivo CSV", type=["csv"])
    if file:
        try:
            preview_df = pd.read_csv(file)
            st.subheader("👀 Preview dos dados")
            st.dataframe(preview_df.head())
            
            if st.button("🚀 Importar Dados", type="primary"):
                files = {"file": (file.name, file.getvalue())}
                headers = {"Authorization": f"Bearer {token}"}
                
                with st.spinner("⏳ Importando dados..."):
                    resp = requests.post(f"{API_URL}/import", files=files, headers=headers)
                    if resp.status_code == 200:
                        st.success("✅ Importação realizada com sucesso!")
                        st.balloons()
                        st.info("💡 Agora vá para o Dashboard e execute o ML para gerar previsões!")
                    else:
                        st.error("❌ Erro ao importar dados")
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {str(e)}")

def show_dashboard(token):
    st.title("📊 Dashboard de Vendas e Previsões ML")
    headers = {"Authorization": f"Bearer {token}"}
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("🤖 Executar ML", type="primary"):
            with st.spinner("🔄 Executando modelo de Machine Learning..."):
                try:
                    response = requests.post(f"{API_URL}/run-ml", headers=headers, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.success("✅ ML executado com sucesso!")
                            st.info("🔄 Recarregando dados...")
                            time.sleep(2) 
                            st.rerun()
                        else:
                            st.error(f"❌ Erro no ML: {result.get('message', 'Erro desconhecido')}")
                            st.code(result.get('message', ''), language="text")
                    else:
                        st.error(f"❌ Erro HTTP {response.status_code}")
                        try:
                            error_detail = response.json()
                            st.code(str(error_detail), language="json")
                        except:
                            st.code(response.text, language="text")
                            
                except requests.exceptions.Timeout:
                    st.error("⏰ Timeout: ML está demorando muito. Tente novamente.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Erro de conexão: Verifique se o backend está rodando")
                except Exception as e:
                    st.error(f"❌ Erro inesperado: {str(e)}")
                    st.code(str(e), language="text")
    
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        if auto_refresh:
            st.rerun()
    
    with col4:
        st.caption("📅 Última atualização: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    try:
        with st.spinner("📡 Carregando dados..."):
            metrics_resp = requests.get(f"{API_URL}/metrics", headers=headers)
            if metrics_resp.status_code != 200:
                st.error(f"❌ Erro métricas HTTP {metrics_resp.status_code}")
                st.text(metrics_resp.text)
                return
            if not metrics_resp.text.strip():
                st.error("❌ Resposta vazia em /metrics")
                return
            metrics = metrics_resp.json()

            forecast_resp = requests.get(f"{API_URL}/forecast", headers=headers)
            if forecast_resp.status_code != 200:
                st.warning(f"⚠️ Forecast HTTP {forecast_resp.status_code}")
                st.text(forecast_resp.text)
                forecast = []
            elif not forecast_resp.text.strip():
                st.warning("⚠️ Forecast vazio")
                forecast = []
            else:
                forecast = forecast_resp.json()
    except Exception as e:
        st.error(f"❌ Erro ao conectar com a API: {str(e)}")
        st.info(f"🔧 Verifique se o backend está rodando em {API_URL}")
        return
    
    st.header("📈 Indicadores Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        receita_total = metrics.get('receita_total', 0)
        crescimento_receita = 0
        if metrics.get('evolucao_mensal') and len(metrics['evolucao_mensal']) >= 2:
            atual = metrics['evolucao_mensal'][-1]['receita']
            anterior = metrics['evolucao_mensal'][-2]['receita']
            crescimento_receita = ((atual - anterior) / anterior) * 100 if anterior > 0 else 0
        
        st.metric(
            label="💰 Receita Total", 
            value=f"R$ {format_number(receita_total)}",
            delta=f"{crescimento_receita:+.1f}%" if crescimento_receita != 0 else "Primeiro período",
            delta_color="normal"
        )
    
    with col2:
        ticket_medio = metrics.get('ticket_medio', 0)
        variacao_ticket = 0
        if metrics.get('evolucao_mensal') and len(metrics['evolucao_mensal']) >= 2:
            vendas_atual = metrics.get('total_vendas', 1)
            receita_atual = metrics['evolucao_mensal'][-1]['receita']
            ticket_atual = receita_atual / vendas_atual if vendas_atual > 0 else 0
            # Simulando variação baseada na tendência
            variacao_ticket = (ticket_atual / ticket_medio - 1) * 100 if ticket_medio > 0 else 0
        
        st.metric(
            label="🎯 Ticket Médio", 
            value=f"R$ {format_number(ticket_medio)}",
            delta=f"{variacao_ticket:+.1f}%" if variacao_ticket != 0 else "Estável",
            delta_color="normal"
        )
    
    with col3:
        total_vendas = metrics.get('total_vendas', 0)
        meta_vendas = 200
        progresso_vendas = (total_vendas / meta_vendas) * 100 if meta_vendas > 0 else 0
        
        st.metric(
            label="🛒 Total de Vendas", 
            value=format_number(total_vendas, 0),
            delta=f"{progresso_vendas:.0f}% da meta ({meta_vendas})",
            delta_color="normal"
        )
    
    with col4:
        produtos_unicos = metrics.get('produtos_unicos', 0)
        produto_destaque = metrics.get('produto_mais_vendido', 'N/A')
        
        st.metric(
            label="📦 Produtos Únicos", 
            value=f"{produtos_unicos}",
            delta=f"⭐ Top: {produto_destaque[:15]}{'...' if len(str(produto_destaque)) > 15 else ''}",
            delta_color="off"
        )
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Evolução da Receita Mensal")
        if metrics.get('evolucao_mensal'):
            df_evolucao = pd.DataFrame(metrics['evolucao_mensal'])
            
            fig_linha = px.line(
                df_evolucao, 
                x='mes', 
                y='receita',
                title="📈 Receita por Mês",
                markers=True,
                color_discrete_sequence=['#2E8B57']
            )
            fig_linha.update_layout(
                xaxis_title="Mês",
                yaxis_title="Receita (R$)",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.info("📊 Nenhum dado de vendas encontrado. Importe dados primeiro!")
    
    with col2:
        st.subheader("🔮 Previsões de Receita ML")
        if forecast:
            df_forecast = pd.DataFrame(forecast)
            df_forecast['data_prevista'] = pd.to_datetime(df_forecast['data_prevista'])
            if 'produto_nome' in df_forecast.columns:
                df_forecast['produto_exibicao'] = df_forecast.apply(
                    lambda r: r['produto_nome'] if pd.notna(r.get('produto_nome')) and str(r.get('produto_nome')).strip() != '' else f"ID {r['produto_id']}", axis=1
                )
            else:
                df_forecast['produto_exibicao'] = df_forecast['produto_id'].apply(lambda x: f"ID {x}")
            df_receita_mes = df_forecast.groupby('data_prevista')['qtd_prevista'].sum().reset_index()
            df_receita_mes.columns = ['data_prevista', 'receita_prevista']
            
            fig_forecast = px.bar(
                df_receita_mes, 
                x='data_prevista', 
                y='receita_prevista',
                title="💰 Previsão de Receita Mensal",
                color='receita_prevista',
                color_continuous_scale='viridis',
                text='receita_prevista'
            )
            fig_forecast.update_traces(
                texttemplate='R$ %{text:,.0f}', 
                textposition='outside'
            )
            fig_forecast.update_layout(
                xaxis_title="Mês Previsto",
                yaxis_title="Receita Prevista (R$)",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            st.subheader("🏆 Produtos Top Previstos")
            
            produto_totals = df_forecast.groupby('produto_exibicao')['qtd_prevista'].sum().reset_index()
            if not produto_totals.empty:
                top_produto_nome = produto_totals.loc[produto_totals['qtd_prevista'].idxmax(), 'produto_exibicao']
                top_receita = produto_totals['qtd_prevista'].max()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "🥇 Produto Destaque", 
                        top_produto_nome,
                        f"R$ {format_number(top_receita)} prev."
                    )
                with col_b:
                    top_3 = produto_totals.nlargest(3, 'qtd_prevista')
                    st.write("**Top 3 Produtos:**")
                    for i, row in top_3.iterrows():
                        st.write(f"{i+1}º {row['produto_exibicao']}: R$ {format_number(row['qtd_prevista'])}")
        else:
            st.warning("⚠️ Nenhuma previsão encontrada!")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🚀 Executar ML Agora", key="ml_btn_2"):
                    with st.spinner("🔄 Executando ML..."):
                        try:
                            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                            response = requests.post(f"{API_URL}/run-ml", headers=headers, timeout=60)
                            if response.status_code == 200:
                                result = response.json()
                                if result["status"] == "success":
                                    st.success("✅ ML executado!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result.get('message', 'Erro')}")
                            else:
                                st.error("❌ Erro HTTP")
                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)}")
            with col_b:
                st.info("💡 Execute o ML para ver previsões de receita e produtos top!")
    
    st.divider()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Vendas por Categoria", 
        "📈 Análise de Tendências", 
        "🎯 Previsões ML Detalhadas", 
        "🏆 Top Produtos",
        "📋 Dados Técnicos"
    ])
    
    with tab1:
        st.subheader("🏷️ Distribuição por Categoria")
        
        if metrics.get('vendas_categoria'):
            vendas_cat = metrics['vendas_categoria']
            categorias = [item['categoria'] or 'Sem categoria' for item in vendas_cat]
            receitas = [item['receita'] for item in vendas_cat]
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pizza = px.pie(
                    values=receitas, 
                    names=categorias,
                    title="🥧 Participação por Categoria",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col2:
                df_cat = pd.DataFrame(vendas_cat)
                df_cat['categoria'] = df_cat['categoria'].fillna('Sem categoria')
                df_cat['Participação %'] = df_cat['receita'].apply(lambda x: f"{(x/sum(receitas)*100):.1f}%")
                df_cat['receita'] = df_cat['receita'].apply(lambda x: f"R$ {x:,.2f}")
                df_cat = df_cat.rename(columns={
                    'categoria': 'Categoria',
                    'receita': 'Receita',
                    'num_vendas': 'Qtd Vendas'
                })
                st.dataframe(df_cat, use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado de categoria encontrado")
    
    with tab2:
        st.subheader("📈 Análise de Crescimento e Tendências")
        
        if metrics.get('evolucao_mensal'):
            df_evolucao = pd.DataFrame(metrics['evolucao_mensal'])
            
            fig_area = px.area(
                df_evolucao, 
                x='mes', 
                y='receita',
                title="📊 Tendência de Crescimento da Receita",
                color_discrete_sequence=['#FF6B6B']
            )
            fig_area.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_area, use_container_width=True)
            
            if len(df_evolucao) > 1:
                crescimento = ((df_evolucao['receita'].iloc[-1] - df_evolucao['receita'].iloc[0]) / df_evolucao['receita'].iloc[0]) * 100
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📈 Crescimento Total", f"{crescimento:.1f}%")
                with col2:
                    st.metric("📊 Média Mensal", f"R$ {df_evolucao['receita'].mean():,.2f}")
                with col3:
                    st.metric("🎯 Melhor Mês", f"R$ {df_evolucao['receita'].max():,.2f}")
            
            # Projeção simples
            st.subheader("🔮 Projeção Simples (Próximos 3 meses)")
            if len(df_evolucao) >= 2:
                media_crescimento = df_evolucao['receita'].pct_change().mean()
                ultimo_valor = df_evolucao['receita'].iloc[-1]
                
                projecoes = []
                for i in range(1, 4):
                    valor_projetado = ultimo_valor * (1 + media_crescimento) ** i
                    projecoes.append(valor_projetado)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📅 Mês +1", f"R$ {projecoes[0]:,.2f}")
                with col2:
                    st.metric("📅 Mês +2", f"R$ {projecoes[1]:,.2f}")
                with col3:
                    st.metric("📅 Mês +3", f"R$ {projecoes[2]:,.2f}")
        else:
            st.info("📊 Dados insuficientes para análise de tendências")
    
    with tab3:
        st.subheader("🤖 Previsões Detalhadas: Receita e Top Produtos")
        
        if forecast:
            df_forecast = pd.DataFrame(forecast)
            df_forecast['data_prevista'] = pd.to_datetime(df_forecast['data_prevista'])
            
            # === ANÁLISE DE RECEITA TOTAL ===
            st.subheader("💰 Análise de Receita Prevista")
            
            # Agrupar receita por mês
            df_receita_mensal = df_forecast.groupby('data_prevista')['qtd_prevista'].sum().reset_index()
            df_receita_mensal.columns = ['data_prevista', 'receita_total']
            
            # Gráfico combinado: Histórico + Previsão de Receita
            fig_combined = go.Figure()
            
            # Dados históricos de receita
            if metrics.get('evolucao_mensal'):
                df_hist = pd.DataFrame(metrics['evolucao_mensal'])
                fig_combined.add_trace(go.Scatter(
                    x=df_hist['mes'],
                    y=df_hist['receita'],
                    mode='lines+markers',
                    name='📊 Receita Histórica',
                    line=dict(color='#2E8B57', width=3),
                    marker=dict(size=8)
                ))
            
            # Previsões de receita
            fig_combined.add_trace(go.Scatter(
                x=df_receita_mensal['data_prevista'],
                y=df_receita_mensal['receita_total'],
                mode='lines+markers',
                name='💰 Receita Prevista',
                line=dict(color='#FFD700', width=3, dash='dash'),
                marker=dict(size=12, symbol='diamond')
            ))
            
            fig_combined.update_layout(
                title="📈 Evolução da Receita: Histórico vs Previsão ML",
                xaxis_title="Período",
                yaxis_title="Receita (R$)",
                legend=dict(x=0, y=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_combined, use_container_width=True)
            
            # === ANÁLISE POR PRODUTO ===
            st.subheader("🏆 Ranking de Produtos Previstos")
            
            # Calcular receita total prevista por produto
            # Garantir coluna de exibição
            if 'produto_exibicao' not in df_forecast.columns:
                df_forecast['produto_exibicao'] = df_forecast['produto_id'].apply(lambda x: f"ID {x}")
            df_produtos = df_forecast.groupby('produto_exibicao').agg({
                'qtd_prevista': 'sum',
                'data_prevista': 'count'
            }).reset_index()
            df_produtos.columns = ['produto_exibicao', 'receita_total_prevista', 'num_previsoes']
            df_produtos = df_produtos.sort_values('receita_total_prevista', ascending=False)
            
            # Gráfico de barras dos top produtos
            fig_produtos = px.bar(
                df_produtos.head(10),
                x='produto_exibicao',
                y='receita_total_prevista',
                title="🥇 Top 10 Produtos por Receita Prevista",
                color='receita_total_prevista',
                color_continuous_scale='plasma',
                text='receita_total_prevista'
            )
            fig_produtos.update_traces(
                texttemplate='R$ %{text:,.0f}', 
                textposition='outside'
            )
            fig_produtos.update_layout(
                xaxis_title="Produto",
                yaxis_title="Receita Total Prevista (R$)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_produtos, use_container_width=True)
            
            # === TABELAS DETALHADAS ===
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Receita Mensal Prevista")
                df_receita_display = df_receita_mensal.copy()
                df_receita_display['data_prevista'] = df_receita_display['data_prevista'].dt.strftime('%m/%Y')
                df_receita_display['receita_total'] = df_receita_display['receita_total'].apply(
                    lambda x: f"R$ {format_number(x)}"
                )
                df_receita_display = df_receita_display.rename(columns={
                    'data_prevista': 'Mês',
                    'receita_total': 'Receita Prevista'
                })
                st.dataframe(df_receita_display, use_container_width=True)
            
            with col2:
                st.subheader("🏆 Top Produtos Detalhado")
                df_produtos_display = df_produtos.head(5).copy()
                df_produtos_display['receita_total_prevista'] = df_produtos_display['receita_total_prevista'].apply(
                    lambda x: f"R$ {format_number(x)}"
                )
                df_produtos_display = df_produtos_display.rename(columns={
                    'produto_exibicao': 'Produto',
                    'receita_total_prevista': 'Receita Prevista',
                    'num_previsoes': 'Nº Previsões'
                })
                st.dataframe(df_produtos_display, use_container_width=True)
            
            # === ESTATÍSTICAS DAS PREVISÕES ===
            st.subheader("📊 Estatísticas das Previsões ML")
            col1, col2, col3, col4 = st.columns(4)
            
            receita_total_prev = df_receita_mensal['receita_total'].sum()
            receita_media_mensal = df_receita_mensal['receita_total'].mean()
            produto_top_nome = df_produtos.iloc[0]['produto_exibicao'] if not df_produtos.empty else "N/A"
            total_produtos_ativos = len(df_produtos)
            
            with col1:
                st.metric("💰 Receita Total Prevista", f"R$ {format_number(receita_total_prev)}")
            with col2:
                st.metric("📅 Receita Média Mensal", f"R$ {format_number(receita_media_mensal)}")
            with col3:
                st.metric("🥇 Produto Top", str(produto_top_nome))
            with col4:
                st.metric("📦 Produtos Ativos", str(total_produtos_ativos))
        else:
            st.warning("🤖 Nenhuma previsão de ML encontrada!")
            st.info("💡 Execute o Machine Learning para gerar previsões:")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Executar ML", key="ml_btn_tab3"):
                    with st.spinner("🔄 Executando ML..."):
                        try:
                            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                            response = requests.post(f"{API_URL}/run-ml", headers=headers, timeout=60)
                            if response.status_code == 200:
                                result = response.json()
                                if result["status"] == "success":
                                    st.success("✅ ML executado com sucesso!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result.get('message', 'Erro')}")
                            else:
                                st.error("❌ Erro HTTP")
                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)}")
            with col2:
                st.info("**Sobre as previsões:**\n- 💰 Receita futura por produto\n- 🏆 Ranking de produtos top\n- 📈 Tendências de crescimento")
    
    with tab4:
        st.subheader("🏆 Top Produtos e Performance")
        
        if metrics.get('top_produtos'):
            top_produtos = pd.DataFrame(metrics['top_produtos'])
            
            # Gráfico de barras horizontal
            fig_bar_h = px.bar(
                top_produtos,
                x='receita',
                y='nome',
                orientation='h',
                title="💰 Top Produtos por Receita",
                color='receita',
                color_continuous_scale='viridis',
                text='receita'
            )
            fig_bar_h.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
            fig_bar_h.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar_h, use_container_width=True)
            
            # Gráfico de barras vertical para quantidade
            fig_bar_v = px.bar(
                top_produtos,
                x='nome',
                y='quantidade',
                title="📦 Top Produtos por Quantidade Vendida",
                color='quantidade',
                color_continuous_scale='plasma'
            )
            fig_bar_v.update_xaxes(tickangle=45)
            fig_bar_v.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar_v, use_container_width=True)
            
            # Tabela detalhada
            st.subheader("📊 Tabela Detalhada dos Top Produtos")
            top_produtos_display = top_produtos.copy()
            top_produtos_display['receita'] = top_produtos_display['receita'].apply(lambda x: f"R$ {x:,.2f}")
            top_produtos_display = top_produtos_display.rename(columns={
                'nome': 'Produto',
                'receita': 'Receita Total',
                'quantidade': 'Qtd Vendida'
            })
            st.dataframe(top_produtos_display, use_container_width=True)
        else:
            st.info("📦 Nenhum produto encontrado")
    
    with tab5:
        st.subheader("📋 Dados Técnicos e Debug")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔧 Métricas da API:**")
            with st.expander("Ver JSON completo"):
                st.json(metrics)
        
        with col2:
            st.write("**🤖 Previsões ML:**")
            if forecast:
                with st.expander("Ver JSON completo"):
                    st.json(forecast)
            else:
                st.warning("Nenhuma previsão disponível")
        
        # Informações do sistema
        st.subheader("ℹ️ Informações do Sistema")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**API URL:** {API_URL}")
        with col2:
            st.info(f"**Total Endpoints:** 5")
        with col3:
            st.info(f"**Última sincronização:** {datetime.now().strftime('%H:%M:%S')}")
    
    # === ALERTAS E INSIGHTS ===
    st.divider()
    st.header("🚨 Alertas e Insights Inteligentes")
    
    alert_col1, alert_col2 = st.columns(2)
    
    with alert_col1:
        st.subheader("📊 Status do Sistema")
        
        # Alert de meta de receita
        receita_meta = 50000
        if metrics.get('receita_total', 0) > receita_meta:
            st.success(f"✅ Meta de receita (R$ {receita_meta:,.2f}) ATINGIDA!")
        else:
            restante = receita_meta - metrics.get('receita_total', 0)
            st.warning(f"⚠️ Faltam R$ {restante:,.2f} para atingir a meta")
        
        # Alert de ML
        if forecast:
            st.success(f"✅ {len(forecast)} previsões ML disponíveis")
        else:
            st.error("❌ Previsões ML não executadas")
        
        # Alert de dados
        if metrics.get('total_vendas', 0) > 0:
            st.success(f"✅ {metrics.get('total_vendas', 0)} vendas registradas")
        else:
            st.warning("⚠️ Nenhuma venda registrada. Importe dados!")
    
    with alert_col2:
        st.subheader("💡 Insights e Recomendações")
        
        # Análise de crescimento
        if metrics.get('evolucao_mensal') and len(metrics['evolucao_mensal']) > 2:
            df_temp = pd.DataFrame(metrics['evolucao_mensal'])
            ultimo_mes = df_temp['receita'].iloc[-1]
            penultimo_mes = df_temp['receita'].iloc[-2]
            
            if ultimo_mes > penultimo_mes:
                crescimento_pct = ((ultimo_mes - penultimo_mes) / penultimo_mes) * 100
                st.success(f"📈 Vendas cresceram {crescimento_pct:.1f}% no último mês!")
            else:
                queda_pct = ((penultimo_mes - ultimo_mes) / penultimo_mes) * 100
                st.warning(f"📉 Queda de {queda_pct:.1f}% detectada no último mês")
        
        # Recomendação de produto
        produto_top = metrics.get('produto_mais_vendido', 'produtos populares')
        st.info(f"💡 **Recomendação:** Focar marketing em {produto_top}")
        
        # Recomendação de ML
        if not forecast:
            st.info("🤖 **Dica:** Execute o ML para obter previsões inteligentes de demanda")

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Sistema de Vendas & ML",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        border: 1px solid #404040;
        padding: 1.2rem;
        border-radius: 0.8rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        color: white;
    }
    .stMetric [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        border: 1px solid #404040;
        padding: 1rem;
        border-radius: 0.8rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric label {
        color: #ffffff !important;
        font-weight: 600;
    }
    .stMetric [data-testid="metric-container"] > div {
        color: #ffffff !important;
    }
    /* Tema escuro para métricas */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #404040;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #4CAF50;
        box-shadow: 0 12px 24px rgba(76, 175, 80, 0.3);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Verificar se está logado
    if 'token' not in st.session_state:
        login()
    else:
        # Sidebar com menu
        with st.sidebar:
            st.title("📊 Menu Principal")
            
            menu = st.selectbox(
                "🎯 Escolha uma opção:",
                ["🏠 Dashboard", "📊 Importar Dados", "🚪 Sair"],
                index=0
            )
            
            st.divider()
            st.subheader("ℹ️ Informações")
            st.info("**Usuário logado** ✅")
            st.caption(f"🕐 Sessão ativa desde {datetime.now().strftime('%H:%M')}")
            
            # Links úteis
            st.subheader("🔗 Links Úteis")
            st.markdown("[📖 Documentação API](http://localhost:8000/docs)")
            st.markdown("[🔧 Repositório](https://github.com)")
        
        # Roteamento das páginas
        if menu == "🏠 Dashboard":
            show_dashboard(st.session_state['token'])
        elif menu == "📊 Importar Dados":
            upload_csv(st.session_state['token'])
        elif menu == "🚪 Sair":
            st.session_state.pop('token', None)
            st.success("👋 Logout realizado!")
            st.rerun()

if __name__ == "__main__":
    main()
