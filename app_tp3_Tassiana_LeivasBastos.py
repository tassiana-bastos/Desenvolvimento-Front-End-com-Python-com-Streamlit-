"""
1.Escolha dos Datasets e Explicação do Objetivo e Motivação:

O Dataset escolhido para este projeto é o "Hospedagem_RJ_1997-2002.xls", disponibilizado pelo portal de dados abertos do município do Rio de Janeiro. 
O objetivo da aplicacao sera analisar a evolucao do setor de hospedagem turistica no Rio de janeiro, permitindo identificar variacoes nos valores das diarias, nos gastos 
medios dos visitantes e no tempo medio de permanencia ao longo dos anos e meses analisados. A escolha desse dataset se deve a possibilidade de relacionar diferentes
indicadores do turismo e transformar dados historicos em informacoes visuais de facil interpretacao.

A aplicacao desenvolvida em Streamlit tera como funcionalidades: upload de arquivo XLS, radio buttons, checkboxes, dropdowns, download dos dados filtrados, barra de
progresso, spinner, color picker, cache e o Session State.

Serao implementadas metricas resumidas, tabela interativa e visualizacoes como graficos de barra, linhas e pizza, alem de histograma e scatter plot, possibilitando observar
tanto a evolucao temporal quanto a relacao entre os indicadores.
"""

# Importacao das bibliotecas necessarias
import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt



# ============================================================
# CONFIGURACAO DA PAGINA
# ============================================================

st.set_page_config(
    page_title="Análise do Setor de Hospedagem Turística no Rio de Janeiro",
    page_icon="🏨",
    layout="wide"
)


# ============================================================
# FUNÇÃO PARA PREPARAR O DATASET
# ============================================================

def preparar_dataset(df):

    # Remove coluna de índice criada na exportação
    df = df.drop(
        columns=["Unnamed: 0"],
        errors="ignore"
    ).copy()


    # Mantém somente as linhas mensais
    meses = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro"
    ]


    # Cria coluna para armazenar o ano
    df["Ano"] = None

    ano_atual = None


    # Identifica o ano através das linhas
    # "Média 1997", "Média 1998", etc.
    for indice, periodo in df["Período"].items():

        periodo = str(periodo).strip()

        if periodo.startswith("Média"):

            ano_atual = int(
                periodo.split()[-1]
            )

        elif periodo in meses:

            df.loc[indice, "Ano"] = ano_atual


    # Mantém somente as linhas mensais
    df = df[
        df["Período"].isin(meses)
    ].copy()


    # Número do mês
    mapa_meses = {
        "Janeiro": 1,
        "Fevereiro": 2,
        "Março": 3,
        "Abril": 4,
        "Maio": 5,
        "Junho": 6,
        "Julho": 7,
        "Agosto": 8,
        "Setembro": 9,
        "Outubro": 10,
        "Novembro": 11,
        "Dezembro": 12
    }

    df["Mês"] = df["Período"].map(mapa_meses)


    # Converte Ano e Mês para inteiros
    df["Ano"] = df["Ano"].astype(int)
    df["Mês"] = df["Mês"].astype(int)


    # Abreviações dos meses
    abreviacoes = {
        1: "Jan.",
        2: "Fev.",
        3: "Mar.",
        4: "Abr.",
        5: "Mai.",
        6: "Jun.",
        7: "Jul.",
        8: "Ago.",
        9: "Set.",
        10: "Out.",
        11: "Nov.",
        12: "Dez."
    }


    # Cria o período no formato "Jan. 1997"
    df["Período"] = (
        df["Mês"].map(abreviacoes)
        + " "
        + df["Ano"].astype(str)
    )


    # Converte os indicadores para números
    colunas_numericas = [
        "Diária média",
        "Gasto médio",
        "Permanência Média"
    ]

    for coluna in colunas_numericas:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )


    # Ordena cronologicamente
    df = df.sort_values(
        ["Ano", "Mês"]
    ).reset_index(drop=True)


    # Reorganiza as colunas
    df = df[
        [
            "Período",
            "Ano",
            "Mês",
            "Diária média",
            "Gasto médio",
            "Permanência Média"
        ]
    ]

    return df


# ============================================================
# TITULO DA APLICACAO
# ============================================================

st.title(
    "Análise do Setor de Hospedagem Turística "
    "no Rio de Janeiro (1997-2002)"
)

st.write(
    "Faça o upload do arquivo XLS."
)


# ============================================================
# QUESTÃO 2 - UPLOAD DO ARQUIVO XLS
# ============================================================

st.header("Upload do Arquivo XLS")

arquivo = st.file_uploader(
    "Escolha o arquivo XLS",
    type=["xls"]
)

# Questao 7 - Color Picker

st.header("Escolha a cor do tema da aplicação")

cor_fundo = st.color_picker(
    "Selecione a cor de fundo:",
    value="#FFFFFF"
)

cor_texto = st.color_picker(
    "Selecione a cor do texto:",
    value="#000000"
)

# Aplica as cores selecionadas ao tema da aplicação
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {cor_fundo};
            color: {cor_texto};
        }}

        .stMarkdown,
        .stText,
        .stHeader,
        .stSubheader,
        label,
        p {{
            color: {cor_texto};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Questao 8 - Utilizar funcionalidade de cache
@st.cache_data(ttl=600)
def carregar_dados(arquivo):
    return pd.read_excel(
        arquivo,
        sheet_name=0,
        header=4
    )

# Questao 9 - Utilizar funcionalidade de Session State

if "ano_selecionado" not in st.session_state:
    st.session_state.ano_selecionado = "Todos"

if "diaria" not in st.session_state:
    st.session_state.diaria = True

if "gasto" not in st.session_state:
    st.session_state.gasto = True

if "permanencia" not in st.session_state:
    st.session_state.permanencia = True

if "mes_selecionado" not in st.session_state:
    st.session_state.mes_selecionado = "Todos"

# ============================================================
# PROCESSAMENTO DO ARQUIVO XLS
# ============================================================

if arquivo is not None:

    # Questao 6 - Barra de Progresso e Spinner

    barra_progresso = st.progress(0, text="Processando o arquivo...")

    with st.spinner(
        "Processando o arquivo, aguarde...", show_time=True
    ):
        # Etapa 1: Leitura do arquivo XLS
        barra_progresso.progress(25, text="Lendo o arquivo XLS...")

        dados = carregar_dados(arquivo)

        # Etapa 2: Preparacao dos dados
        barra_progresso.progress(60, text="Preparando os dados...")

        df = preparar_dataset(dados)

        # Etapa 3 - Finalização
        barra_progresso.progress(
            100,
            text="Processamento concluído!"
        )

    st.success(
        "Arquivo carregado e processado com sucesso!"
    )

    
    # QUESTÃO 3 - FILTRO DE DADOS E SELEÇÃO
    

    st.header("Filtros de Dados")


    # --------------------------------------------------------
    # RADIO - Filtro de Ano
    # --------------------------------------------------------

    anos = sorted(
        df["Ano"].unique()
    )

    ano_selecionado = st.radio(
        "Selecione o Ano:",
        ["Todos"] + anos, 
        key="ano_selecionado"
    )


    
    # CHECKBOX - Seleção das métricas
    

    st.subheader(
        "Selecione as informações que deseja visualizar:"
    )

    diaria = st.checkbox(
        "Diária Média",
        key="diaria"
    )

    gasto = st.checkbox(
        "Gasto Médio",
        key="gasto"
    )

    permanencia = st.checkbox(
        "Permanência Média",
        key="permanencia"
    )


    
    # SELECTBOX - Filtro de Mês
    

    meses = [
        "Todos",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro"
    ]

    mes_selecionado = st.selectbox(
        "Selecione o Mês:",
        meses,
        key="mes_selecionado"
    )


    # --------------------------------------------------------
    # FILTRAGEM DOS DADOS
    # --------------------------------------------------------

    df_filtrado = df.copy()


    # Filtragem por Ano
    if ano_selecionado != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["Ano"] == ano_selecionado
        ]


    # Filtragem por Mês
    if mes_selecionado != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["Período"].str.startswith(
                mes_selecionado[:3]
            )
        ]


    # --------------------------------------------------------
    # AVISO SOBRE DADOS NÃO DISPONÍVEIS
    # --------------------------------------------------------

    if (
        gasto
        and not df_filtrado.empty
        and df_filtrado["Gasto médio"].isna().all()
    ):

        st.info(
            "ℹ️ Os dados de Gasto médio não estão "
            "disponíveis para o período selecionado."
        )


    # --------------------------------------------------------
    # SELEÇÃO DAS COLUNAS PELO CHECKBOX
    # --------------------------------------------------------

    colunas_selecionadas = [
        "Período"
    ]


    if diaria:

        colunas_selecionadas.append(
            "Diária média"
        )


    if gasto:

        if df_filtrado["Gasto médio"].notna().any():

            colunas_selecionadas.append(
                "Gasto médio"
            )


    if permanencia:

        colunas_selecionadas.append(
            "Permanência Média"
        )


    
    # QUESTÃO 4 - TABELA INTERATIVA
    

    st.header("Tabela Interativa")


    if len(colunas_selecionadas) == 1:

        st.warning(
            "Selecione pelo menos uma informação "
            "para visualizar os dados."
        )

    elif df_filtrado.empty:

        st.warning(
            "Não existem dados disponíveis para "
            "os filtros selecionados."
        )

    else:

        st.write(
            "A tabela abaixo apresenta os dados "
            "filtrados de forma interativa. "
            "Você pode ordenar as colunas clicando "
            "nos cabeçalhos."
        )

        st.dataframe(
            df_filtrado[colunas_selecionadas],
            width="stretch",
            hide_index=True
        )

# Questao 5 - Download dos dados filtrados

# Download dos Dados Filtrados

    st.header("Download dos Dados Filtrados")

    st.write(
    "Clique no botão abaixo para baixar os dados filtrados em formato Excel."
    )

# Verifica se existem dados para exportar
    if df_filtrado.empty:

        st.warning(
        "Não existem dados para download com os filtros selecionados."
    )

    else:

    # Cria o arquivo Excel em memória
        arquivo_xls = BytesIO()

        with pd.ExcelWriter(
            arquivo_xls,
            engine="openpyxl"
            ) as writer:

        # Garante que pelo menos uma planilha seja criada
            df_filtrado.to_excel(
            writer,
            index=False,
            sheet_name="Dados Filtrados"
        )

    # Volta para o início do arquivo em memória
    arquivo_xls.seek(0)

    # Botão de download
    st.download_button(
        label="📥 Baixar Dados Filtrados",
        data=arquivo_xls,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    # QUESTÃO 10 - GRÁFICOS SIMPLES


    st.header("Visualizações dos Dados")


# GRÁFICO DE BARRAS

    st.subheader("Diária Média por Ano")

    df_anual= (
        df.groupby("Ano")[["Diária média"]].mean().reset_index()
    )

    st.bar_chart(
        df_anual,
        x="Ano",
        y="Diária média"
    )

# GRÁFICO DE LINHAS

    st.subheader("Evolução Mensal da Diária Média")

    df_grafico= df.copy()

    df_grafico["Data"]= pd.to_datetime(
        dict(year=df_grafico["Ano"], month=df_grafico["Mês"], day=1)
    )

    df_grafico= df_grafico.sort_values("Data")

    st.line_chart(
        df_grafico,
        x="Data",
        y="Diária média"
    )

# ------------------------------------------------------------
# GRÁFICO DE PIZZA
# ------------------------------------------------------------

    st.subheader("Participacao de Cada Ano no Total da Diária Média")
    df_pizza = (
        df.groupby("Ano")["Diária média"].sum()
    )

    fig, ax = plt.subplots()
    ax.pie(
        df_pizza.values, 
        labels=df_pizza.index,
        autopct='%1.1f%%'
    )

    ax.set_title("Participação de Cada Ano na Diária Média Total")  

    st.pyplot(fig)

    # QUESTÃO 11 - GRÁFICOS AVANÇADOS

    st.header("Visualizações Avançadas")

    # Histograma

    st.subheader("Distribuição da Diária Média")

    fig, ax = plt.subplots()

    ax.hist(
    df["Diária média"].dropna(),
    bins=10
    )

    ax.set_title("Distribuição dos Valores de Diária Média")
    ax.set_xlabel("Diária Média")
    ax.set_ylabel("Frequência")

    st.pyplot(fig)


# ------------------------------------------------------------
# SCATTER PLOT
# ------------------------------------------------------------

    st.subheader("Relação entre Diária Média e Permanência Média")

    df_scatter = df[
    ["Diária média", "Permanência Média"]
    ].dropna()

    fig, ax = plt.subplots()

    ax.scatter(
    df_scatter["Diária média"],
    df_scatter["Permanência Média"]
    )

    ax.set_title(
    "Diária Média x Permanência Média"
    )

    ax.set_xlabel("Diária Média")
    ax.set_ylabel("Permanência Média")

    st.pyplot(fig)


# QUESTÃO 12 - MÉTRICAS BÁSICAS


    st.header("Resumo dos Dados")


    # Calcula as métricas
    total_registros = len(df)

    media_diaria = df["Diária média"].mean()

    media_gasto = df["Gasto médio"].mean()

    media_permanencia = df["Permanência Média"].mean()

    soma_diaria = df["Diária média"].sum()


# Exibe as métricas em colunas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
        label="Total de Registros",
        value=total_registros
    )

    with col2:
        st.metric(
        label="Diária Média",
        value=f"R$ {media_diaria:.2f}"
    )

    with col3:
        st.metric(
        label="Gasto Médio",
        value=f"R$ {media_gasto:.2f}"
    )

    with col4:
        st.metric(
        label="Permanência Média",
        value=f"{media_permanencia:.2f} dias"
    )

    st.metric(
    label="Soma dos Valores de Diária Média",
    value=f"R$ {soma_diaria:.2f}"
)

else:

    # Mensagem exibida enquanto nenhum arquivo foi carregado
    st.info(
        "Selecione o arquivo XLS do portal Data.Rio."
    )


