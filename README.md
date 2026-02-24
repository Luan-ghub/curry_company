# Curry Company - Dashboard de Operações e Logística

## 1. O Problema de Negócio

**O que é a Curry Company?**
A Curry Company é uma empresa de tecnologia focada em logística e entrega de comida. O seu modelo de negócio atua como Marketplace, sendo um intermediário que conecta clientes, restaurantes e entregadores parceiros, garantindo que os pedidos cheguem de forma rápida e segura aos consumidores.

**Dataset**
O conjunto de dados utilizado neste projeto ([disponível no Kaggle](https://www.kaggle.com/datasets/gauravmalik26/food-delivery-dataset)) contém informações detalhadas sobre as operações de entrega da empresa. Ele inclui dados demográficos e avaliações dos entregadores, coordenadas geográfica dos restaurantes e dos locais de entrega, datas e horários dos pedidos, condições climáticas, densidade do trânsito e demais informações que serão úteis para geração de KPI’s.

**Objetivo e Papel do Cientista de Dados**
Através dos dados da Curry Company, é possível monitorar a saúde operacional da empresa, entender os gargalos logísticos e avaliar o desempenho da frota de entregadores.
Simulando a atuação como um Cientista de Dados da empresa, o meu papel foi organizar essa base de dadose desenvolver um painel de indicadores tático e estratégico para fornecer ao CEO e aos times de operações uma ferramenta que respondesse a perguntas sobre o negócio.

**Resultado Final**
O resultado é um Dashboard interativo, hospedado na nuvem, que permite a navegação e filtragem de dados logísticos divididos em três visões principais: Visão Empresa, Visão Entregadores e Visão Restaurantes.

---

## 2. Premissas do Negócio

Para a construção deste projeto, foram adotadas as seguintes premissas:

- 
- **Modelo de Negócio:** Considerou-se a visão de logística e Marketplace
- **Visões Abordadas:** O projeto focou-se em três visões principais:
    1. **Visão Empresa:** Acompanhamento de pedidos gerais, distribuição por tráfego, crescimento semanal e mapeamento geográfico das entregas.
    2. **Visão Entregadores:** Métricas de avaliação por idade, impacto das condições climáticas e trânsito, e ranking de velocidade.
    3. **Visão Restaurantes:** Análise de distâncias médias, tempo de entrega com ou sem eventos especiais e tempo por tipo de pedido.

---

## 3. Estratégia da Solução

O projeto foi executado através das seguintes etapas:

1. **Entendimento e Planejamento:** Levantamento das principais perguntas de negócio que precisavam ser respondidas.
2. **Coleta e Limpeza de Dados:**
    - Tratamento de valores nulos e duplicadas;
    - Padronização de nomes de colunas e remoção de espaços vazios;
    - Conversão dos tipos de dados;
    - Feature Engineering:
3. **Análise Exploratória:** Criação de análises estatísticas e protótipos de gráficos no Jupyter Notebook usando a biblioteca *Plotly* para validar as hipóteses logísticas.
4. **Desenvolvimento do Dashboard (Python + Streamlit):**
    - Estruturação do código em arquivos `.py` modulares (`1_visao_empresa.py`, `2_visao_entregadores.py`, `3_visao_restaurante.py`).
    - Geração de um dashboard interativo por meio do Streamlit com hospedagem em nuvem via Streamlit Cloud

---

## 4. Top 3 Insights de Dados

Durante a análise exploratória, os principais insights descobertos foram:

> 💡 **1. Impacto de datas festivas na Logística**
Em dias de Festival, o tempo médio de entrega sofre um aumento drástico, e o desvio padrão cresce proporcionalmente. Isso indica que a frota atual não consegue absorver o pico de demanda, o que sugere  a necessidade de incentivos temporários para atrair mais entregadores nessas datas.
> 

> 💡 **2. Densidade do Trânsito**
A maior parte do volume de pedidos ocorre justamente nos horários de trânsito moderado a alto, o que pode indicar uma ação da empresa para captar mais entregadores nesses horários durante a semana
> 

> 💡 **3. Distância vs. Tempo de Preparo**
Em certas cidades, principalmente urbanas e semi-urbanas, mesmo com distâncias médias menores, o tempo total de entrega é maior. Isso aponta para gargalos não no deslocamento em si, mas possivelmente no trânsito urbano pesado, nas condições do trânsito ou na demora do preparo no restaurante.
> 

---

## 5. O Produto Final do Projeto

O produto final é um Dashboard alojado na nuvem, acessível a partir de qualquer navegador web.

**Funcionalidades do App:**

- **Filtros Dinâmicos:** O utilizador pode filtrar todos os painéis escolhendo uma janela de datas e selecionando cenários específicos de trânsito.
- **Indicadores de Desempenho:** Visibilidade imediata no topo de cada página com as métricas mais críticas.
- **Mapas Interativos:** Visualização geográfica , permitindo o zoom e a análise da densidade de entregas por região.

🔗 **Link para o Dashboard:** [Curry Company](https://currycompany-project.streamlit.app/)

---

## 6. Conclusão e Próximos Passos

O objetivo era criar um dashboard que pudesse ser utilizado de fato como uma ferramenta gerencial. O Dashboard da Curry Company permite à liderança observar a operação sob diferentes ângulos, identificando os possíveis pontos de melhoria e pontos positivos.

**Próximos Passos :**
Caso este projeto fosse continuado, as próximas etapas incluiriam:

- **Previsão de Tempo de Entrega:** Treinar um modelo de Regressão para prever o tempo exato de entrega no momento em que o cliente faz o pedido, baseando-se no clima, trânsito e distância.
- **Dashboard em Tempo Real:** Conectar o script Python a um banco de dados SQL, em vez de um CSV, alimentando as métricas e o mapa geográfico em tempo real.
