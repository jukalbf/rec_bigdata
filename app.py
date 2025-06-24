import streamlit as st
from database.mongo_db import MongoDB
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Painel de Gestão Pública - Recife",
    layout="wide",
    initial_sidebar_state="expanded"
)

db = MongoDB()

st.title("🏙️ Painel de Gestão Pública - Recife")
st.markdown("Análise integrada de serviços municipais baseada em dados abertos")

with st.sidebar:
    st.header("Filtros")
    data_inicio = st.date_input("Data Início", value=datetime(2023, 1, 1))
    data_fim = st.date_input("Data Fim", value=datetime.today())

    try:
        bairros = db.get_distinct_values('ocorrencias_seguranca', 'bairro')
        bairros = [b for b in bairros if b is not None]
        bairros.sort()
    except:
        bairros = []

    bairro = st.selectbox("Bairro", ["Todos"] + bairros)

def load_data(collection_name):
    return pd.DataFrame(db.get_data(collection_name))

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Limpeza Urbana",
    "🏗️ Obras e Licenciamento",
    "👮 Segurança Pública",
    "🏥 Saúde"
])

with tab1:
    st.header("Eficiência da Limpeza Urbana")
    df_limpeza = load_data('limpeza_urbana')

    if not df_limpeza.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Rotas por Turno")
            turno_count = df_limpeza['turno'].value_counts()
            fig = px.pie(turno_count, names=turno_count.index, values=turno_count.values)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Frequência de Coleta")
            freq_count = df_limpeza['frequencia'].value_counts()
            fig = px.bar(freq_count, x=freq_count.index, y=freq_count.values)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados de limpeza urbana não disponíveis")

with tab2:
    st.header("Monitoramento de Obras e Licenciamento")
    df_obras = load_data('obras_licenciamento')

    if not df_obras.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Licenças por Tipo")
            tipo_count = df_obras['tipo_licenciamento'].value_counts().head(10)
            fig = px.bar(tipo_count, x=tipo_count.index, y=tipo_count.values)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Distribuição por Bairro")
            bairro_count = df_obras['bairro'].value_counts().head(10)
            fig = px.pie(bairro_count, names=bairro_count.index, values=bairro_count.values)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados de obras não disponíveis")

with tab3:
    st.header("Ocorrências de Segurança Pública")
    df_seguranca = load_data('ocorrencias_seguranca')

    if not df_seguranca.empty:
        if 'data' in df_seguranca.columns:
            df_seguranca['data'] = pd.to_datetime(df_seguranca['data'])
            df_filtrado = df_seguranca[
                (df_seguranca['data'] >= pd.Timestamp(data_inicio)) &
                (df_seguranca['data'] <= pd.Timestamp(data_fim))
            ]

            if bairro != "Todos":
                df_filtrado = df_filtrado[df_filtrado['bairro'] == bairro]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Ocorrências por Bairro")
            bairro_count = df_filtrado['bairro'].value_counts().head(10)
            fig = px.bar(bairro_count, x=bairro_count.index, y=bairro_count.values)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Tipos de Ocorrências")
            tipo_count = df_filtrado['tipo_acao'].value_counts().head(10)
            fig = px.pie(tipo_count, names=tipo_count.index, values=tipo_count.values)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Evolução Temporal")
        df_filtrado['mes'] = df_filtrado['data'].dt.to_period('M').astype(str)
        evolucao = df_filtrado.groupby('mes').size().reset_index(name='ocorrencias')
        fig = px.line(evolucao, x='mes', y='ocorrencias', title='Ocorrências por Mês')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados de segurança pública não disponíveis")

with tab4:
    st.header("Indicadores de Saúde Pública")
    df_saude = load_data('distribuicao_medicamentos')

    if not df_saude.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Medicamentos Mais Distribuídos")
            top_meds = df_saude.groupby('medicamento')['quantidade'].sum().nlargest(10).reset_index()
            fig = px.bar(top_meds, x='medicamento', y='quantidade')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Distribuição por Bairro")
            bairro_dist = df_saude.groupby('bairro')['quantidade'].sum().nlargest(10).reset_index()
            fig = px.pie(bairro_dist, names='bairro', values='quantidade')
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Unidades de Saúde com Maior Distribuição")
        unidade_dist = df_saude.groupby('unidade')['quantidade'].sum().nlargest(5).reset_index()
        st.dataframe(unidade_dist)
    else:
        st.warning("Dados de saúde não disponíveis")

db.close()

st.markdown("---")
st.caption("Dados obtidos do Portal Recife Dados Aberto | Atualizado em: " + datetime.today().strftime("%d/%m/%Y"))
