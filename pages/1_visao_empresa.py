# ==================================================================================================================================================================#
#                                                                           BIBLIOTECAS E IMPORT
# ==================================================================================================================================================================#
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image

# ==================================================================================================================================================================
#                                                                           CONFIGURAÇÃO DA PÁGINA
# ==================================================================================================================================================================
st.set_page_config(page_title="Visão Empresa", page_icon="🏢", layout="wide")

# ==================================================================================================================================================================
#                                                                           FUNÇÃO DE LIMPEZA E LOAD
# ==================================================================================================================================================================
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    
    # 1. Limpeza de espaços em branco nos textos
    cols_str = df.select_dtypes(include=['object']).columns
    for col in cols_str:
        df[col] = df[col].str.strip()
        
    # 2. Tratamento de valores nulos ('NaN' em texto para nulo real)
    df = df.replace('NaN', np.nan)
    df = df.dropna()
    
    # 3. Conversão de Tipos
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    
    # 4. Limpeza da coluna de Tempo
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: int(x.split('(min) ')[1]) if pd.notnull(x) and '(min)' in x else x)
    
    # 5. Criação da Feature: Semana do Ano
    df['week_of_year'] = df['Order_Date'].dt.isocalendar().week
    
    return df

# Carregar os dados limpos
df_raw = load_data('dataset/train.csv')

# ==================================================================================================================================================================
#                                                                           BARRA LATERAL (SIDEBAR)
# ==================================================================================================================================================================
st.sidebar.markdown("## ⚙️ Filtros")

# Filtro 1: Data
min_date = df_raw['Order_Date'].min().to_pydatetime()
max_date = df_raw['Order_Date'].max().to_pydatetime()

date_slider = st.sidebar.slider(
    "Selecione o limite de data:",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    format="DD-MM-YYYY"
)

# Filtro 2: Densidade de Tráfego
traffic_options = df_raw['Road_traffic_density'].unique().tolist()
all_traffic = st.sidebar.checkbox("Selecionar Todos os Tráfegos", value=True)

if all_traffic:
    traffic_filter = traffic_options
else:
    traffic_filter = st.sidebar.multiselect("Selecione a Densidade de Tráfego:", traffic_options, default=traffic_options)

st.sidebar.markdown("---")
st.sidebar.caption("Cury Company © 2026")

# Aplicação dos Filtros
df_filtered = df_raw[(df_raw['Order_Date'] <= date_slider) & (df_raw['Road_traffic_density'].isin(traffic_filter))]

# ==================================================================================================================================================================
#                                                                           DASHBOARD (CORPO PRINCIPAL)
# ==================================================================================================================================================================
st.title("🏢 Visão Empresa")
st.markdown("---")

# KPIs Principais
st.markdown("### 📊 Indicadores Principais")
col1, col2, col3 = st.columns(3)

with col1:
    total_pedidos = df_filtered.shape[0]
    st.metric(label="Total de Pedidos Realizados", value=f"{total_pedidos:,}")

with col2:
    entregadores_unicos = df_filtered['Delivery_person_ID'].nunique()
    st.metric(label="Entregadores Únicos Ativos", value=f"{entregadores_unicos:,}")

with col3:
    cidades_unicas = df_filtered['City'].nunique()
    st.metric(label="Cidades Operadas", value=f"{cidades_unicas}")

st.markdown("---")

# Abas de Navegação
tab_gerencial, tab_tatica, tab_geografica = st.tabs(["📈 Visão Gerencial", "🎯 Visão Tática", "🗺️ Visão Geográfica"])

# ABA 1: GERENCIAL
with tab_gerencial:
    st.markdown("#### Evolução de Pedidos Diários")
    df_aux = df_filtered.groupby('Order_Date').size().reset_index(name='count')
    fig = px.bar(df_aux, x='Order_Date', y='count', labels={'Order_Date': 'Data', 'count': 'Volume de Pedidos'}, color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Pedidos por Densidade de Tráfego")
        df_aux2 = df_filtered.groupby('Road_traffic_density').size().reset_index(name='count')
        fig2 = px.pie(df_aux2, values='count', names='Road_traffic_density', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig2, use_container_width=True)
        
    with col2:
        st.markdown("#### Volume de Pedidos: Cidade vs Tráfego")
        df_aux3 = df_filtered.groupby(['City', 'Road_traffic_density']).size().reset_index(name='count')
        fig3 = px.scatter(df_aux3, x='City', y='Road_traffic_density', size='count', color='City')
        st.plotly_chart(fig3, use_container_width=True)

# ABA 2: TÁTICA
with tab_tatica:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Evolução Semanal de Pedidos")
        df_aux4 = df_filtered.groupby('week_of_year').size().reset_index(name='count')
        fig4 = px.line(df_aux4, x='week_of_year', y='count', markers=True, labels={'week_of_year': 'Semana do Ano', 'count': 'Total de Pedidos'})
        st.plotly_chart(fig4, use_container_width=True)
        
    with col2:
        st.markdown("#### Produtividade Média (Pedidos/Entregador)")
        df_aux5 = df_filtered.groupby('week_of_year').agg({'ID': 'count', 'Delivery_person_ID': 'nunique'}).reset_index()
        df_aux5['produtividade'] = df_aux5['ID'] / df_aux5['Delivery_person_ID']
        fig5 = px.line(df_aux5, x='week_of_year', y='produtividade', markers=True, labels={'week_of_year': 'Semana', 'produtividade': 'Média de Pedidos'})
        st.plotly_chart(fig5, use_container_width=True)

# ABA 3: GEOGRÁFICA
with tab_geografica:
    st.markdown("#### Mapa de Distribuição Geográfica Central")
    df_aux6 = df_filtered.groupby(['City', 'Road_traffic_density'])[['Delivery_location_latitude', 'Delivery_location_longitude']].median().reset_index()
    
    mapa = folium.Map(location=[df_aux6['Delivery_location_latitude'].mean(), df_aux6['Delivery_location_longitude'].mean()], zoom_start=5)
    
    for index, location_info in df_aux6.iterrows():
        folium.Marker(
            [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
            popup=f"{location_info['City']} | Tráfego: {location_info['Road_traffic_density']}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(mapa)
        
    folium_static(mapa, width=1024, height=600)