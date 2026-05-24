"""
10_dashboard_cyberpunk.py
=========================
Dashboard interativo — tema Neon Cyberpunk
Roda com: python src/10_dashboard_cyberpunk.py
Acesse em: http://127.0.0.1:8050

Dependências:
    pip install dash plotly pandas scikit-learn
"""

import sqlite3
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────────
#  PALETA CYBERPUNK
# ─────────────────────────────────────────────
BG_PAGE   = "#0d0d1a"   # fundo geral
BG_CARD   = "#16162a"   # cartões / painéis
BG_CARD2  = "#1e1e38"   # cartão levemente mais claro
BORDER    = "#2a2a4a"   # borda sutil

ROXO      = "#c3a6ff"   # principal — roxo lavanda
ROSA      = "#ff79c6"   # destaque — rosa neon
CIANO     = "#8be9fd"   # informação — ciano
VERDE     = "#50fa7b"   # sucesso — verde neon
LARANJA   = "#ffb86c"   # aviso — âmbar
BRANCO    = "#f8f8f2"   # texto principal
CINZA     = "#6272a4"   # texto secundário

PALETA_GENEROS = [
    ROXO, ROSA, CIANO, VERDE, LARANJA,
    "#bd93f9", "#ff5555", "#f1fa8c", "#6be5fd", "#ff92df",
    "#a4ffb0", "#ffcc80", "#b0c4ff", "#ffadc0", "#7efff5",
]

FONT = "JetBrains Mono, Fira Code, monospace"

# ─────────────────────────────────────────────
#  ESTILOS REUTILIZÁVEIS
# ─────────────────────────────────────────────
CARD_STYLE = {
    "background": BG_CARD,
    "border": f"1px solid {BORDER}",
    "borderRadius": "10px",
    "padding": "20px",
    "marginBottom": "16px",
}

TITLE_STYLE = {
    "color": CINZA,
    "fontFamily": FONT,
    "fontSize": "10px",
    "fontWeight": "600",
    "letterSpacing": "2px",
    "textTransform": "uppercase",
    "marginBottom": "6px",
}

VALUE_STYLE = {
    "fontFamily": FONT,
    "fontSize": "26px",
    "fontWeight": "700",
    "lineHeight": "1",
}

ESTILO_DADO = {
    "background": "rgba(139, 233, 253, 0.04)",
    "borderLeft": f"4px solid {CIANO}",
    "padding": "10px 12px",
    "borderRadius": "4px",
    "marginBottom": "10px",
    "fontSize": "11.5px",
    "color": BRANCO,
    "lineHeight": "1.45"
}

ESTILO_INSIGHT = {
    "background": "rgba(80, 250, 123, 0.04)",
    "borderLeft": f"4px solid {VERDE}",
    "padding": "10px 12px",
    "borderRadius": "4px",
    "fontSize": "11.5px",
    "color": BRANCO,
    "lineHeight": "1.45"
}

BTN_BASE_STYLE = {
    "flex": "1",
    "padding": "16px 20px",
    "fontFamily": FONT,
    "fontSize": "12.5px",
    "fontWeight": "700",
    "backgroundColor": BG_CARD,
    "border": f"1px solid {BORDER}",
    "borderRadius": "8px",
    "cursor": "pointer",
    "transition": "all 0.3s ease",
}

dropdown_style = {
    "backgroundColor": BG_CARD2,
    "color":           BRANCO,
    "border":          f"1px solid {BORDER}",
    "borderRadius":    "6px",
    "fontFamily":      FONT,
    "fontSize":        "12px",
}

layout_base = dict(
    paper_bgcolor=BG_CARD,
    plot_bgcolor=BG_CARD,
    font=dict(family=FONT, color=BRANCO, size=10),
    margin=dict(l=15, r=15, t=40, b=15),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(size=9, color=CINZA),
    ),
    xaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        tickfont=dict(color=CINZA, size=9),
        title_font=dict(color=CINZA, size=9),
    ),
    yaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        tickfont=dict(color=CINZA, size=9),
        title_font=dict(color=CINZA, size=9),
    ),
)


# ─────────────────────────────────────────────
#  CARREGAMENTO DE DADOS (SQLite)
# ─────────────────────────────────────────────
def obter_caminho_banco():
    # Verifica primeiro se o banco está na raiz atual (se rodar da raiz)
    if os.path.exists("spotify_brasil.db"):
        return "spotify_brasil.db"
    # Se rodar de dentro da pasta src/
    caminho_pai = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "spotify_brasil.db"))
    if os.path.exists(caminho_pai):
        return caminho_pai
    return "spotify_brasil.db"


def carregar_dados_completos(db_path=None):
    if db_path is None:
        db_path = obter_caminho_banco()
    conn = sqlite3.connect(db_path)
    
    # 1. Dados gerais de todas as faixas
    q_faixas = """
        SELECT 
            f.nome AS musica, art.nome AS artista, f.genero, f.popularidade,
            a.danceability, a.energy, a.valence, a.tempo AS bpm, a.loudness, a.acousticness,
            CASE WHEN f.popularidade >= 70 THEN 'Mega Hit (>=70)' ELSE 'Comum (<70)' END as status_hit
        FROM faixas f
        JOIN atributos_audio a ON f.id = a.faixa_id
        JOIN artistas art      ON f.artista_id = art.id
    """
    df = pd.read_sql(q_faixas, conn)
    
    # 2. Dados agrupados por gênero para o Insight 1 (mínimo de 10 faixas)
    q_todos_generos = """
        SELECT f.genero, AVG(a.danceability) as dance, AVG(a.energy) as energia, COUNT(f.id) as total_faixas
        FROM faixas f JOIN atributos_audio a ON f.id = a.faixa_id
        WHERE f.genero IS NOT NULL
        GROUP BY f.genero HAVING COUNT(f.id) >= 10
    """
    df_todos_generos = pd.read_sql(q_todos_generos, conn)
    
    # 3. Top artistas de elite (mínimo de 5 faixas)
    q_artistas = """
        SELECT art.nome as artista, AVG(f.popularidade) as popularidade_media, COUNT(f.id) as total_faixas
        FROM faixas f
        JOIN artistas art ON f.artista_id = art.id
        GROUP BY art.id HAVING COUNT(f.id) >= 5
        ORDER BY popularidade_media DESC LIMIT 10
    """
    df_artistas = pd.read_sql(q_artistas, conn)
    
    # 4. Gêneros nacionais específicos
    q_br = """
        SELECT f.genero, AVG(a.danceability) as dance, AVG(a.energy) as energia, AVG(a.acousticness) as acustico
        FROM faixas f JOIN atributos_audio a ON f.id = a.faixa_id
        WHERE f.genero IN ('sertanejo', 'forro', 'samba', 'pagode', 'mpb', 'funk')
        GROUP BY f.genero
    """
    df_br = pd.read_sql(q_br, conn)
    
    conn.close()
    
    df["categoria"] = pd.cut(
        df["popularidade"],
        bins=[-1, 30, 69, 100],
        labels=["Baixa (0–30)", "Média (31–69)", "Sucesso (70–100)"],
    )
    df["is_hit"] = (df["popularidade"] >= 70).astype(int)
    
    return df, df_todos_generos, df_artistas, df_br


df, df_todos_generos, df_artistas, df_br = carregar_dados_completos()

GENEROS_LISTA = sorted(df["genero"].dropna().unique())
MAPA_NOMES_BR = {'sertanejo': 'Sertanejo', 'forro': 'Forró', 'samba': 'Samba', 'pagode': 'Pagode', 'mpb': 'MPB', 'funk': 'Funk'}

# ─────────────────────────────────────────────
#  FEATURE IMPORTANCE (Random Forest)
# ─────────────────────────────────────────────
FEATURES = ["danceability", "energy", "valence", "bpm", "loudness", "acousticness"]
FEATURES_LABEL = ["Dançabilidade", "Energia", "Alegria (Valência)", "Tempo (BPM)", "Volume (Loudness)", "Acústico (Acousticness)"]
FEAT_COLORS = [VERDE, CIANO, ROXO, ROSA, LARANJA, CINZA]

_df_ml = df.dropna(subset=FEATURES).copy()
_df_ml["is_hit"] = (_df_ml["popularidade"] >= 70).astype(int)
_X = _df_ml[FEATURES]
_y = _df_ml["is_hit"]
_modelo = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
_modelo.fit(_X, _y)
IMPORTANCIAS = pd.Series(_modelo.feature_importances_, index=FEATURES_LABEL).sort_values(ascending=True)


# ─────────────────────────────────────────────
#  KPI BUILDER
# ─────────────────────────────────────────────
def gerar_kpi_layout(df_kpi):
    total_faixas = len(df_kpi)
    total_generos = df_kpi["genero"].nunique()
    total_artistas = df_kpi["artista"].nunique()
    total_hits = len(df_kpi[df_kpi["popularidade"] >= 70])
    
    return html.Div(
        style={"display": "flex", "gap": "14px", "marginBottom": "20px", "flexWrap": "wrap"},
        children=[
            # Músicas Analisadas
            html.Div(
                style={**CARD_STYLE, "flex": "1", "minWidth": "160px", "marginBottom": "0"},
                children=[
                    html.P("MÚSICAS ANALISADAS", style=TITLE_STYLE),
                    html.P(f"{total_faixas:,}".replace(",", "."), style={**VALUE_STYLE, "color": ROXO}),
                ]
            ),
            # Artistas Identificados
            html.Div(
                style={**CARD_STYLE, "flex": "1", "minWidth": "160px", "marginBottom": "0"},
                children=[
                    html.P("ARTISTAS IDENTIFICADOS", style=TITLE_STYLE),
                    html.P(f"{total_artistas:,}".replace(",", "."), style={**VALUE_STYLE, "color": CIANO}),
                ]
            ),
            # Gêneros Musicais
            html.Div(
                style={**CARD_STYLE, "flex": "1", "minWidth": "160px", "marginBottom": "0"},
                children=[
                    html.P("GÊNEROS MUSICAIS", style=TITLE_STYLE),
                    html.P(str(total_generos), style={**VALUE_STYLE, "color": VERDE}),
                ]
            ),
            # Hits de Sucesso (Pop >= 70)
            html.Div(
                style={**CARD_STYLE, "flex": "1", "minWidth": "160px", "marginBottom": "0"},
                children=[
                    html.P("FAIXAS DE SUCESSO (POP >= 70)", style=TITLE_STYLE),
                    html.P(f"{total_hits:,}".replace(",", "."), style={**VALUE_STYLE, "color": ROSA}),
                ]
            ),
        ]
    )


# ─────────────────────────────────────────────
#  FUNÇÕES DE PLOTAGEM DE GRÁFICOS (MUNDIAL E NACIONAL)
# ─────────────────────────────────────────────
def plot_insight_1():
    fig = px.scatter(
        df_todos_generos, x="dance", y="energia", color="energia", size="total_faixas",
        hover_data=["genero", "total_faixas"],
        color_continuous_scale="Viridis",
        labels={'dance': 'Dançabilidade Média', 'energia': 'Energia Média', 'total_faixas': 'Faixas'},
        title="Dispersão de DNA Sonoro Médio por Gênero Musical"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
        "coloraxis": {"showscale": False}
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_2():
    df_animado = df.groupby('status_hit')[['danceability', 'energy']].mean().reset_index()
    df_melt = df_animado.melt(id_vars='status_hit', var_name='Atributo', value_name='Média')
    df_melt['Atributo'] = df_melt['Atributo'].map({'danceability': 'Dançabilidade', 'energy': 'Energia'})
    fig = px.bar(
        df_melt, x="Atributo", y="Média", color="status_hit", barmode="group",
        color_discrete_map={"Mega Hit (>=70)": VERDE, "Comum (<70)": CINZA},
        labels={'status_hit': 'Categoria', 'Média': 'Média'},
        title="Comparativo das Médias de Ritmo e Intensidade"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_3():
    fig = px.bar(
        pd.DataFrame({"importancia": IMPORTANCIAS.values, "atributo": IMPORTANCIAS.index}),
        x="importancia", y="atributo", orientation="h",
        color="importancia", color_continuous_scale="Greens",
        labels={'importancia': 'Importância', 'atributo': 'Atributo'},
        title="Importância dos Atributos Técnicos para o Algoritmo"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
        "coloraxis": {"showscale": False}
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_4():
    dados_amostra = df.sample(min(len(df), 5000), random_state=42)
    fig = px.box(
        dados_amostra, x="status_hit", y="loudness", color="status_hit",
        color_discrete_map={"Mega Hit (>=70)": VERDE, "Comum (<70)": CINZA},
        labels={'status_hit': 'Categoria', 'loudness': 'Volume (dB)'},
        title="Distribuição do Volume Físico das Faixas"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_5():
    df_acustico = df.groupby('status_hit')['acousticness'].mean().reset_index()
    fig = px.bar(
        df_acustico, x="status_hit", y="acousticness", color="status_hit",
        color_discrete_map={"Mega Hit (>=70)": VERDE, "Comum (<70)": CINZA},
        labels={'status_hit': 'Categoria', 'acousticness': 'Média Acústica'},
        title="Índice de Acústica Médio por Categoria"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_6():
    df_tristes = df[(df['popularidade'] >= 70) & (df['valence'] < 0.4)]
    df_tristes_count = df_tristes['genero'].value_counts().reset_index()
    df_tristes_count.columns = ['Gênero', 'Hits Tristes']
    fig = px.bar(
        df_tristes_count.head(10), x="Gênero", y="Hits Tristes",
        color="Hits Tristes", color_continuous_scale="Reds",
        labels={'Gênero': 'Gênero', 'Hits Tristes': 'Hits Tristes'},
        title="Top 10 Gêneros por Volume de Hits Melancólicos"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
        "coloraxis": {"showscale": False}
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_7():
    fig = px.bar(
        df_artistas, x="popularidade_media", y="artista", orientation="h",
        color="popularidade_media", color_continuous_scale="Purples",
        labels={'popularidade_media': 'Popularidade Média', 'artista': 'Artista'},
        title="Top 10 Artistas por Consistência Comercial no Dataset"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
        "coloraxis": {"showscale": False},
        "yaxis": {"categoryorder": "total ascending"}
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_br_1():
    df_br_melt = df_br.melt(id_vars='genero', var_name='Atributo', value_name='Média')
    df_br_melt['Atributo'] = df_br_melt['Atributo'].map({'dance': 'Dançabilidade', 'energia': 'Energia', 'acustico': 'Acústico'})
    df_br_melt['genero_formatado'] = df_br_melt['genero'].map(MAPA_NOMES_BR)
    fig = px.bar(
        df_br_melt, x="genero_formatado", y="Média", color="Atributo", barmode="group",
        color_discrete_sequence=["#50fa7b", "#8be9fd", "#ffb86c"],
        labels={'genero_formatado': 'Gênero', 'Média': 'Média'},
        title="Comparativo Sonoro: Gêneros Musicais Brasileiros"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_br_2():
    df_br_completo = df[df['genero'].isin(['sertanejo', 'forro', 'samba', 'pagode', 'mpb', 'funk'])].copy()
    df_br_completo['genero_formatado'] = df_br_completo['genero'].map(MAPA_NOMES_BR)
    fig = px.box(
        df_br_completo, x="genero_formatado", y="bpm", color="genero_formatado",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={'genero_formatado': 'Gênero', 'bpm': 'BPM (Velocidade)'},
        title="Distribuição de Velocidade (BPM) por Gênero Nacional"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
        "showlegend": False
    }
    fig.update_layout(**layout)
    return fig


def plot_insight_br_3():
    df_br_completo = df[df['genero'].isin(['sertanejo', 'forro', 'samba', 'pagode', 'mpb', 'funk'])].copy()
    df_br_completo['genero_formatado'] = df_br_completo['genero'].map(MAPA_NOMES_BR)
    df_pop_br = df_br_completo.groupby('genero_formatado')['popularidade'].mean().reset_index().sort_values(by='popularidade', ascending=False)
    fig = px.bar(
        df_pop_br, x="popularidade", y="genero_formatado", orientation="h",
        color="popularidade", color_continuous_scale="Greens",
        labels={'popularidade': 'Popularidade Média', 'genero_formatado': 'Gênero'},
        title="Popularidade Média dos Gêneros Nacionais no Dataset"
    )
    layout = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
        "coloraxis": {"showscale": False},
        "yaxis": {"categoryorder": "total ascending"}
    }
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────
#  ESTRUTURADORES DE LAYOUT DOS CARDS DE INSIGHTS
# ─────────────────────────────────────────────
def card_insight(titulo, figure_id, figure_or_graph, legenda_visual, o_que_mostra, insight):
    return html.Div(
        style=CARD_STYLE,
        children=[
            html.H3(titulo, style={"color": ROXO, "fontFamily": FONT, "fontSize": "14px", "fontWeight": "700", "marginBottom": "16px"}),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1.2fr 0.8fr", "gap": "20px", "alignItems": "center"},
                children=[
                    # Coluna do Gráfico
                    html.Div(
                        children=[
                            dcc.Graph(id=figure_id, figure=figure_or_graph, config={"displayModeBar": False})
                        ]
                    ),
                    # Coluna das Explicações
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "justifyContent": "center"},
                        children=[
                            html.P(
                                [html.Strong("Legenda e Visual: "), legenda_visual],
                                style={"fontSize": "11px", "color": CINZA, "marginBottom": "12px", "lineHeight": "1.3"}
                            ),
                            html.Div(
                                [html.Strong("O que o dado mostra:"), html.Br(), o_que_mostra],
                                style=ESTILO_DADO
                            ),
                            html.Div(
                                [html.Strong("Insight:"), html.Br(), insight],
                                style=ESTILO_INSIGHT
                            ),
                        ]
                    )
                ]
            )
        ]
    )


# ─────────────────────────────────────────────
#  LAYOUTS DAS ABAS
# ─────────────────────────────────────────────
def layout_relatorio_mundial():
    return html.Div(
        children=[
            html.H2("Histórias e Curiosidades do Mercado Musical Global", style={"color": BRANCO, "fontFamily": FONT, "fontSize": "16px", "fontWeight": "700", "marginBottom": "20px"}),
            
            card_insight(
                "1. O DNA Sonoro muda drasticamente por Gênero",
                "insight-graph-1", plot_insight_1(),
                "Eixo X: Dançabilidade · Eixo Y: Energia · Tamanho da bolha: Volume de faixas no banco · Cor: Escala de Energia.",
                "Gêneros essencialmente urbanos, como Hip-hop e Funk, posicionam-se no extremo direito (Dançabilidade média de 0.730 e 0.692). Gêneros instrumentais e de performance física, como Sertanejo e Rock, lideram em Energia (acima de 0.640).",
                "O comportamento sonoro depende diretamente do estilo. Enquanto os gêneros urbanos são estruturados em cima de batidas rítmicas feitas para dançar, estilos clássicos e orgânicos priorizam a intensidade instrumental e o vigor da performance."
            ),
            
            card_insight(
                "2. Mega Hits são estatisticamente mais animados",
                "insight-graph-2", plot_insight_2(),
                "Eixo X: Atributos · Eixo Y: Média (0 a 1) · Barra Verde: Mega Hits · Barra Cinza: Faixas comuns.",
                "Enquanto as músicas comuns têm uma média moderada de Dançabilidade (0.55), os Mega Hits saltam consideravelmente para uma média de 0.65 de Dançabilidade e 0.66 de Energia.",
                "Músicas que alcançam grande repercussão de público tendem a ser significativamente mais enérgicas e propensas à dança em comparação com a média geral, refletindo uma forte inclinação do público por faixas dinâmicas e estimulantes nas paradas."
            ),
            
            card_insight(
                "3. Dançabilidade é a métrica número 1 para prever o Sucesso",
                "insight-graph-3", plot_insight_3(),
                "Eixo X: Peso do atributo no modelo de IA · Eixo Y: Variável de áudio analisada · Cor: Intensidade da importância.",
                "O modelo de classificação inteligente (Random Forest) identificou que a Dançabilidade obteve disparadamente a maior importância na classificação (acima de 35% de peso), seguida de perto pela Energia.",
                "A cadência e a capacidade de movimentação (dançabilidade) são os fatores mais determinantes para definir a popularidade de uma faixa. O ritmo e a pulsação corporal se sobressaem sobre atributos como velocidade (BPM) ou intensidade sonora bruta no gosto do grande público."
            ),
            
            card_insight(
                "4. A Guerra do Volume (Loudness War) no Streaming",
                "insight-graph-4", plot_insight_4(),
                "Eixo X: Grupos · Eixo Y: Decibéis (valores negativos, quanto menor o volume negativo, mais alto é o som) · Caixa Verde: Limites do volume de Hits.",
                "Estatisticamente, os Hits tocam bem mais alto, concentrando sua média em -6.7 dB. Músicas comuns ou menos escutadas tocam de forma significativamente mais baixa, com média de -8.5 dB.",
                "As faixas mais escutadas possuem uma masterização estatisticamente mais alta do que a média geral, um reflexo prático do fenômeno da compressão dinâmica na música popular contemporânea para capturar a atenção imediata do ouvinte."
            ),
            
            card_insight(
                "5. O Mainstream praticamente baniu o som Acústico",
                "insight-graph-5", plot_insight_5(),
                "Eixo X: Grupos · Eixo Y: Escala acústica (0 representa digital; 1 representa acústico puro) · Barra Verde: Nível nos hits.",
                "Canções comuns mantêm um índice médio de som acústico de 0.33. Nos Mega Hits, esse índice despenca para 0.22, evidenciando uma sonoridade predominantemente artificial e sintetizada.",
                "Há uma clara preferência do grande público por arranjos eletrônicos e digitais. Instrumentos puramente acústicos têm menor representatividade entre as faixas mais ouvidas do que no catálogo geral, apontando para uma era de produções sintetizadas."
            ),
            
            card_insight(
                "6. O canal de sucesso específico para músicas Tristes",
                "insight-graph-6", plot_insight_6(),
                "Eixo X: Gêneros musicais · Eixo Y: Quantidade de faixas melancólicas que viraram hit · Cor: Escala de quantidade.",
                "Ao cruzar Valência baixa (músicas melancólicas ou sombrias, abaixo de 0.4) com alta popularidade, descobrimos que os gêneros que mais conseguem emplacar essa sonoridade são Alt-Rock e Indie-Pop.",
                "Embora músicas melancólicas (baixa valência) encontrem maior barreira na média geral, elas encontram um espaço fértil de grande recepção de público no Rock Alternativo e no Indie-Pop, onde há maior conexão do ouvinte com composições emotivas."
            ),
            
            card_insight(
                "7. Artistas de Elite e Consistência (O Efeito Bad Bunny)",
                "insight-graph-7", plot_insight_7(),
                "Eixo X: Média de popularidade · Eixo Y: Nomes dos artistas · Cor: Escala de popularidade do grupo.",
                "Artistas de alta consistência como Bad Bunny sustentam médias altíssimas de popularidade (85.3) ao longo de dezenas de músicas no dataset, distanciando-se de sucessos isolados de um hit só.",
                "A popularidade consistente de artistas consagrados sugere um efeito de arrasto: catálogos consolidados geram engajamento contínuo, fazendo com que novos lançamentos desses artistas já iniciem com grande vantagem de recomendação."
            ),
        ]
    )


def layout_relatorio_nacional():
    return html.Div(
        children=[
            html.H2("Relatório Especial: O DNA da Música Brasileira", style={"color": BRANCO, "fontFamily": FONT, "fontSize": "16px", "fontWeight": "700", "marginBottom": "20px"}),
            
            card_insight(
                "1. O Comportamento Sonoro dos Ritmos Brasileiros",
                "insight-br-graph-1", plot_insight_br_1(),
                "Eixo X: Gêneros nacionais · Eixo Y: Escala média (0 a 1) · Barra Verde: Dançabilidade · Barra Azul: Energia · Barra Laranja: Nível Acústico.",
                "O Funk lidera em Dançabilidade (0.692) e possui o menor índice acústico (0.324). O Forró atinge a maior Energia média (0.789). Pagode e Samba destacam-se como os mais orgânicos, com os maiores índices acústicos (0.562 e 0.485, respectivamente).",
                "A música brasileira exibe um comportamento sonoro multifacetado: enquanto o Funk e o Forró apresentam alto apelo físico com grande dançabilidade e intensidade digital, estilos como o Pagode e o Samba mantêm viva a rica tradição acústica nacional através de instrumentos orgânicos."
            ),
            
            card_insight(
                "2. A Velocidade e a Pulsação do Ritmo Nacional (BPM)",
                "insight-br-graph-2", plot_insight_br_2(),
                "Eixo X: Gêneros nacionais · Eixo Y: Batidas Por Minuto (BPM) · Caixas Coloridas: Variação e limites de velocidade das músicas.",
                "O Forró lidera em andamento físico rápido com uma média de velocidade próxima a 130 BPM, acompanhado de perto pelo Funk (média de 125 BPM). A MPB e o Samba apresentam andamentos mais cadenciados e controlados, com médias entre 110 e 115 BPM.",
                "Gêneros focados em comemorações e performance de dança ativa (como Forró e Funk) estruturam-se sobre andamentos rápidos e tempos marcados. Em contrapartida, estilos voltados à apreciação poética e dança clássica (Samba e MPB) priorizam ritmos confortáveis e andamentos mais relaxantes para o ouvinte."
            ),
            
            card_insight(
                "3. Tração Comercial e Aceitação dos Gêneros Brasileiros",
                "insight-br-graph-3", plot_insight_br_3(),
                "Eixo X: Escala de Popularidade Média (0 a 100) · Eixo Y: Gêneros nacionais · Cor: Intensidade da popularidade média.",
                "O Sertanejo e o Funk apresentam a maior média de popularidade no banco de dados (ambos acima de 50 de pontuação média). MPB e Samba mantêm médias estáveis mas inferiores (entre 35 e 40).",
                "O Sertanejo e o Funk possuem forte apelo de consumo em massa e rotação contínua nas plataformas de streaming atuais, concentrando os maiores volumes de engajamento diário de playlists comerciais. A MPB e o Samba, embora possuam valor cultural indiscutível, operam em nichos de consumo estáveis, mas com menor frequência de reprodução massiva nos charts."
            ),
        ]
    )


def layout_laboratorio_controles():
    return html.Div(
        style={**CARD_STYLE, "marginBottom": "20px"},
        children=[
            html.H3("Filtros do Laboratório Interativo", style={"color": ROXO, "fontFamily": FONT, "fontSize": "13px", "fontWeight": "700", "marginBottom": "16px"}),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "24px"},
                children=[
                    # Coluna de Gêneros
                    html.Div(
                        children=[
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "6px"},
                                children=[
                                    html.P("SELECIONAR GÊNEROS PARA ANÁLISE:", style={**TITLE_STYLE, "margin": 0}),
                                    html.Div(
                                        style={"display": "flex", "gap": "10px"},
                                        children=[
                                            html.Button("Selecionar Todos", id="lab-btn-select-all", n_clicks=0, style={
                                                "background": "none", "border": "none", "color": VERDE, "cursor": "pointer",
                                                "fontFamily": FONT, "fontSize": "10px", "textTransform": "uppercase", "letterSpacing": "1px",
                                                "padding": "0"
                                            }),
                                            html.Span("|", style={"color": CINZA, "fontSize": "10px"}),
                                            html.Button("Remover Seleção", id="lab-btn-deselect-all", n_clicks=0, style={
                                                "background": "none", "border": "none", "color": ROSA, "cursor": "pointer",
                                                "fontFamily": FONT, "fontSize": "10px", "textTransform": "uppercase", "letterSpacing": "1px",
                                                "padding": "0"
                                            })
                                        ]
                                    )
                                ]
                            ),
                            dcc.Dropdown(
                                id="lab-generos",
                                options=[{"label": g, "value": g} for g in GENEROS_LISTA],
                                value=['pop', 'rock', 'sertanejo', 'funk', 'electronic', 'latin'],
                                multi=True,
                                clearable=True,
                                style=dropdown_style,
                            ),
                        ]
                    ),
                    # Coluna de Popularidade
                    html.Div(
                        children=[
                            html.P("LIMITAR POPULARIDADE DAS MÚSICAS:", style=TITLE_STYLE),
                            dcc.RangeSlider(
                                id="lab-popularidade",
                                min=0,
                                max=100,
                                step=1,
                                value=[0, 100],
                                marks={0: {"label": "0", "style": {"color": CINZA}}, 20: "20", 40: "40", 60: "60", 80: "80", 100: {"label": "100", "style": {"color": CINZA}}},
                                tooltip={"always_visible": False, "placement": "bottom"},
                            ),
                        ]
                    ),
                ]
            )
        ]
    )


def layout_laboratorio_grid():
    return html.Div(
        id="lab-grid-container",
        children=[
            html.H3("Visualizações Editáveis", style={"color": ROXO, "fontFamily": FONT, "fontSize": "13px", "fontWeight": "700", "marginTop": "24px", "marginBottom": "16px"}),
            
            # Linha 1
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                children=[
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-1", config={"displayModeBar": False})]),
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-2", config={"displayModeBar": False})]),
                ]
            ),
            # Linha 2
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                children=[
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-3", config={"displayModeBar": False})]),
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-4", config={"displayModeBar": False})]),
                ]
            ),
            # Linha 3
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                children=[
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-5", config={"displayModeBar": False})]),
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-6", config={"displayModeBar": False})]),
                ]
            ),
            # Linha 4
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                children=[
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-7", config={"displayModeBar": False})]),
                    html.Div(style=CARD_STYLE, children=[dcc.Graph(id="lab-graph-8", config={"displayModeBar": False})]),
                ]
            ),
        ]
    )


def layout_laboratorio():
    return html.Div(
        children=[
            layout_laboratorio_controles(),
            html.Div(id="lab-kpi-container"),
            layout_laboratorio_grid(),
        ]
    )


# ─────────────────────────────────────────────
#  Navegação Ativa - Style Helper
# ─────────────────────────────────────────────
def obter_estilo_botao(aba_selecionada, aba_alvo):
    if aba_selecionada == aba_alvo:
        return {
            **BTN_BASE_STYLE,
            "border": f"1px solid {ROXO}",
            "color": ROXO,
            "boxShadow": f"0 0 10px rgba(195, 166, 255, 0.12)",
        }
    return {
        **BTN_BASE_STYLE,
        "color": CINZA,
    }


# ─────────────────────────────────────────────
#  APP DASH E LAYOUT PRINCIPAL
# ─────────────────────────────────────────────
app = dash.Dash(__name__, title="Spotify · Cyberpunk Dashboard", suppress_callback_exceptions=True)

app.layout = html.Div(
    style={"background": BG_PAGE, "minHeight": "100vh", "padding": "24px 32px", "fontFamily": FONT},
    children=[
        # Armazena a aba selecionada atual
        dcc.Store(id="aba-selecionada", data="relatorio_mundial"),

        # ── HEADER ──────────────────────────────────────
        html.Div(
            style={"marginBottom": "28px"},
            children=[
                html.Div(
                    style={"display": "flex", "alignItems": "center", "gap": "14px", "marginBottom": "6px"},
                    children=[
                        html.Div("◈", style={"color": ROXO, "fontSize": "28px"}),
                        html.H1(
                            "O ALGORITMO DO SUCESSO MUSICAL",
                            style={"color": BRANCO, "fontSize": "22px", "fontWeight": "700",
                                   "letterSpacing": "1px", "margin": "0"},
                        ),
                    ],
                ),
                html.P(
                    "Uma investigação profunda do DNA sonoro por trás dos maiores hits do Spotify através de dados e machine learning.  \n"
                    "Os dados utilizados nesta análise foram obtidos a partir do Spotify Tracks Dataset no Kaggle, abrangendo as características técnicas de áudio extraídas diretamente da API oficial da plataforma.",
                    style={"color": CINZA, "fontSize": "11px", "margin": "0", "lineHeight": "1.5"},
                ),
                html.Div(
                    style={"height": "1px", "background": f"linear-gradient(90deg, {ROXO}, {ROSA}, transparent)",
                           "marginTop": "16px"},
                ),
            ],
        ),

        # ── NAVEGAÇÃO ───────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px"},
            children=[
                html.Button("RELATÓRIO MUNDIAL", id="btn-mundial", n_clicks=0, style=BTN_BASE_STYLE),
                html.Button("RELATÓRIO NACIONAL", id="btn-nacional", n_clicks=0, style=BTN_BASE_STYLE),
                html.Button("LABORATÓRIO DE EXPLORAÇÃO", id="btn-laboratorio", n_clicks=0, style=BTN_BASE_STYLE),
            ]
        ),

        # ── CONTEÚDO ────────────────────────────────────
        html.Div(id="kpi-topo-container"),
        html.Div(id="conteudo-principal-aba"),

        # ── FOOTER ──────────────────────────────────────
        html.Div(
            style={"height": "1px", "background": f"linear-gradient(90deg, transparent, {ROXO}, {ROSA}, transparent)",
                   "marginTop": "32px", "marginBottom": "16px"},
        ),
        html.P(
            "◈ Spotify Cyberpunk Dashboard · dados: Kaggle spotify-tracks-dataset · banco: SQLite local",
            style={"color": CINZA, "fontSize": "10px", "textAlign": "center", "letterSpacing": "1px"},
        ),
    ],
)


# ─────────────────────────────────────────────
#  CALLBACKS DE ABAS E KPIs FIXOS
# ─────────────────────────────────────────────
@app.callback(
    Output("aba-selecionada", "data"),
    Input("btn-mundial", "n_clicks"),
    Input("btn-nacional", "n_clicks"),
    Input("btn-laboratorio", "n_clicks"),
    State("aba-selecionada", "data")
)
def alternar_aba_clique(c1, c2, c3, aba_atual):
    ctx = dash.callback_context
    if not ctx.triggered:
        return aba_atual
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "btn-mundial":
        return "relatorio_mundial"
    elif button_id == "btn-nacional":
        return "relatorio_nacional"
    elif button_id == "btn-laboratorio":
        return "laboratorio"
    return aba_atual


@app.callback(
    Output("btn-mundial", "style"),
    Output("btn-nacional", "style"),
    Output("btn-laboratorio", "style"),
    Output("kpi-topo-container", "children"),
    Output("conteudo-principal-aba", "children"),
    Input("aba-selecionada", "data")
)
def renderizar_conteudo_aba(aba):
    estilo_m = obter_estilo_botao(aba, "relatorio_mundial")
    estilo_n = obter_estilo_botao(aba, "relatorio_nacional")
    estilo_l = obter_estilo_botao(aba, "laboratorio")
    
    if aba == "relatorio_mundial":
        # KPIs globais
        kpi_layout = gerar_kpi_layout(df)
        conteudo = layout_relatorio_mundial()
    elif aba == "relatorio_nacional":
        # KPIs nacionais (Sertanejo, Funk, Samba, Pagode, Forró e MPB)
        df_nacional = df[df["genero"].isin(['sertanejo', 'forro', 'samba', 'pagode', 'mpb', 'funk'])]
        kpi_layout = gerar_kpi_layout(df_nacional)
        conteudo = layout_relatorio_nacional()
    else: # laboratorio
        # O laboratório renderiza seus próprios KPIs em outro callback dinamicamente
        kpi_layout = None
        conteudo = layout_laboratorio()
        
    return estilo_m, estilo_n, estilo_l, kpi_layout, conteudo


@app.callback(
    Output("lab-generos", "value"),
    Input("lab-btn-select-all", "n_clicks"),
    Input("lab-btn-deselect-all", "n_clicks"),
    State("lab-generos", "value"),
    prevent_initial_call=True
)
def gerenciar_selecao_dropdown(select_clicks, deselect_clicks, valores_atuais):
    ctx = dash.callback_context
    if not ctx.triggered:
        return valores_atuais
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "lab-btn-select-all":
        return GENEROS_LISTA
    elif triggered_id == "lab-btn-deselect-all":
        return []
    return valores_atuais


# ─────────────────────────────────────────────
#  CALLBACK REATIVO DO LABORATÓRIO (KPIs + 8 Gráficos)
# ─────────────────────────────────────────────
@app.callback(
    Output("lab-kpi-container", "children"),
    Output("lab-graph-1", "figure"),
    Output("lab-graph-2", "figure"),
    Output("lab-graph-3", "figure"),
    Output("lab-graph-4", "figure"),
    Output("lab-graph-5", "figure"),
    Output("lab-graph-6", "figure"),
    Output("lab-graph-7", "figure"),
    Output("lab-graph-8", "figure"),
    Input("lab-generos", "value"),
    Input("lab-popularidade", "value"),
)
def atualizar_laboratorio(generos_selecionados, pop_range):
    # Filtragem em tempo real
    df_filtrado = df[
        (df["genero"].isin(generos_selecionados)) &
        (df["popularidade"] >= pop_range[0]) &
        (df["popularidade"] <= pop_range[1])
    ]
    
    if df_filtrado.empty:
        empty_fig = go.Figure()
        layout_e = {
            **layout_base,
            "title": dict(text="SEM DADOS CORRESPONDENTES AOS FILTROS", font=dict(size=11, color=ROXO)),
            "height": 330
        }
        empty_fig.update_layout(**layout_e)
        kpis = html.Div(
            style={**CARD_STYLE, "padding": "15px", "textAlign": "center"},
            children=[html.P("Nenhuma música corresponde aos filtros selecionados. Tente expandir sua pesquisa!", style={"color": ROSA, "fontFamily": FONT, "margin": 0})]
        )
        return kpis, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # KPIs reativos
    kpis = gerar_kpi_layout(df_filtrado)
    
    # ── 1. Distribuição: Energia vs Dançabilidade ──
    # Amostragem para preservar a performance no scatter
    dados_scatter = df_filtrado
    if len(dados_scatter) > 2000:
        dados_scatter = dados_scatter.sample(2000, random_state=42)
        
    cat_map  = {"Baixa (0–30)": CINZA, "Média (31–69)": CIANO, "Sucesso (70–100)": ROSA}
    size_map = {"Baixa (0–30)": 4,     "Média (31–69)": 6,     "Sucesso (70–100)": 9}

    fig1 = go.Figure()
    for cat, cor in cat_map.items():
        sub = dados_scatter[dados_scatter["categoria"] == cat]
        if not sub.empty:
            fig1.add_trace(
                go.Scatter(
                    x=sub["danceability"],
                    y=sub["energy"],
                    mode="markers",
                    name=cat,
                    marker=dict(
                        color=cor,
                        size=size_map[cat],
                        opacity=0.6,
                        line=dict(width=0),
                    ),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Artista: %{customdata[1]}<br>"
                        "Dance: %{x:.2f}  Energia: %{y:.2f}<br>"
                        "Popularidade: %{customdata[2]}<extra></extra>"
                    ),
                    customdata=sub[["musica", "artista", "popularidade"]].values,
                )
            )
    layout1 = {
        **layout_base,
        "title": dict(text="1. Distribuição: Energia vs Dançabilidade", font=dict(size=11, color=ROXO)),
        "xaxis": dict(**layout_base["xaxis"], title="Dançabilidade", range=[-0.02, 1.05]),
        "yaxis": dict(**layout_base["yaxis"], title="Energia",       range=[-0.02, 1.05]),
        "height": 330,
        "legend": dict(**layout_base["legend"], title=dict(text="Popularidade", font=dict(color=CINZA, size=9))),
    }
    fig1.update_layout(**layout1)

    # ── 2. Comparativo Sonoro por Gênero Selecionado ──
    df_gen_avg = df_filtrado.groupby('genero')[['danceability', 'energy', 'acousticness']].mean().reset_index()
    df_gen_melt = df_gen_avg.melt(id_vars='genero', var_name='Atributo', value_name='Média')
    df_gen_melt['Atributo'] = df_gen_melt['Atributo'].map({'danceability': 'Dançabilidade', 'energy': 'Energia', 'acousticness': 'Acústico'})
    fig2 = px.bar(
        df_gen_melt, x="genero", y="Média", color="Atributo", barmode="group",
        color_discrete_sequence=[VERDE, CIANO, LARANJA],
        labels={'genero': 'Gênero', 'Média': 'Média'},
        title="2. Comparativo Sonoro por Gênero Selecionado"
    )
    layout2 = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig2.update_layout(**layout2)

    # ── 3. Ritmo e Intensidade: Hits vs Comuns ──
    df_anim_f = df_filtrado.groupby('status_hit')[['danceability', 'energy']].mean().reset_index()
    df_melt_f = df_anim_f.melt(id_vars='status_hit', var_name='Atributo', value_name='Média')
    df_melt_f['Atributo'] = df_melt_f['Atributo'].map({'danceability': 'Dançabilidade', 'energy': 'Energia'})
    fig3 = px.bar(
        df_melt_f, x="Atributo", y="Média", color="status_hit", barmode="group",
        color_discrete_map={"Mega Hit (>=70)": VERDE, "Comum (<70)": CINZA},
        labels={'status_hit': 'Categoria', 'Média': 'Média'},
        title="3. Ritmo e Intensidade: Hits vs Comuns"
    )
    layout3 = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig3.update_layout(**layout3)

    # ── 4. Distribuição do Volume das Faixas ──
    dados_box = df_filtrado.sample(min(len(df_filtrado), 2000), random_state=42)
    fig4 = px.box(
        dados_box, x="status_hit", y="loudness", color="status_hit",
        color_discrete_map={"Mega Hit (>=70)": VERDE, "Comum (<70)": CINZA},
        labels={'status_hit': 'Categoria', 'loudness': 'Volume (dB)'},
        title="4. Distribuição do Volume das Faixas"
    )
    layout4 = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig4.update_layout(**layout4)

    # ── 5. Índice de Acústica Médio: Hits vs Comuns ──
    df_acust_f = df_filtrado.groupby('status_hit')['acousticness'].mean().reset_index()
    fig5 = px.bar(
        df_acust_f, x="status_hit", y="acousticness", color="status_hit",
        color_discrete_map={"Mega Hit (>=70)": VERDE, "Comum (<70)": CINZA},
        labels={'status_hit': 'Categoria', 'acousticness': 'Índice Acústico'},
        title="5. Índice de Acústica Médio: Hits vs Comuns"
    )
    layout5 = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig5.update_layout(**layout5)

    # ── 6. Distribuição de Alegria (Valência) das Faixas ──
    fig6 = px.violin(
        dados_box, y="valence", color="status_hit",
        box=True, points=False,
        color_discrete_map={"Mega Hit (>=70)": VERDE, "Comum (<70)": CINZA},
        labels={'status_hit': 'Categoria', 'valence': 'Alegria (Valência)'},
        title="6. Distribuição de Alegria (Valência) das Faixas"
    )
    layout6 = {
        **layout_base,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "height": 330,
    }
    fig6.update_layout(**layout6)

    # ── 7. Gêneros por Volume de Hits Melancólicos ──
    df_trist_f = df_filtrado[(df_filtrado['popularidade'] >= 70) & (df_filtrado['valence'] < 0.4)]
    if df_trist_f.empty:
        fig7 = go.Figure()
        layout7 = {
            **layout_base,
            "title": dict(text="7. Gêneros por Volume de Hits Melancólicos (Sem dados)", font=dict(size=11, color=ROXO)),
            "height": 330
        }
        fig7.update_layout(**layout7)
    else:
        df_trist_count_f = df_trist_f['genero'].value_counts().reset_index()
        df_trist_count_f.columns = ['Gênero', 'Hits Tristes']
        fig7 = px.bar(
            df_trist_count_f.head(10), x="Gênero", y="Hits Tristes",
            color="Hits Tristes", color_continuous_scale="Reds",
            labels={'Gênero': 'Gênero', 'Hits Tristes': 'Hits Tristes'},
            title="7. Gêneros por Volume de Hits Melancólicos"
        )
        layout7 = {
            **layout_base,
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "height": 330,
            "coloraxis": {"showscale": False}
        }
        fig7.update_layout(**layout7)

    # ── 8. Top 10 Artistas por Popularidade Média ──
    df_art_f = df_filtrado.groupby('artista').agg(
        popularidade_media=('popularidade', 'mean'),
        total_faixas=('musica', 'count')
    ).reset_index()
    df_art_f = df_art_f[df_art_f['total_faixas'] >= 2]
    if df_art_f.empty:
        fig8 = go.Figure()
        layout8 = {
            **layout_base,
            "title": dict(text="8. Top 10 Artistas por Popularidade Média (Sem dados)", font=dict(size=11, color=ROXO)),
            "height": 330
        }
        fig8.update_layout(**layout8)
    else:
        df_art_top_f = df_art_f.sort_values(by='popularidade_media', ascending=False).head(10)
        fig8 = px.bar(
            df_art_top_f, x="popularidade_media", y="artista", orientation="h",
            color="popularidade_media", color_continuous_scale="Purples",
            labels={'popularidade_media': 'Popularidade Média', 'artista': 'Artista'},
            title="8. Top 10 Artistas por Popularidade Média"
        )
        layout8 = {
            **layout_base,
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "height": 330,
            "coloraxis": {"showscale": False},
            "yaxis": {"categoryorder": "total ascending"}
        }
        fig8.update_layout(**layout8)

    return kpis, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8


# ─────────────────────────────────────────────
#  INICIALIZAÇÃO DO SERVIDOR
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n* Spotify Cyberpunk Dashboard")
    print("  Acesse: http://127.0.0.1:8050\n")
    app.run(debug=False)
