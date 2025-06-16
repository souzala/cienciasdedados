import streamlit as st
import pandas as pd
import plotly.express as px

# Título do Dashboard
st.set_page_config(page_title="Censo Escolar 2022", layout="wide")
st.title("Dashboard - Censo Escolar 2022")

# Carregar os dados
df = pd.read_csv('microdados_ed_basica_2022.csv', sep=';', encoding='latin1')

# Sidebar para filtros

st.sidebar.header("Filtros")
tipo_dependencia = st.sidebar.multiselect(
    "Tipo de Escola",
    options=df['TP_DEPENDENCIA'].unique(),
    default=df['TP_DEPENDENCIA'].unique()
)

# Filtro aplicado
df_filtro = df.query("TP_DEPENDENCIA == @tipo_dependencia")

# Gráfico - Localização Urbana ou Rural
local = df_filtro['TP_LOCALIZACAO'].map({1: 'Urbana', 2: 'Rural'}).value_counts().reset_index()
fig1 = px.pie(local, values='count', names='index', title='Localização das Escolas')

# Gráfico - Energia Renovável
energia = df_filtro['IN_ENERGIA_RENOVAVEL'].map({1: 'Com Renovável', 0: 'Sem Renovável'}).value_counts().reset_index()
fig2 = px.pie(energia, values='count', names='index', title='Uso de Energia Renovável')

# Gráfico - Dependência Administrativa
dep = df_filtro['TP_DEPENDENCIA'].map({1: 'Federal', 2: 'Estadual', 3: 'Municipal', 4: 'Privada'}).value_counts().reset_index()
fig3 = px.bar(dep, x='index', y='count', title='Dependência Administrativa')

# Layout em 3 colunas
col1, col2, col3 = st.columns(3)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)
col3.plotly_chart(fig3, use_container_width=True)

# Dashboard expandido pode ter mais gráficos como:
# - Cor/Raça
# - Abastecimento de água
# - Tratamento de lixo
# - Atendimento especializado por região

st.markdown("---")
st.subheader("Análise por Tipo de Abastecimento de Água")

agua_cols = ['IN_AGUA_POTAVEL', 'IN_AGUA_REDE_PUBLICA', 'IN_AGUA_POCO_ARTESIANO',
             'IN_AGUA_CACIMBA', 'IN_AGUA_FONTE_RIO', 'IN_AGUA_INEXISTENTE']
agua_legenda = ['Água Potável', 'Rede Pública', 'Poço Artesiano', 'Cacimba', 'Fonte/Rio', 'Sem Água']

agua_data = df_filtro[agua_cols].sum()
fig4 = px.bar(x=agua_legenda, y=agua_data, title="Abastecimento de Água nas Escolas")
st.plotly_chart(fig4, use_container_width=True)
