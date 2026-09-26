
# Importacao das bibliotecas
import streamlit as st
from statsbombpy import sb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch

# Configuracao da pagina

st.set_page_config(
    page_title= "Sports Analytics Dashboard",
    page_icon="⚽",
    layout="wide"
)

# Funcoes para carregamento dos dados

@st.cache_data # para evitar o processamento repetitivo
def carregar_competicoes():
    """
    Funcao elaborada para carregar os campeonatos disponiveis no StatsBomb.
    """
    return sb.competitions()

@st.cache_data
def carregar_partidas(competition_id, season_id):
    """
    Carrega as partidas de uma competicao e temporada selecionadas.
    """
    return sb.matches(
        competition_id=competition_id,
        season_id=season_id
    )

# Carregamento dos Eventos

@st.cache_data
def carregar_eventos(match_id):
    """
    Carrega todos os eventos registrados para uma partida
    """

    return sb.events(match_id=match_id)

@st.cache_data
def carregar_jogadores(match_id):
    """
    Carrega os jogadores das equipes de uma partida selecionada.
    """

    lineups = sb.lineups(match_id)

    jogadores = []

    for equipe, dados in lineups.items():
        if "player_name" in dados.columns:
            for nome_jogador in dados["player_name"].dropna().unique():
                jogadores.append({
                    "jogador": nome_jogador, 
                    "equipe": equipe
                })

    return jogadores

@st.cache_data
def converter_para_csv(df):
    """
    Converte o DataFrame filtrado para CSV.
    """

    return df.to_csv(
        index=False
    ).encode("utf-8-sig")

# Calculo das estatisticas basicas

def calcular_estatisticas_partida(eventos):
    """
    Funcao criada para calcular estatisticas basicas da partida a partir dos eventos do StatsBomb
    """

    # Total de gols
    gols= (
        (eventos["type"] == "Shot")
        & (eventos["shot_outcome"] == "Goal")
    ).sum()

    # Total de chutes/finalizacoes
    chutes= (
        eventos["type"] == "Shot"
    ).sum()

    # Taxa de conversao de chutes em gol
    taxa_conversao= (
        (gols / chutes) * 100
        if chutes > 0
        else 0
    )

    # Total de passes
    passes= (
        eventos["type"] == "Pass"
    ).sum()

    # Total de passes bem-sucedidos
    passes_bem_sucedidos= (
        (eventos["type"] == "Pass")
        & (eventos["pass_outcome"].isna())
    ).sum()

    # Total de desarmes
    desarmes= (
        (eventos["type"] == "Duel")
        & (eventos["duel_type"] == "Tackle")
    ).sum()

    # Total de interceptacoes
    interceptacoes= (
        eventos["type"] == "Interception"
    ).sum()

    # Total de recuperacoes de bola
    recuperacoes= (
        eventos["type"] == "Ball Recovery"
    ).sum()

    return {
        "Gols": int(gols), 
        "Chutes": int(chutes), 
        "Passes": int(passes),
        "Passes bem-sucedidos": int(passes_bem_sucedidos), 
        "Taxa de conversao": float(taxa_conversao),
        "Desarmes": int(desarmes), 
        "Interceptacoes": int(interceptacoes), 
        "Recuperacoes": int(recuperacoes)
    }




# Funcao para preparar o dataframe de eventos

def preparar_dataframe_eventos(eventos):
    """
    Funcao para selecionar e organizar as principais informacoes dos eventos para exibicao no dashboard.
    """

    colunas_desejadas= [
        "minute", 
        "second", 
        "period", 
        "team", 
        "player", 
        "type", 
        "pass_outcome", 
        "shot_outcome", 
        "duel_type", 
        "location"
    ]

    # Verificacao para manter somente as colunas que realmente existem
    colunas_disponiveis= [
        coluna 
        for coluna in colunas_desejadas
        if coluna in eventos.columns
    ]

    df_eventos= eventos[colunas_disponiveis].copy()

    # Renomeacao das colunas para apresentacao no dashboard
    nomes_colunas= {
        "minute": "Minuto", 
        "second": "Segundo", 
        "period": "Periodo", 
        "team": "Equipe", 
        "player": "Jogador", 
        "type": "Evento", 
        "pass_outcome": "Resultado do passe", 
        "shot_outcome": "Resultado do chute", 
        "duel_type": "Tipo de duelo", 
        "location": "Localizacao"
    }

    df_eventos= df_eventos.rename(
        columns= nomes_colunas
    )

    return df_eventos

# Estatisticas por equipe
def preparar_estatisticas_equipes(eventos):

    equipes= eventos["team"].dropna().unique()

    dados=[]

    for equipe in equipes:

        eventos_equipe= eventos[
            eventos["team"] == equipe
        ]

        passes = (
            eventos_equipe["type"] == "Pass"
        ).sum()

        chutes = (
            eventos_equipe["type"] == "Shot"
        ).sum()

        gols = (
            (eventos_equipe["type"] == "Shot")
            &
            (eventos_equipe["shot_outcome"] == "Goal")
        ).sum()

        recuperacoes = (
            eventos_equipe["type"] == "Ball Recovery"
        ).sum()

        interceptacoes = (
            eventos_equipe["type"] == "Interception"
        ).sum()

        dados.append({
            "Equipe": equipe,
            "Passes": passes,
            "Chutes": chutes,
            "Gols": gols,
            "Recuperacoes": recuperacoes,
            "Interceptacoes": interceptacoes
        })

    return pd.DataFrame(dados)

# Estatisticas por jogador
def preparar_estatisticas_jogadores(eventos):

    dados = []

    jogadores = eventos[
        "player"
    ].dropna().unique()

    for jogador in jogadores:

        eventos_jogador = eventos[
            eventos["player"] == jogador
        ]

        passes = (
            eventos_jogador["type"] == "Pass"
        ).sum()

        chutes = (
            eventos_jogador["type"] == "Shot"
        ).sum()

        gols = (
            (eventos_jogador["type"] == "Shot")
            &
            (eventos_jogador["shot_outcome"] == "Goal")
        ).sum()

        equipe = eventos_jogador[
            "team"
        ].dropna()

        equipe = (
            equipe.iloc[0]
            if not equipe.empty
            else "Desconhecida"
        )

        dados.append({
            "Jogador": jogador,
            "Equipe": equipe,
            "Passes": passes,
            "Chutes": chutes,
            "Gols": gols
        })

    return pd.DataFrame(dados)


# Funcoes para visualizacoes

def gerar_visualizacoes(eventos, eventos_partida=None): # Eventos filtrados pelo jogador/formulario e todos os eventos da partida
    """
    Apresenta as estatisticas basicas e a tabela de eventos.
    """
    if eventos_partida is None:
        eventos_partida= eventos

    estatisticas= calcular_estatisticas_partida(
        eventos
    )

    estatisticas_partida= calcular_estatisticas_partida(
        eventos_partida
    )

    # indicadores

    st.subheader("Estatisticas basicas da partida")

    col1, col2, col3= st.columns(3)

    col1.metric(
        "⚽ Gols da partida",
        estatisticas_partida["Gols"], 
        delta= "Destaque", 
        delta_color="normal"      
    )

    col2.metric(
        "🥅 Chutes",
        estatisticas["Chutes"],
        delta="Finalizacoes", 
        delta_color="normal"
    )

    col3.metric(
        "🎯 Passes bem-sucedidos",
        estatisticas["Passes bem-sucedidos"], 
        delta="Completados", 
        delta_color="normal"
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "🎯 Taxa de conversão",
        f'{estatisticas["Taxa de conversao"]:.1f}%',
        delta="Gols / chutes",
        delta_color="normal"
    )

    col5.metric(
        "🛡️ Desarmes",
        estatisticas["Desarmes"]
    )

    col6.metric(
        "🔵 Recuperações",
        estatisticas["Recuperacoes"]
    )

    st.divider()

    # Dataframe dos eventos

    st.subheader("Eventos da partida")

    st.write(
        """
        A tabela apresenta os eventos registrados durante a partida, incluindo passes, conducoes, recuperacoes de bola, finalizacoes,
         interceptacoes, duelos e outras acoes registradas pelo StatsBomb.
        """
    )        

    df_eventos= preparar_dataframe_eventos(
        eventos
    )

    st.dataframe(
        df_eventos, 
        width= "stretch", 
        hide_index=True
    )

# Mapa de chutes
def gerar_mapa_chutes(eventos, jogador_selecionado):

    # Seleciona apenas os chutes
    chutes= eventos[
        eventos["type"] == "Shot"
    ].copy()

    # Filtrar o jogador
    if jogador_selecionado != "Todos os jogadores":
        chutes= chutes[chutes["player"] == jogador_selecionado
        ].copy()

    if chutes.empty:
        st.warning("Nao existem chutes para a selecao realizada.")
        return

    # extracao das coordenadas
    chutes[["x", "y"]]= pd.DataFrame(
        chutes["location"].tolist(), 
        index=chutes.index
    )

    pitch= Pitch(
        pitch_type="statsbomb", 
    )

    fig, ax= pitch.draw(
        figsize=(12,8)
    )

    resultados= chutes["shot_outcome"].fillna(
        "Sem resultado"
    ).unique()

    marcadores= {
        "Goal": "*", 
        "Saved": "o", 
        "Off T": "x", 
        "Blocked": "s",
        "Post": "D"
    }

    for resultado in resultados:

        chutes_resultado= chutes[
            chutes["shot_outcome"].fillna(
                "Sem resultado"
            ) == resultado
        ]

        pitch.scatter(
            chutes_resultado["x"], 
            chutes_resultado["y"], 
            ax=ax, 
            s=100, 
            marker=marcadores.get(
                resultado, 
                "o"
            ), 
            label=resultado
        )

    ax.set_title(
        "Mapa de Chutes", 
        fontsize=16, 
        pad=20
    )

    ax.legend(
        loc="upper center", 
        bbox_to_anchor=(0.5, -0.03), 
        ncol=3
    )

    st.pyplot(fig)

# Heatmap de chutes
def gerar_heatmap_chutes(eventos, jogador_selecionado):

    # Seleciona apenas os chutes
    chutes= eventos[
        eventos["type"] == "Shot"
    ].copy()

    # Filtragem pelo jogador selecionado

    if jogador_selecionado != "Todos os jogadores":
        chutes= chutes[
            chutes["player"] == jogador_selecionado
        ].copy()

    if chutes.empty:
        st.warning("Nao existem chutes para gerar o heatmap.")
        return

    chutes[["x", "y"]] = pd.DataFrame(
        chutes["location"].tolist(),
        index=chutes.index
    )    

    # Cria o campo de futebol
    pitch= Pitch(
        pitch_type="statsbomb", 
        pitch_color="#0B132B",
        line_color="white"
    )

    #Calculo da quantidade de chutes por regiao do campo
    bin_statistic= pitch.bin_statistic(
        chutes["x"], 
        chutes["y"], 
        statistic= "count", 
        bins=(10, 8)
    )

    #Cria a figura

    fig, ax= pitch.draw(
        figsize=(12,8)
    )
    # Adicao do heatmap
    pitch.heatmap(
        bin_statistic, 
        ax=ax
    )

    ax.set_title(
        "Heatmap da Distribuicao dos Chutes", 
        fontsize=16, 
        color="white", 
        pad=20
    )

    st.pyplot(fig)


# Mapa de passes

def gerar_mapa_passes(eventos, jogador_selecionado):

    # Seleciona apenas os passes
    passes= eventos[
        eventos["type"] == "Pass"
    ].copy()

    # Filtra pelo jogador selecionado

    if jogador_selecionado != "Todos os jogadores":
        passes= passes[
            passes["player"] == jogador_selecionado
        ].copy()

    # Extrai as coordenadas iniciais e finais
    passes[["x_inicio", "y_inicio"]]= pd.DataFrame(
        passes["location"].tolist(), 
        index=passes.index
    )

    passes[["x_fim", "y_fim"]]=pd.DataFrame(
        passes["pass_end_location"].tolist(), 
        index=passes.index
    )

    pitch= Pitch( # criacao do campo
        pitch_type="statsbomb"
    )

    fig, ax= pitch.draw(
        figsize=(12,8)
    )
    # identificacao das equipes
    equipes= passes["team"].dropna().unique()

    cores= [
        "#4FC3F7",
        "#FFCA28"
    ]
    # Desenho dos passes por equipe
    for i, equipe in enumerate(equipes):

        passes_equipe= passes[
            passes["team"] == equipe
        ]

        pitch.arrows(
            passes_equipe["x_inicio"], 
            passes_equipe["y_inicio"], 
            passes_equipe["x_fim"], 
            passes_equipe["y_fim"], 
            ax=ax, 
            color=cores[i % len(cores)], 
            width=1.5, 
            headwidth=4, 
            headlength=4, 
            label=equipe
        )

    ax.set_title(
        "Mapa de Passes", 
        fontsize=16, 
        pad=20
    )

    ax.legend(
        loc="upper center", 
        bbox_to_anchor=(0.5, -0.03), 
        ncol=2
    )

    st.pyplot(fig)


# Grafico de estatisticas por equipe com Matplotlib

def gerar_grafico_estatisticas_equipes(eventos):

    df_estatisticas = preparar_estatisticas_equipes(
        eventos
    )

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    x = np.arange(
        len(df_estatisticas)
    )

    largura = 0.2

    ax.bar(
        x - largura,
        df_estatisticas["Passes"],
        largura,
        label="Passes"
    )

    ax.bar(
        x,
        df_estatisticas["Chutes"],
        largura,
        label="Chutes"
    )

    ax.bar(
        x + largura,
        df_estatisticas["Gols"],
        largura,
        label="Gols"
    )

    ax.set_title(
        "Comparacao das Estatisticas das Equipes"
    )

    ax.set_xlabel(
        "Equipe"
    )

    ax.set_ylabel(
        "Quantidade"
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        df_estatisticas["Equipe"],
        rotation=15
    )

    ax.legend()

    fig.tight_layout()

    st.pyplot(fig)


# Relacao entre passes e chutes com Seaborn
def gerar_grafico_passes_chutes(eventos):

    df_jogadores = preparar_estatisticas_jogadores(
        eventos
    )

    if df_jogadores.empty:
        st.warning(
            "Nao existem dados suficientes para gerar o grafico."
        )
        return

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    sns.scatterplot(
        data=df_jogadores,
        x="Passes",
        y="Chutes",
        hue="Equipe",
        size="Gols",
        sizes=(60, 300),
        ax=ax
    )

    ax.set_title(
        "Relacao entre Passes e Chutes por Jogador"
    )

    ax.set_xlabel(
        "Numero de passes"
    )

    ax.set_ylabel(
        "Numero de chutes"
    )

    fig.tight_layout()

    st.pyplot(fig)


# Funcao principal das visualizacoes
def gerar_visualizacoes_avancadas(
    eventos,
    jogador_selecionado
):

    st.subheader(
        "Visualizações da partida"
    )

    st.write("""
        As visualizações abaixo permitem explorar a distribuição
        espacial das ações e comparar estatísticas dos jogadores
        e das equipes durante a partida selecionada.
    """)

    # Mapas de futebol
    tab_passes, tab_chutes, tab_heatmap = st.tabs(
        [
            "⚽ Mapa de passes",
            "🥅 Mapa de chutes",
            "🔥 Heatmap de chutes"
        ]
    )

    with tab_passes:

        st.caption(
            "Distribuição espacial dos passes registrados na partida."
        )

        gerar_mapa_passes(
            eventos,
            jogador_selecionado
        )

    with tab_chutes:

        st.caption(
            "Localização das finalizações e seus respectivos resultados."
        )

        gerar_mapa_chutes(
            eventos,
            jogador_selecionado
        )

    with tab_heatmap:

        st.caption(
            "Concentração espacial das finalizações."
        )

        gerar_heatmap_chutes(
            eventos,
            jogador_selecionado
        )

    st.divider()

    # Estatisticas
    st.subheader(
        "Comparação das estatísticas"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "**Matplotlib — Estatísticas por equipe**"
        )

        gerar_grafico_estatisticas_equipes(
            eventos
        )

    with col2:

        st.write(
            "**Seaborn — Passes × Chutes por jogador**"
        )

        gerar_grafico_passes_chutes(
            eventos
        )


# Funcao para construir a interface

def construir_interface():

    # Cabecalho

    with st.container(): 
        st.title("⚽ Sports Analytics Dashboard")

        st.write(
            """
            Dashboard interativo para analise de dados de futebol utilizando dados do StatsBomb.
            """
        )
    # Carregamento inicial dos dados

    barra_progresso= st.progress(
        0, 
        text="Preparando o dashboard..."
    )

    with st.spinner(
        "Carregando as competicoes disponiveis no StatsBomb..."):
        competicoes= carregar_competicoes()

    barra_progresso.progress(
        30, 
        text="Competicoes carregadas."
    )

    if competicoes.empty:
        st.error("Nao foi possivel carregar as competicoes.")
        st.stop()

    # Sidebar - filtros

    st.sidebar.header("Filtros da analise")

    # Selecao do campeonato
    competicoes["nome_competicao"] = (
        competicoes["competition_name"]
        + " - "
        + competicoes["country_name"]
    )

    competicao_selecionada= st.sidebar.selectbox(
        "Selecione o campeonato:", 
        competicoes["nome_competicao"].unique().tolist()
    )

    # Recupera o registro da competicao selecionada
    competencia= competicoes[
        competicoes["nome_competicao"] == competicao_selecionada
    ].iloc[0]

    competition_id= int(competencia["competition_id"])

    # Selecao da temporada

    temporadas= competicoes[
        competicoes["competition_id"] == competition_id
    ].copy()

    temporadas["temporada_nome"] = temporadas["season_name"]

    temporada_selecionada= st.sidebar.selectbox(
        "Selecione a temporada:", 
        temporadas["temporada_nome"].tolist()
    )

    temporada= temporadas[
        temporadas["temporada_nome"] == temporada_selecionada
    ].iloc[0]

    season_id = int(temporada["season_id"])

    # Carregamento das partidas

    with st.spinner(
        "Carregando as partidas da temporada selecionada..."
        ):

        partidas= carregar_partidas(
            competition_id, 
            season_id
            )
    barra_progresso.progress(
        55, 
        text="Partidas carregadas."
    )


    if partidas.empty:
        st.warning(
            "Nao existem partidas disponiveis para a competicao e a temporada selecionadas."
        )
        st.stop()

    # Selecao da partida

    partidas["partida"]= (
        partidas["home_team"]
        + " x "
        + partidas["away_team"]
    )

    partida_selecionada= st.sidebar.selectbox(
        "Selecione a partida:", 
        partidas["partida"].tolist()
    )

    partida = partidas[
        partidas["partida"] == partida_selecionada
    ].iloc[0]

    match_id= int(partida["match_id"])
    # st.write("MATCH ID:", match_id)

    # Carregamento dos eventos da partida selecionada
    with st.spinner(
        "Carregando os eventos da partida..."
        ):
        eventos= carregar_eventos(match_id)

    barra_progresso.progress(
        75, 
        text="Eventos da partida carregados."
        )

    # Carregamento dos jogadores

    with st.spinner(
        "Carregando os jogadores da partida..."
        ):
        jogadores= carregar_jogadores(match_id)

    barra_progresso.progress(
        100, 
        text="Dados carregados com sucesso."
        )

    # Remocao da barra apos o carregamento
    barra_progresso.empty()

 
    #st.write("Tipos de eventos registrados na partida:")
    #st.write(eventos["type"].value_counts())
 

    # Selecao e filtro de jogadores

    nomes_jogadores= sorted(
        list(
            set(
                jogador["jogador"]
                for jogador in jogadores
                if jogador["jogador"]
            )
        )
    )

    # Formulario interativo da analise

    with st.sidebar.form("formulario_analise"):

        st.subheader("⚙️ Opções da análise")

        # Dropdown
        jogador_form= st.selectbox(
            "Selecione o jogador:", 
            ["Todos os jogadores"] + nomes_jogadores
        )

        # Radio button
        periodo_form= st.radio(
            "Periodo da partida:", 
            ["Partida completa", "1º tempo", "2º tempo"]
        )

        # Quantidade de eventos
        quantidade_eventos_form= st.slider(
            "Quantidade de eventos a visualizar:", 
            min_value=10, 
            max_value=min(500, len(eventos)), 
            value=min(100, len(eventos)), 
            step=10
        )

        # Checkbox
        mostrar_detalhes_form= st.checkbox(
            "Mostrar detalhes dos eventos", 
            value=True
        )

        aplicar_formulario= st.form_submit_button(
            "Aplicar filtros", 
            width="stretch"
        )

        # Caixa de texto

        observacao_form= st.text_input(
            "Observacao da analise:", 
            placeholder="Ex: analisar desempenho ofensivo"
        )

    # Inicializacao dos valores persistentes

    if "jogador_form" not in st.session_state:
        st.session_state.jogador_form = "Todos os jogadores"

    if "periodo_form" not in st.session_state:
        st.session_state.periodo_form= "Partida completa"

    if "quantidade_eventos_form" not in st.session_state:
        st.session_state.quantidade_eventos_form= min(
            100, 
            len(eventos)
        )

    if "mostrar_detalhes_form" not in st.session_state:
        st.session_state.mostrar_detalhes_form= True

    if "observacao_form" not in st.session_state:
        st.session_state.observacao_form= ""

    if aplicar_formulario:

        st.session_state.jogador_form= jogador_form
        st.session_state.periodo_form= periodo_form
        st.session_state.quantidade_eventos_form= quantidade_eventos_form
        st.session_state.mostrar_detalhes_form= mostrar_detalhes_form
        st.session_state.observacao_form= observacao_form

    # Recuperacao dos valores persistidos

    jogador_selecionado= st.session_state.jogador_form
    periodo_selecionado= st.session_state.periodo_form
    quantidade_eventos= st.session_state.quantidade_eventos_form
    mostrar_detalhes= st.session_state.mostrar_detalhes_form

    # Filtro de periodo

    eventos_filtrados= eventos.copy()

    if periodo_selecionado == "1º tempo":
        eventos_filtrados= eventos_filtrados[
            eventos_filtrados["period"] == 1
        ]

    elif periodo_selecionado == "2º tempo":
        eventos_filtrados = eventos_filtrados[
            eventos_filtrados["period"] == 2
        ]

    # Filtro de jogador

    if jogador_selecionado != "Todos os jogadores":

        eventos_filtrados= eventos_filtrados[
            eventos_filtrados["player"] == jogador_selecionado
        ].copy()


    # Download dos dados filtrados

    st.subheader("⬇️ Download dos dados filtrados")
    if eventos_filtrados.empty:
            st.warning("Nenhum evento encontrado para o jogador selecionado."
        )

    else:
        # DataFrame preparado para exibicao
        
        df_eventos_filtrados = preparar_dataframe_eventos(
            eventos_filtrados
             )

        # CSV da tabela organizada

        csv_eventos_filtrados = converter_para_csv(
            df_eventos_filtrados
            )

        # CSV com os eventos completos

        csv_eventos_completos = converter_para_csv(
            eventos_filtrados
            )

        # Nome utilizado nos arquivos

        nome_jogador_arquivo = (
            "todos_jogadores"

            if jogador_selecionado == "Todos os jogadores"

            else jogador_selecionado
            .lower()
            .replace(" ", "_")
            )

        # Organizacao dos botoes

        col_download1, col_download2 = st.columns(2)

        with col_download1:

                st.download_button(
                label="📥 Baixar tabela filtrada (CSV)",
                data=csv_eventos_filtrados,
                file_name=(
                    f"eventos_{nome_jogador_arquivo}.csv"
                ),
                mime="text/csv",
                width="stretch",
                on_click="ignore"
            )

        # Download dos eventos completos

        with col_download2:

            st.download_button(
                label="📥 Baixar eventos completos (CSV)",
                data=csv_eventos_completos,
                file_name=(
                    f"eventos_completos_{nome_jogador_arquivo}.csv"
                ),
                mime="text/csv",
                width="stretch",
                on_click="ignore"
            )       


    # Informacoes da Selecao

    with st.container():
        st.subheader("Selecao da analise")

        col1, col2, col3 = st.columns(3)

        col1.metric(
                "Competicao", 
                competencia["competition_name"]
                )

        col2.metric(
                "Temporada", 
                temporada_selecionada
                )

        col3.metric(
                "Partida", 
            partida_selecionada
            )

    # Status dos filtros aplicados

    if jogador_selecionado == "Todos os jogadores":

        st.info(
            f"Exibindo até {quantidade_eventos} eventos do {periodo_selecionado.lower()}."
        )

    else:

        st.success(
            f"Filtro aplicado: eventos de **{jogador_selecionado}** - {periodo_selecionado.lower()}."
        )

    # Abas do dashboard

    tab1, tab2, tab3 = st.tabs(
        [
            "📊 Visão geral",
            "📈 Visualizações",
            "👤 Jogador"
        ]
    )

    # Visao Geral

    with tab1:

        gerar_visualizacoes(
            eventos_filtrados, # chama jogador/filtros selecionados
            eventos # chama a partida inteira
        )

    # Visualizacoes

    with tab2:
        gerar_visualizacoes_avancadas(
        eventos_filtrados, 
        jogador_selecionado
        )

    # Aba 3 - jogador

    with tab3:
        st.subheader("Analise individual de cada jogador")

        if jogador_selecionado == "Todos os jogadores":

            st.info(
                "Selecione um jogador e clique em Aplicar para visualizar seus eventos."
            )

        else:

            st.write(
                f"Jogador selecionado: "
                f"**{jogador_selecionado}**"
            )

            st.write(
                f"Quantidade de eventos: ", 
                f"**{len(eventos_filtrados)}**"
            )

            st.dataframe(
                preparar_dataframe_eventos(
                    eventos_filtrados
                ), 
                width="stretch", 
                hide_index=True
            )


# Execucao da aplicacao

if __name__ == "__main__":
    construir_interface()

