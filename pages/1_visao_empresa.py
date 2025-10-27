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

                                            # FUNÇÃO DE CRIAÇÃO DO GRAFICO DE PEDIDOS POR DIA

def order_by_date(df1):
    """ Função para criar um gráfico de barras de quantidade de pedidos por dia:
    1 - cria uma variavel (df_aux) que recebe o grouby feito em df1
    2 - cria uma variavel (fig) para receber o grafico de barras

    Entrada: dataframe
    Saída: gráfico

    """
    df_aux = df1.groupby("Order_Date")["ID"].count().reset_index()
    fig = px.bar(df_aux, x="Order_Date", y="ID", text="ID", title="Pedidos por Dia")
    return fig

                                            # FUNÇÃO DE CRIAÇÃO DO GRAFICO DE DISTRIBUIÇÃO DE ENTREGAS POR TIPO DE TRÁFEGO


def order_by_traffic(df1):
    """ Função que desenha um gráfico de pizza da distribuição de entregas por tipo de tráfego
    1- cria uma variavel auxiliar (df_aux) que recebe o groupby feito em df1
    2- cria uma variavel (fig) que recebe um gráfico de pizza dos ids por tipo de tráfego

    Entrada: dataframe
    saída: gráfico
    """
    df_aux = df1.groupby("Road_traffic_density")["ID"].count().reset_index()
    fig = px.pie(df_aux, values='ID', names='Road_traffic_density', title="Distribuição por Tipo de Tráfego")
    return fig

    
                                            # FUNÇÃO DE CRIAÇÃO DO GRÁFICO DA QUANTIDADE DE ENTREGAS POR CIDADE E TIPO DE TRAFEGO

def order_by_city_and_traffic(df1):
    """ Função que desenha um gráfico de pizza da quantidade de entregas por tipo de tráfego
        1- cria uma variavel auxiliar (df_aux) que recebe o groupby feito em df1
        2- cria uma variavel (fig) que recebe um gráfico de barras da quantidade de entregas por cidade e tipo de tráfego
    
        Entrada: dataframe
        saída: gráfico
    """
    df_aux = df1.groupby(["City", "Road_traffic_density"])["ID"].count().reset_index()
    fig = px.bar(df_aux, x="City", y="ID", color='Road_traffic_density', barmode='group', text='ID', title="Pedidos por Cidade e Tráfego")
    fig.update_traces(textposition='outside', texttemplate='%{y}', cliponaxis=False)
    return fig

                                            # FUNÇÃO DE CRIAÇÃO DO GRAFICO DE PEDIDOS POR SEMANA


def order_by_week(df1):
    """ Função que desenha um gráfico de barras da quantidade de entregas por semana
    1- cria uma variavel auxiliar (df_aux) que recebe o groupby feito em df1
    2- cria uma variavel (fig) que recebe um gráfico de barras da quantidade de pedidos por semana

    Entrada: dataframe
    saída: gráfico
    """
    df1['Week'] = df1['Order_Date'].dt.strftime('%U')
    df_aux =df1.groupby('Week')["ID"].count().reset_index()
    fig = px.bar(df_aux, x='Week', y='ID', text="ID", title="Total de Pedidos por Semana do Ano")
    return fig


                                            # FUNÇÃO DE CRIAÇÃO DO GRAFICO DE PEDIDOS POR QUANTIDADE DE ENTREGADORES NA SEMANA

def order_by_deliver(df1):   
    """ Função que desenha um gráfico de linhas da quantidade de entregadores a cada semana
    1- cria uma variavel auxiliar (df1_aux) que recebe o groupby feito em df1 para entregas
    2 - cria uma variavel auxiliar (df2_aux) que recebe o groupby feito em df1 para entregadores
    3 - cria um dataframe unindo as duas visualizações de groupby
    4- cria uma variavel (fig) que recebe um gráfico de linhas da quantidade de entregas feitas por entregadores na semana
    
    Entrada: dataframe
    saída: gráfico
    """
    df1_aux = df1.groupby("Week")["ID"].count().reset_index()
    df2_aux = df1.groupby("Week")["Delivery_person_ID"].nunique().reset_index()
    df_final = pd.merge(df1_aux, df2_aux, how="inner")
    df_final["order_by_deliver"] = df_final["ID"] / df_final["Delivery_person_ID"]
    fig = px.line(df_final, x="Week", y="order_by_deliver", title="Média de Pedidos por Entregador a cada Semana")
    return fig


                                                # FUNÇÃO DE CRIAÇÃO DO MAPA DOS LOCAIS DE ENTREGA

def map(df1):
    """ Função que desenha um mapa da distância média dos locais de entrega
    1- cria uma variavel auxiliar (df1_aux) que recebe o groupby feito em df1 as medias da latitude e longitude dos locais de entrega
    2 - realiza um if para verificar se a coluna contem dados
    3 - realiza um for para cada linha da coluna de latitude e longitude para adicionar ao mapa
    4- cria um mapa com dimensões 1024x600
    
    Entrada: dataframe
    saída: mapa
    """
    df1_aux = df1.groupby(["City", "Road_traffic_density"])[["Delivery_location_latitude", "Delivery_location_longitude"]].median().reset_index()
    
    if not df1_aux.empty:
        mapa = folium.Map(location=[df1_aux['Delivery_location_latitude'].iloc[0], df1_aux['Delivery_location_longitude'].iloc[0]], zoom_start=11)
        
        for index, local in df1_aux.iterrows():
            folium.Marker(
                location=[local['Delivery_location_latitude'], local['Delivery_location_longitude']],
                popup=f"{local['City']} - {local['Road_traffic_density']}"
            ).add_to(mapa)
        
        folium_static(mapa, width=1024, height=600)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
    return None
#===========================================================================================================================================================================                              
                                                                    #CARREGAMENTO DOS DADOS
#===========================================================================================================================================================================

df1 = carregar_e_limpar_dados()                                                            

#===========================================================================================================================================================================#
                                                                        # LAYOUT
#===========================================================================================================================================================================#
st.set_page_config(page_title = "Visão Empresa", layout= "wide")
st.header("Marketplace - Visão Cliente")
#===========================================================================================================================================================================#
                                                                        # SIDEBAR
#===========================================================================================================================================================================#
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


#===========================================================================================================================================================================#
                                                                        # ABAS
#===========================================================================================================================================================================#
tab_gerencial, tab_tatica, tab_geografica = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])

# Aba Gerencial
with tab_gerencial:
    
    with st.container():
        fig = order_by_date(df1)
        st.header("Order by Date")
        st.plotly_chart(fig, use_container_width=True)
        
     
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header("Traffic Order Share")
            fig = order_by_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("Traffic Order City")
            fig = order_by_city_and_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
            

# Aba Tática
with tab_tatica:
    with st.container():
        st.header("Pedidos por Semana")
        fig = order_by_week(df1)
        st.plotly_chart(fig, container_use_width=True)
            
    with st.container():
        st.header("Pedidos por Entregadores")
        fig = order_by_deliver(df1)
        st.plotly_chart(fig, use_container_width=True)
        

# Aba Geográfica
with tab_geografica:
    st.header("Localização Central por Cidade e Tráfego")
    map (df1)