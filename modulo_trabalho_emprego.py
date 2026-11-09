import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def render_trabalho_emprego():
    st.header("💼 Painel de Emprego, Desocupação e Informalidade")
    st.subheader("Consultoria Estratégica para a Ministra do Trabalho e Sebrae")

  
    uploaded_file = st.file_uploader("Carregue a base de dados da PNAD Contínua (CSV ou XLSX)", type=["csv", "xlsx"], key="trabalho_upload")
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
       
            st.sidebar.markdown("### Filtros de Trabalho & Emprego")
            uf_selecionada = st.sidebar.multiselect("Selecione as UFs para Análise", options=sorted(df['UF'].unique()), default=sorted(df['UF'].unique())[:5])
            setor_economico = st.sidebar.selectbox("Setor Econômico", options=["Todos", "Agropecuária", "Indústria", "Serviços"])
            escolaridade = st.sidebar.selectbox("Nível de Escolaridade", options=["Todos", "Fundamental Incompleto", "Médio Completo", "Superior Completo"])
            
        
            df_comparativo = df[(df['UF'].isin(uf_selecionada)) & (df['Ano'].isin([2012, 2022]))]
            if setor_economico != "Todos":
                df_comparativo = df_comparativo[df_comparativo['Setor'] == setor_economico]
            if escolaridade != "Todos":
                df_comparativo = df_comparativo[df_comparativo['Escolaridade'] == escolaridade]

          
            valores_taxa = df_comparativo['Taxa_Desocupacao'].dropna().to_numpy()
            
            if len(valores_taxa) > 0:
                media = np.mean(valores_taxa)
                mediana = np.median(valores_taxa)
                
              
                q1 = np.percentile(valores_taxa, 25)
                q3 = np.percentile(valores_taxa, 75)
                iqr = q3 - q1
                desvio_padrao = np.std(valores_taxa, ddof=1) if len(valores_taxa) > 1 else 0.0
                amplitude = np.max(valores_taxa) - np.min(valores_taxa)
                
              
                limite_sup = q3 + (1.5 * iqr)
                limite_inf = q1 - (1.5 * iqr)
                outliers = df_comparativo[(df_comparativo['Taxa_Desocupacao'] > limite_sup) | (df_comparativo['Taxa_Desocupacao'] < limite_inf)]

             
                st.markdown("### 📊 Indicadores Estatísticos Prontos para Tomada de Decisão")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Média de Desocupação", f"{media:.2f}%")
                col2.metric("Mediana da Taxa", f"{mediana:.2f}%")
                col3.metric("Desvio Padrão (Variação)", f"{desvio_padrao:.2f}%")
                col4.metric("Amplitude Territorial", f"{amplitude:.2f}%")

              
                st.markdown("#### 🎯 Insights de Negócio para o Governo")
                df_2012 = df_comparativo[df_comparativo['Ano'] == 2012].set_index('UF')['Taxa_Desocupacao']
                df_2022 = df_comparativo[df_comparativo['Ano'] == 2022].set_index('UF')['Taxa_Desocupacao']
                reducao = (df_2012 - df_2022).dropna()
                
                if not reducao.empty:
                    melhor_estado = reducao.idxmax()
                    valor_reducao = reducao.max()
                    st.success(f"🏆 **Redução Histórica:** O estado que registrou a maior redução na população desempregada entre 2012 e 2022 foi **{melhor_estado}**, com queda de **{valor_reducao:.2f} pontos percentuais** na taxa.")
                
                if len(outliers) > 0:
                    st.warning(f"⚠️ **Estados Outliers:** Detectou-se comportamento anômalo de desocupação fora dos limites em: {', '.join(outliers['UF'].unique())}.")
                
               
                st.markdown("### 📈 Gráficos Comparativos Executivos")
                tab1, tab2 = st.tabs(["Comparação Temporal e Gênero", "Rendimento e Assimetria"])
                
                with tab1:
                  
                    fig_formalidade = px.bar(df_comparativo[df_comparativo['Ano'] == 2022], x='UF', y=['Taxa_Formalidade', 'Taxa_Informalidade'],
                                             title='Taxas de Formalidade vs. Informalidade por Estado (Ano Base: 2022)',
                                             barmode='group')
                    st.plotly_chart(fig_formalidade, use_container_width=True)
                    
                  
                    fig_genero = px.bar(df_comparativo, x='UF', y='Taxa_Desocupacao', color='Ano', facet_col='Sexo',
                                        title='Taxa de Desocupação por Gênero e Ano (2012 x 2022)', barmode='group')
                    st.plotly_chart(fig_genero, use_container_width=True)
                    
                with tab2:
                    
                    fig_hist = px.histogram(df_comparativo, x='Rendimento_Medio', color='Ano', nbins=20,
                                            title='Histograma de Rendimento do Trabalho (Assimetria Média vs Mediana)')
                    st.plotly_chart(fig_hist, use_container_width=True)
                    st.info("💡 *Nota de Assimetria:* A cauda longa à direita no histograma demonstra concentração de renda, justificando por que a Média Salarial é artificialmente superior à Mediana real dos trabalhadores brasileiros.")

            else:
                st.error("Dados insuficientes para calcular métricas com os filtros ativos.")

           
            st.markdown("---")
            st.markdown("### 📰 Monitor do Mercado de Trabalho")
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                st.markdown("🔗 **[PNAD Contínua: Informalidade atinge patamares recordes em setores de serviços](https://ibge.gov.br)**")
                st.caption("Ministério do Trabalho estuda incentivos de microcrédito junto ao Sebrae para acelerar a formalização de MEIs.")
            with col_n2:
                st.markdown("🔗 **[Dados do CAGED mostram expansão do emprego formal na Indústria](https://www.gov.br)**")
                st.caption("Apesar da criação de vagas com carteira assinada, disparidade salarial entre gêneros permanece estagnada.")
                
        except Exception as e:
            st.error(f"Erro ao ler ou tratar o arquivo: {e}")
    else:
        st.info("Aguardando upload da base de dados microdados da PNAD Contínua / IBGE.")
