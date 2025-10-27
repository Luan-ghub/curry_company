# ==================================================================================================================================================================#
                                                                            # BIBLIOTECAS E IMPORT
# ==================================================================================================================================================================#
import numpy as np
import haversine
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

#===========================================================================================================================================================================                             
                                                                                # FUNÇÕES
#===========================================================================================================================================================================

                                            # FUNÇÃO DE LIMPEZA DE COLUNAS DE TEXTO

def limpar_colunas_texto (df1):
    ''' Função que limpa as colunas com formato texto em um data frame:
    1 - cria uma cópia do dataframe
    2 - Cria uma variável para alocar as colunas do tipo texto
    3 - Percorre a variável (lista) e, para cada item, aplicar a padronização de texto e substituição dos valores de texto NaN por none
    4 - retorna o data frame limpo

    Parâmetro: Data frame a ser limpo

    Retorno: Data frame com colunas do tipo objetos limpas e padronizadas para letra minúscula
    '''
#1.1
    df_limpo = df1.copy()
#1.2
    colunas = df_limpo.select_dtypes(include = ["object"]).columns
#1.3
    for coluna in colunas:
        df_limpo[coluna] = df_limpo[coluna].str.strip().str.casefold()
        df_limpo[coluna] = df_limpo[coluna].replace("nan",np.nan)
#1.5
    return df_limpo


                                            # FUNÇÃO DE PADRONIZAÇÃO DAS COLUNAS

def padronizar_colunas (df1):
    ''' Função que padroniza as colunas em um data frame:
        1 - Modifica todas as colunas com dados em formato equivocado para o seu formato adequado
        2 - Retorna um data frame padronizado
    '''

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
        """
    Função que carrega, limpa e padroniza os dados do arquivo csv principal, guardando as ações no cache do streamlit
    para otimizar o carregamento da página.

    1 - Recebe um dataset
    2 - aplica as funções de limpeza e padronização
    3 - retorna o dataset limpo e padronizado e armazena em cache

    Entrada: dataframe original
    Saída: dataframe limpo
    """
    df = pd.read_csv("dataset/train.csv")
    df1 = df.copy()
    df1 = limpar_colunas_texto(df1)
    df1 = padronizar_colunas(df1)
    return df1

                                        # FUNÇÃO DE GRÁFICO DA DISTANCIA MÉDIA POR CIDADE

def distancia_media (df1):
    """
    Função para calcular a distância média de entrega por cidade e gerar um gráfico de pizza.

    1 - Agrupa o dataframe por cidade e calcula a distância média.
    2 - Cria um gráfico de pizza com as distâncias médias por cidade.

    Entrada: Dataframe 
    Saída: Gráfico.
    """
    distancia_media_cidade = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = px.pie(distancia_media_cidade, 
                 values='distance', 
                 names='City', 
                 hover_data=['distance'],
                 labels={'distance':'Distância Média'})
    return fig

                                             # FUNÇÃO DE GRÁFICO DE MÉDIA E DESVIO PADRÃO DE TEMPO POR CIDADE
  
def time_by_city (df1):
    """
    Função para calcular a média e desvio padrão do tempo de entrega por cidade e gerar um gráfico de barras.

    1 - Agrupa o dataframe por cidade e calcula a média e desvio padrão do tempo.
    2 - Cria um gráfico de barras com a média como altura e o desvio padrão como barra de erro.

    Entrada: Dataframe
    Saída: Gráfico de barras
    """
    df_aux = df1.loc[:, ['City', 'time_taken']].groupby("City").agg({"time_taken" : ["mean","std"]}).reset_index()
    df_aux.columns = ['City', 'time_mean', 'time_std']
    fig = px.bar(df_aux, 
                 x='City', 
                 y='time_mean', 
                 error_y='time_std',
                 labels={'City': 'Cidade', 'time_mean': 'Tempo Médio de Entrega (min)'},
                 text='time_mean')
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    return fig

                                                 # FUNÇÃO DE MÉDIA E DESVIO PADRÃO DE TEMPO POR TIPO DE PEDIDO

def meantime_by_delivery (df1):
    """
    Função para calcular a média e desvio padrão do tempo de entrega, agrupando por cidade e tipo de pedido.

    1 - Agrupa o dataframe por cidade e tipo de pedido.
    2 - Calcula a média e desvio padrão do tempo para cada grupo.
    3 - Renomeia as colunas do dataframe resultante.

    Entrada: Dataframe
    Saída: Dataframe
    """
    df1_time = df1.groupby(["City","Type_of_order"]).agg({"time_taken" : ["mean","std"]}).reset_index()
    df1_time.columns = ["Cidade", "Tipo de Pedido", "Tempo Médio", "Desvio Padrão"]
    return df1_time

                                                     # FUNÇÃO DE MÉDIA E DESVIO PADRÃO DE TEMPO POR TRÁFEGO

def meantime_by_citytrafic (df1):
    """
    Função para calcular a média e desvio padrão do tempo de entrega por cidade e densidade de tráfego, e gerar um gráfico sunburst.

    1 - Agrupa o dataframe por cidade e densidade de tráfego.
    2 - Calcula a média e desvio padrão do tempo para cada grupo.
    3 - Cria um gráfico sunburst mostrando a hierarquia e os valores.

    Entrada: Dataframe
    Saída: Gráfico
    """
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
                                                                  # CARREGAMENTO DOS DADOS
#===========================================================================================================================================================================

df1 = carregar_e_limpar_dados()     
                                                                  
#===========================================================================================================================================================================#
                                                                        # SIDEBAR
#===========================================================================================================================================================================#
st.set_page_config(page_title = "Visão Restaurantes", layout= "wide")
st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

# Filtro Data
st.sidebar.markdown("## Selecione uma data limite:")
date_slider = st.sidebar.slider(
    "Filtro de Datas",
    min_value=df1["Order_Date"].min().to_pydatetime(),
    max_value=df1["Order_Date"].max().to_pydatetime(),
    value=df1["Order_Date"].max().to_pydatetime(),
    format="DD/MM/YYYY"
)
st.sidebar.markdown("""---""")

# Filtro Condições de Trânsito
traffic_options = st.sidebar.multiselect(
    "Condições de Trânsito",
    options=df1["Road_traffic_density"].unique(),
    default=df1["Road_traffic_density"].unique()
)

# Separador
st.sidebar.markdown("""---""")


# Filtro de Data
linhas_selecionadas_data = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas_data, :]

# Filtro de Trânsito
linhas_selecionadas_transito = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas_transito, :]

# =======================================================================================================================================================================
#                                                       LAYOUT - VISÃO RESTAURANTE
# =======================================================================================================================================================================
st.title("Marketplace - Visão Restaurante")
st.markdown("""---""")

# --- Linha 1: Métricas Gerais ---
with st.container():
    st.header("Análise Geral")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        entregadores = df1['Delivery_person_ID'].nunique()
        st.metric("Entregadores Únicos", entregadores)
        
    with col2:
        df1["distance"] = df1.apply(
            lambda x: haversine.haversine(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1
        )
        media = df1["distance"].mean()
        st.metric("Distância Média", f"{media:.2f} km")
        
    df_festival_stats = df1.groupby("Festival")["time_taken"].agg(['mean', 'std']).reset_index()

    with col3:
        tempo_com_festival = df_festival_stats.loc[df_festival_stats['Festival'] == 'yes', 'mean'].iloc[0] if not df_festival_stats[df_festival_stats['Festival'] == 'yes'].empty else 0
        st.metric("Tempo Médio (c/ Festival)", f"{tempo_com_festival:.2f} min")
        
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

# Gráfico de Pizza 
with st.container():
    st.header("Distribuição da Distância Média por Cidade")
    fig = distancia_media (df1)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""---""")

#  ráfico com Intervalos
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Distribuição do Tempo por Cidade")
        fig = time_by_city (df1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.header("Tempo Médio por Tipo de Entrega (Tabela)")
        df1_time = meantime_by_delivery (df1)
        st.dataframe(df1_time, use_container_width=True)

st.markdown("""---""")

# Gráfico Sunburst
with st.container():
    st.header("Tempo Médio por Cidade e Tipo de Tráfego")
    fig = meantime_by_citytrafic (df1)
    st.plotly_chart(fig, use_container_width=True)