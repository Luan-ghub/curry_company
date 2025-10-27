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
                                        # FUNÇÃO DE GRAFICO DA MEDIA DE NOTAS POR DENSIDADE DE TRAFEGO

def media_de_notas_por_trafego(df1):
    """
    Função que realiza a média de avaliações dos enrtegadores por tipo de tráfego e plota um gráfico de barras.

    1- Recebe um dataset
    2- realiza o groupby aplicando a média e o desvio padrão das notas de avaliação por tipo de tráfego
    3- plota um gráfico de barras com as médias e os desvios padrões por cada tipo

    Entrada: dataframe
    Saída: gráfico
    """
    df_avg_std_traffic = df1.groupby("Road_traffic_density").agg({
        "Delivery_person_Ratings": ["mean", "std"]})
    df_avg_std_traffic.columns = ["ratings_mean", "ratings_std"]
    df_avg_std_traffic = df_avg_std_traffic.reset_index()
    
    fig = px.bar(
        df_avg_std_traffic, 
        x='Road_traffic_density', 
        y='ratings_mean', 
        error_y='ratings_std',
        labels={'Road_traffic_density': 'Densidade do Tráfego', 'ratings_mean': 'Avaliação Média'},
        text_auto='.2f',
    )
    return fig

                                        # FUNÇÃO DE GRAFICO DA QUANTIDADE DE ENTREGADORES POR RANGE DE IDADE

def delivery_by_age(df1):
    """
    Função que realiza um range de idades dos entregadores e gera um gráfico de pizza da quantidade de entregadores por cada range
    de idade.

    1- Recebe um dataset
    2- Cria um range de idades e aloca cada idade do dataset em um dos ranges criados
    2- realiza o groupby aplicando a contagem única de entregadores por range de idade
    3- plota um gráfico de pizza com a quantidade de entregadores por cada range de idade
    
    Entrada: dataframe
    Saída: gráfico
    """
    bins = [0, 24, 30, 34, float('inf')]
    labels = ["Até 24", "25-30", "31-34", "35+"]
    df1["age_range"] = pd.cut(df1["Delivery_person_Age"], bins=bins, labels=labels, right=True)
    
    df_age_range = df1.groupby("age_range", observed=True)["Delivery_person_ID"].nunique().reset_index()
    
    fig = px.pie(
        df_age_range, 
        values="Delivery_person_ID", 
        names="age_range", 
    )
    return fig

                                            # FUNÇÃO DE TOP10 ENTREGADORES MAIS RÁPIDOS


def top10_fast(df1):
    df_top10_fast = df1.loc[:, ['Delivery_person_ID', 'City', 'time_taken']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'time_taken'], ascending=True)
    df_top10_fast = df_top10_fast.groupby('City').head(10).reset_index()
    return df_top10_fast

                                            # FUNÇÃO DE TOP10 ENTREGADORES MAIS LENTOS

def top10_slow(df1):
    df_top10_slow = df1.loc[:, ['Delivery_person_ID', 'City', 'time_taken']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'time_taken'], ascending=False)
    df_top10_slow = df_top10_slow.groupby('City').head(10).reset_index()
    return df_top10_slow

    
#===========================================================================================================================================================================                              
                                                                  # CARREGAMENTO DOS DADOS
#===========================================================================================================================================================================

df1 = carregar_e_limpar_dados()                                                            
                                                                  
#===========================================================================================================================================================================#
                                                                        # SIDEBAR
#===========================================================================================================================================================================#
st.set_page_config(page_title = "Visão Entregadores", layout= "wide")
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
                                                                # MÉTRICAS GERAIS
# =======================================================================================================================================================================

st.title("Dashboard de Análise - Visão dos Entregadores")
st.markdown("""---""")


st.header("Métricas Gerais")
col1, col2, col3, col4 = st.columns(4)
with col1:
    maior_idade = df1['Delivery_person_Age'].max()
    st.metric(label="Maior Idade", value=f"{maior_idade} anos")

with col2:
    menor_idade = df1['Delivery_person_Age'].min()
    st.metric(label="Menor Idade", value=f"{menor_idade} anos")

with col3:
    melhor_condicao = df1['Vehicle_condition'].max()
    st.metric(label="Melhor Condição de Veículo", value=melhor_condicao)

with col4:
    pior_condicao = df1['Vehicle_condition'].min()
    st.metric(label="Pior Condição de Veículo", value=pior_condicao)

st.markdown("""---""")

# =======================================================================================================================================================================
                                                                # Avaliações
# =======================================================================================================================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Avaliações Médias por Trânsito")
    fig = media_de_notas_por_trafego(df1)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribuição dos Entregadores por Faixa Etária")
    fig = delivery_by_age(df1)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""---""")

# =======================================================================================================================================================================
                                                                # Entregadores
# =======================================================================================================================================================================

st.header("Desempenho de Entrega")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Entregadores Mais Rápidos")
    df_top10_fast = top10_fast(df1)
    st.dataframe(df_top10_fast)


with col2:
    st.subheader("Top 10 Entregadores Mais Lentos")
    df_top10_slow = top10_slow(df1)
    st.dataframe(df_top10_slow)







