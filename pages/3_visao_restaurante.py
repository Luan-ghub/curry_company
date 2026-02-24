# ==================================================================================================================================================================#
#                                                                           BIBLIOTECAS E IMPORT
# ==================================================================================================================================================================#
import numpy as np
import haversine
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

# ==================================================================================================================================================================
#                                                                           CONFIGURAÇÃO DA PÁGINA
# ==================================================================================================================================================================
st.set_page_config(page_title="Visão Restaurantes", page_icon="🍽️", layout="wide")

#===========================================================================================================================================================================                             
#                                                                                FUNÇÕES
#===========================================================================================================================================================================

# FUNÇÃO DE LIMPEZA DE COLUNAS DE TEXTO
def limpar_colunas_texto (df1):
    df_limpo = df1.copy()
    colunas = df_limpo.select_dtypes(include = ["object"]).columns
    for coluna in colunas:
        df_limpo[coluna] = df_limpo[coluna].str.strip().str.casefold()
        df_limpo[coluna] = df_limpo[coluna].replace("nan",np.nan)
    return df_limpo

# FUNÇÃO DE PADRONIZAÇÃO DAS COLUNAS
def padronizar_colunas (df1):
    df_padronizado = df1.copy()
    df_padronizado["Delivery_person_Age"] = pd.to_numeric(df_padronizado["Delivery_person_Age"], errors='coerce')
    df_padronizado["Delivery_person_Ratings"] = pd.to_numeric(df_padronizado["Delivery_person_Ratings"], errors='coerce')
    df_padronizado["multiple_deliveries"] = pd.to_numeric(df_padronizado["multiple_deliveries"], errors='coerce')
    df_padronizado["Time_taken(min)"] = df_padronizado["Time_taken(min)"].str.removeprefix("(min)")
    df_padronizado["Time_taken(min)"] = pd.to_numeric(df_padronizado["Time_taken(min)"], errors='coerce')
    df_padronizado["Order_Date"] = pd.to_datetime(df_padronizado["Order_Date"],format = "%d-%m-%Y", errors='coerce')
    df_padronizado['Time_Orderd'] = pd.to_datetime(df_padronizado['Time_Orderd'],format='%H:%M:%S', errors='coerce').dt.time
    df_padronizado['Time_Order_picked'] = pd.to_datetime(df_padronizado['Time_Order_picked'],format='%H:%M:%S', errors='coerce').dt.time
    df_padronizado.dropna(inplace=True)
    df_padronizado["Delivery_person_Age"] = df_padronizado["Delivery_person_Age"].astype(int)
    df_padronizado["multiple_deliveries"] = df_padronizado["multiple_deliveries"].astype(int)
    df_padronizado["Time_taken(min)"] = df_padronizado["Time_taken(min)"].astype(int)
    df_padronizado["Weatherconditions"] = df_padronizado["Weatherconditions"].str.removeprefix("conditions ")
    df_padronizado = df_padronizado.rename(columns = {"Time_taken(min)" : "time_taken"})
    return df_padronizado

# FUNÇÃO DE CARREGAMENTO E LIMPEZA COM CACHE
@st.cache_data
def carregar_e_limpar_dados():
    df = pd.read_csv("dataset/train.csv") # Mantido o nome do arquivo na raiz
    df1 = df.copy()
    df1 = limpar_colunas_texto(df1)
    df1 = padronizar_colunas(df1)
    
    # Criar coluna distance aqui para otimizar e não recalcular a cada filtro
    df1["distance"] = df1.apply(
        lambda x: haversine.haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1
    )
    return df1

# FUNÇÃO DE GRÁFICO DA DISTANCIA MÉDIA POR CIDADE
def distancia_media(df1):
    distancia_media_cidade = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = px.pie(distancia_media_cidade, 
                 values='distance', 
                 names='City', 
                 hole=0.4, # Adicionado furo no meio para ficar mais moderno (Donut Chart)
                 hover_data=['distance'],
                 labels={'distance':'Distância Média'},
                 color_discrete_sequence=px.colors.sequential.RdBu)
    return fig

# FUNÇÃO DE GRÁFICO DE MÉDIA E DESVIO PADRÃO DE TEMPO POR CIDADE
def time_by_city(df1):
    df_aux = df1.loc[:, ['City', 'time_taken']].groupby("City").agg({"time_taken" : ["mean","std"]}).reset_index()
    df_aux.columns = ['City', 'time_mean', 'time_std']
    fig = px.bar(df_aux, 
                 x='City', 
                 y='time_mean', 
                 error_y='time_std',
                 labels={'City': 'Cidade', 'time_mean': 'Tempo Médio de Entrega (min)'},
                 text='time_mean',
                 color_discrete_sequence=['#1f77b4'])
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    return fig

# FUNÇÃO DE MÉDIA E DESVIO PADRÃO DE TEMPO POR TIPO DE PEDIDO
def meantime_by_delivery(df1):
    df1_time = df1.groupby(["City","Type_of_order"]).agg({"time_taken" : ["mean","std"]}).reset_index()
    df1_time.columns = ["Cidade", "Tipo de Pedido", "Tempo Médio", "Desvio Padrão"]
    return df1_time

# FUNÇÃO DE MÉDIA E DESVIO PADRÃO DE TEMPO POR TRÁFEGO
def meantime_by_citytrafic(df1):
    df_aux = df1.groupby(["City","Road_traffic_density"]).agg({"time_taken" : ["mean","std"]}).reset_index()
    df_aux.columns = ["City", "Road_traffic_density", "time_mean", "time_std"]
    fig = px.sunburst(df_aux,
                      path=['City', 'Road_traffic_density'],
                      values='time_mean',
                      color='time_std',
                      color_continuous_scale='RdBu',
                      hover_name="City")
    return fig

#===========================================================================================================================================================================                              
#                                                                 CARREGAMENTO DOS DADOS
#===========================================================================================================================================================================
df_raw = carregar_e_limpar_dados()     

#===========================================================================================================================================================================#
#                                                                       SIDEBAR
#===========================================================================================================================================================================#
st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## ⚙️ Filtros")

# Filtro Data
min_date = df_raw["Order_Date"].min().to_pydatetime()
max_date = df_raw["Order_Date"].max().to_pydatetime()

date_slider = st.sidebar.slider(
    "Selecione uma data limite:",
    min_value=min_date,
    max_value=max_date,
    value=max_date,
    format="DD/MM/YYYY"
)

# Filtro Condições de Trânsito
traffic_options = df_raw["Road_traffic_density"].unique().tolist()
all_traffic = st.sidebar.checkbox("Selecionar Todos os Tráfegos", value=True)

if all_traffic:
    traffic_filter = traffic_options
else:
    traffic_filter = st.sidebar.multiselect("Condições de Trânsito", options=traffic_options, default=traffic_options)

st.sidebar.markdown("""---""")
st.sidebar.caption("Cury Company © 2026")

# Aplicação dos Filtros no Dataframe
linhas_selecionadas_data = df_raw['Order_Date'] <= date_slider
linhas_selecionadas_transito = df_raw['Road_traffic_density'].isin(traffic_filter)

df1 = df_raw.loc[linhas_selecionadas_data & linhas_selecionadas_transito, :]

# =======================================================================================================================================================================
#                                                       LAYOUT - VISÃO RESTAURANTE
# =======================================================================================================================================================================
st.title("🍽️ Visão Restaurante")
st.markdown("""---""")

# ---------------------------------------------------------
# Seção de KPIs Principais
# ---------------------------------------------------------
st.markdown("### 📊 Análise Geral")

# Linha 1 de KPIs
col1, col2, col3 = st.columns(3)
with col1:
    entregadores = df1['Delivery_person_ID'].nunique()
    st.metric("Entregadores Únicos", f"{entregadores:,}")
    
with col2:
    media = df1["distance"].mean()
    st.metric("Distância Média de Entrega", f"{media:.2f} km")
    
df_festival_stats = df1.groupby("Festival")["time_taken"].agg(['mean', 'std']).reset_index()

with col3:
    tempo_com_festival = df_festival_stats.loc[df_festival_stats['Festival'] == 'yes', 'mean'].iloc[0] if not df_festival_stats[df_festival_stats['Festival'] == 'yes'].empty else 0
    st.metric("Tempo Médio (c/ Festival)", f"{tempo_com_festival:.2f} min")

st.markdown("<br>", unsafe_allow_html=True) # Espaçamento invisível

# Linha 2 de KPIs
col4, col5, col6 = st.columns(3)
with col4:
    std_com_festival = df_festival_stats.loc[df_festival_stats['Festival'] == 'yes', 'std'].iloc[0] if not df_festival_stats[df_festival_stats['Festival'] == 'yes'].empty else 0
    st.metric("Desvio Padrão (c/ Festival)", f"{std_com_festival:.2f} min")
    
with col5:
    tempo_sem_festival = df_festival_stats.loc[df_festival_stats['Festival'] == 'no', 'mean'].iloc[0] if not df_festival_stats[df_festival_stats['Festival'] == 'no'].empty else 0
    st.metric("Tempo Médio (s/ Festival)", f"{tempo_sem_festival:.2f} min")
    
with col6:
    std_sem_festival = df_festival_stats.loc[df_festival_stats['Festival'] == 'no', 'std'].iloc[0] if not df_festival_stats[df_festival_stats['Festival'] == 'no'].empty else 0
    st.metric("Desvio Padrão (s/ Festival)", f"{std_sem_festival:.2f} min")

st.markdown("""---""")

# ---------------------------------------------------------
# Seção de Gráficos de Distância e Tráfego
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Distribuição da Distância Média por Cidade")
    fig1 = distancia_media(df1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### Tempo Médio por Cidade e Tráfego")
    fig2 = meantime_by_citytrafic(df1)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("""---""")

# ---------------------------------------------------------
# Seção de Tempos de Entrega
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Distribuição do Tempo por Cidade")
    fig3 = time_by_city(df1)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("#### Tempo Médio por Tipo de Entrega")
    df1_time = meantime_by_delivery(df1)
    st.dataframe(df1_time, use_container_width=True)