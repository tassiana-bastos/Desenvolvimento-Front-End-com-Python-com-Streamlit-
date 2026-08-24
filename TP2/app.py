import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pydeck as pdk

st.set_page_config(
    page_title="TP2 - COVID-19",
    page_icon="📊",
    layout="wide"
)

st.title("TP2 - Desenvolvimento Front-End com Python")
st.subheader("Análise dos dados da COVID-19")

st.header("Atividade 1 - Importancia da visualizacao dos dados")

"""
No contexto da COVID-19; a visualizacao de dados pode auxiliar na identificacao da evolucao dos casos e dos obitos ao longo do tempo, permitindo 
observar periodos de aumento ou reducao da doenca e diferencas entre estados, regioes e municipios. 
Para os gestores de saude publica, essas informacoes sao importantes para apoiar a tomada de decisoes, como o planejamento de recursos, a 
identificacao de regioes que necessitam de maior atencao e o acompanhamento da evolucao da situacao epidemiologica.
Para a populacao em geral, graficos e mapas podem facilitar a compreensao da situacao da pandemia e permitir o acompanhamento de informacoes 
relevantes de forma mais clara.
"""

# ============================================================
# LEITURA E CONCATENAÇÃO DOS DADOS
# ============================================================

arquivo1 = "HIST_PAINEL_COVIDBR_2025_Parte1_05set2025.csv"
arquivo2 = "HIST_PAINEL_COVIDBR_2025_Parte2_05set2025.csv"

df1 = pd.read_csv(arquivo1, sep=";")
df2 = pd.read_csv(arquivo2, sep=";")

df = pd.concat([df1, df2], ignore_index=True)

print(df.shape)
print(df.head())
print(df.info())

df["data"] = pd.to_datetime(df["data"])

# Registros agregados por estado
df_estado = df[
    df["estado"].notna() &
    df["municipio"].isna()
].copy()

# Registros de municipios
df_municipio = df[
    df["municipio"].notna()
].copy()

# Data mais recente disponível
data_final = df["data"].max()

# Semana epidemiológica mais recente
semana_final = df["semanaEpi"].max()


st.header("Atividade 2 - Evolução semanal dos casos de COVID-19")

"""
Estado escolhido: Sao Paulo (SP)
Justificativa: Sao Paulo foi escolhida por ser uma das Unidades Federativas de maior relevancia para a analise da pandemia e por permitir observar
a evolucao dos casos novos ao longo das semanas epidemiologicas de notificacao.
"""
sp = df_estado[df_estado["estado"] == "SP"]

casos_sp = (
    sp.groupby("semanaEpi", as_index=False)["casosNovos"]
    .sum()
)


st.bar_chart(
    casos_sp,
    x="semanaEpi",
    y="casosNovos"
)

st.header("Atividade 3 - Óbitos acumulados no Brasil")
brasil = df[
    (df["regiao"] == "Brasil") &
    (df["estado"].isna()) &
    (df["municipio"].isna())
].copy()

brasil = brasil.sort_values("data")

obitos_brasil = (
    brasil
    .groupby("semanaEpi", as_index=False)
    .tail(1)
    .sort_values("semanaEpi")
)


st.line_chart(
    obitos_brasil,
    x="semanaEpi",
    y="obitosAcumulado"
)
"""
A curva representa o total acumulado de óbitos ao longo das semanas epidemiológicas.Uma curva mais inclinada indica maior crescimento do total
acumulado naquele período. Uma curva mais próxima da horizontal indica menor crescimento. gráfico de linha é adequado porque permite observar
tendências e variações ao longo do tempo.
"""


st.header("Atividade 4 - Casos acumulados em três estados")


estados = ["SP", "MG", "RJ"]

dados_area = df_estado[
    df_estado["estado"].isin(estados)
].sort_values("data")

dados_area = (
    dados_area
    .groupby(["estado", "semanaEpi"], as_index=False)
    .tail(1)
)

dados_area = dados_area[
    ["semanaEpi", "estado", "casosAcumulado"]
]

dados_area = dados_area.pivot(
    index="semanaEpi",
    columns="estado",
    values="casosAcumulado"
)

dados_area = dados_area.sort_index()


st.area_chart(dados_area)

"""
Observa-se que Sao Paulo apresenta os maiores valores de casos acumulados ao longo das semanas, seguido por Minas Gerais e Rio de Janeiro. As 
diferencas podem estar relacionadas principalmente ao tamanho da populacao e a dinamica de transmissao da COVID-19 em cada estado. O grafico 
tambem evidencia que o crescimento dos casos nao ocorreu de forma uniforme entre os estados, permitindo comparar a intensidade e a evolucao da 
pandemia em cada local. 
"""

st.header("Atividade 5 - Distribuição dos casos por município")

# O estado escolhido foi SP, e a partir dele foram selecionados os cinco municipios com maior numero de casos acumulados na data mais recente
# disponivel

sp_municipios = df_municipio[
    (df_municipio["estado"] == "SP") &
    (df_municipio["data"] == data_final)
].copy()

top5 = (
    sp_municipios
    .sort_values("casosAcumulado", ascending=False)
    .head(5)
)

# As coordenadas dos municipios escolhidos foram adicionadas manualmente, uma vez que o arquivo nao possui os campos latitude e longitude.

coordenadas = {
    "São Paulo": (-23.5505, -46.6333),
    "Campinas": (-22.9099, -47.0626),
    "São José do Rio Preto": (-20.8118, -49.3762),
    "São José dos Campos": (-23.1896, -45.8841),
    "Sorocaba": (-23.5015, -47.4526)
}

top5["latitude"] = top5["municipio"].map(
    lambda x: coordenadas.get(x, (None, None))[0]
)

top5["longitude"] = top5["municipio"].map(
    lambda x: coordenadas.get(x, (None, None))[1]
)

mapa = top5.dropna(
    subset=["latitude", "longitude"]
)


st.map(
    mapa[["latitude", "longitude"]]
)

st.dataframe(
    mapa[
        ["municipio", "casosAcumulado"]
    ]
)

"""
O mapa permite observar espacialmente onde estao concentrados os municipios com maior numero de casos. A visualizacao geografica facilita a 
identificacao de concentracoes e diferencas espaciais da pandemia.
"""


st.header("Atividade 6 - Casos novos x Óbitos novos")


# A semana 36 está incompleta no arquivo e apresenta valores zero. Por isso, utilizamos a semana 35, última semana informativa disponível.

semana_analise = 35

dados_6 = df_estado[
    df_estado["semanaEpi"] == semana_analise
].sort_values("casosNovos", ascending=False).head(10)


fig, ax = plt.subplots(figsize=(10, 6))

x = range(len(dados_6))

ax.bar(
    x,
    dados_6["casosNovos"],
    label="Casos novos"
)

ax.bar(
    x,
    dados_6["obitosNovos"],
    label="Óbitos novos"
)

ax.set_xticks(list(x))
ax.set_xticklabels(
    dados_6["estado"],
    rotation=45, 
    ha="right"
)

ax.set_title(
    "Casos novos e óbitos novos - Semana 35"
)

ax.set_xlabel("Estado")
ax.set_ylabel("Quantidade")
ax.legend()

plt.tight_layout()
st.pyplot(fig)

"""
Os casos novos são numericamente muito superiores aos óbitos novos. A existência de mais casos não significa que haverá proporcionalmente 
a mesma quantidade de óbitos. O gráfico permite comparar a magnitude das duas variáveis, mas não permite afirmar causalidade entre elas.
"""

st.header("Atividade 7 - Distribuição dos casos por região")


regioes = ["Norte", "Nordeste", "Sudeste"]

dados_7 = (
    df_estado[
        df_estado["regiao"].isin(regioes)
    ]
    .groupby(
        ["regiao", "semanaEpi"],
        as_index=False
    )["casosNovos"]
    .sum()
)


sns.set_theme(style="darkgrid")

fig, ax = plt.subplots(figsize=(10, 5))

sns.boxplot(
    data=dados_7,
    x="regiao",
    y="casosNovos",
    ax=ax
)

ax.set_title(
    "Distribuição dos casos novos por semana"
)

ax.set_xlabel("Região")
ax.set_ylabel("Casos novos")

st.pyplot(fig)

"""
O Sudeste apresenta valores semanais mais elevados, além de maior dispersão. O Nordeste apresenta valores intermediários.
O Norte apresenta os menores valores entre as três regiões. O boxplot permite comparar mediana, dispersão e possíveis valores extremos (outliers).
"""

st.header("Atividade 8 - Casos novos no Sudeste")

dados_8 = (
    df_estado[
        df_estado["regiao"] == "Sudeste"
    ]
    .groupby(
        "semanaEpi",
        as_index=False
    )["casosNovos"]
    .sum()
)


grafico_area = (
    alt.Chart(dados_8)
    .mark_area()
    .encode(
        x="semanaEpi:Q",
        y="casosNovos:Q"
    )
)


st.altair_chart(
    grafico_area,
    use_container_width=True
)

"""
O Sudeste foi escolhido por apresentar grande volume de casos na série analisada. 
As principais tendencias observadas no grafico sao:
- Alta volatilidade no numero de casos novos ao longo das semanas, com oscilacoes acentuadas;
- Picos expressivos nas semanas 3, 8, 10 e 19, sendo a semana 3 o maior pico;
- Apos a semana 19, observa-se uma reducao geral dos casos, embora com novos aumentos pontuais;
- Entre as semanas 20 e 35, os casos permanecem em niveis mais baixos, mas apresentam oscilacoes frequentes, com destaque para um novo aumento
na semana 35;
- A partir da semana 36, o grafico indica ausencia de valores, encerrando a serie apresentada.
"""

st.header("Atividade 9 - Correlação entre casos e óbitos")

# Os arquivos CSV de 2025 utilizados aqui nao possuem uma coluna referente a leitos hospitalares ocupados. Desta forma serao utilizadas somente
# as variaveis disponiveis: casos novos e obitos novos.

dados_9 = df_estado[
    df_estado["estado"] == "SP"
][
    ["casosNovos", "obitosNovos"]
].copy()


corr = dados_9.corr()


corr = corr.reset_index().melt(
    id_vars="index"
)

corr.columns = [
    "variavel_x",
    "variavel_y",
    "correlacao"
]


heatmap = (
    alt.Chart(corr)
    .mark_rect()
    .encode(
        x="variavel_x:N",
        y="variavel_y:N",
        color="correlacao:Q"
    )
)


st.altair_chart(
    heatmap,
    use_container_width=True
)

"""
A correlacao casosNovos x obitosNovos e relativamente alta, com um valor proximo de 0.83.
"""


st.header("Atividade 10 - Distribuição dos casos por região")


dados_10 = df_estado[
    df_estado["data"] == data_final
]


casos_regiao = (
    dados_10
    .groupby("regiao", as_index=False)["casosAcumulado"]
    .sum()
)


fig_pizza = px.pie(
    casos_regiao,
    names="regiao",
    values="casosAcumulado",
    title="Distribuição dos casos acumulados por região"
)


st.plotly_chart(
    fig_pizza
)

"""
A regiao Sudeste apresenta a maior participacao dos casos acumulados, seguida pelas regioes Sul e Nordeste. A regiao Norte apresenta a menor 
participacao entre as cinco regioes. Essa diferenca mostra que a distribuicao dos casos acumulados nao e uniforme entre as regioes brasileiras.

"""

st.header("Atividade 11 - Comparação entre regiões")


regioes_11 = ["Sudeste", "Nordeste"]

dados_11 = (
    df_estado[
        df_estado["regiao"].isin(regioes_11)
    ]
    .groupby(
        ["regiao", "semanaEpi"],
        as_index=False
    )[["casosNovos", "obitosNovos"]]
    .sum()
)

# Criação dos subplots:
# Linha 1 -> Casos novos
# Linha 2 -> Óbitos novos
# Colunas -> Sudeste e Nordeste

fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=[
        "Sudeste - Casos novos",
        "Nordeste - Casos novos",
        "Sudeste - Óbitos novos",
        "Nordeste - Óbitos novos"
    ],
    vertical_spacing=0.12
)

for i, regiao in enumerate(regioes_11, start=1):

    dados_regiao = dados_11[
        dados_11["regiao"] == regiao
    ]

    # Linha 1 - Casos novos
    fig.add_trace(
        go.Bar(
            x=dados_regiao["semanaEpi"],
            y=dados_regiao["casosNovos"],
            name=f"{regiao} - Casos novos"
        ),
        row=1,
        col=i
    )

    # Linha 2 - Óbitos novos
    fig.add_trace(
        go.Bar(
            x=dados_regiao["semanaEpi"],
            y=dados_regiao["obitosNovos"],
            name=f"{regiao} - Óbitos novos"
        ),
        row=2,
        col=i
    )


fig.update_layout(
    title="Comparação de casos novos e óbitos novos por semana",
    height=800,
    showlegend=False
)


fig.update_xaxes(
    title_text="Semana epidemiológica",
    row=2
)

fig.update_yaxes(
    title_text="Casos novos",
    row=1
)

fig.update_yaxes(
    title_text="Óbitos novos",
    row=2
)


st.plotly_chart(fig, use_container_width=True)

"""
O Sudeste apresenta um volume total de casos novos maior que o Nordeste no período analisado. Os óbitos também apresentam diferenças entre as 
regiões, embora em quantidade muito menor que os casos. A comparação mostra que a evolução da pandemia não ocorreu da mesma forma nas duas regiões.

"""


st.header("Atividade 12 - Casos acumulados ajustados pela população")


# Os mesmos cinco municípios selecionados na Atividade 5 serao utilizados aqui.


mapa_12 = mapa.copy()


mapa_12["casos_100mil"] = (
    mapa_12["casosAcumulado"] /
    mapa_12["populacaoTCU2019"] *
    100000
)


# Posição inicial do mapa.

view_state = pdk.ViewState(
    latitude=mapa_12["latitude"].mean(),
    longitude=mapa_12["longitude"].mean(),
    zoom=7
)


layer = pdk.Layer(
    "ColumnLayer",
    data=mapa_12,
    get_position=[
        "longitude",
        "latitude"
    ],
    get_elevation="casos_100mil",
    radius=10000,
    opacity=0.6
)


deck = pdk.Deck(
    initial_view_state=view_state,
    layers=[layer],
    tooltip={
        "text": "{municipio}: {casos_100mil}"
    }
)


st.pydeck_chart(deck)


st.dataframe(
    mapa_12[
        [
            "municipio",
            "casosAcumulado",
            "populacaoTCU2019",
            "casos_100mil"
        ]
    ]
)


"""
A densidade populacional pode favorecer a disseminacao da COVID-19 porque, em areas com maior concentracao de pessoas, ha mais contato e interacao
entre individuos, facilitando a transmissao do virus. No grafico, isso ajuda a entender por que municipios mais populosos podem apresentar muitos
casos, embora a quantidade absoluta de casos tambem dependa de outros fatores.
"""