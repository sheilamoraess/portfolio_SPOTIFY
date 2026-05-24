"""
10_dashboard_cyberpunk.py
=========================
Dashboard interativo — tema Neon Cyberpunk
Roda com: python 10_dashboard_cyberpunk.py
Acesse em:  http://127.0.0.1:8050

Dependências:
    pip install dash plotly pandas scikit-learn

O banco spotify_brasil.db deve estar na mesma pasta que este script
(gerado pelo 03_carregar_banco.py).
"""

import sqlite3
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import dash
from dash import dcc, html, Input, Output
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
    "fontSize": "28px",
    "fontWeight": "700",
    "lineHeight": "1",
}

layout_base = dict(
    paper_bgcolor=BG_CARD,
    plot_bgcolor=BG_CARD,
    font=dict(family=FONT, color=BRANCO, size=11),
    margin=dict(l=12, r=12, t=36, b=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(size=10, color=CINZA),
    ),
    xaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        tickfont=dict(color=CINZA, size=10),
        title_font=dict(color=CINZA, size=10),
    ),
    yaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        tickfont=dict(color=CINZA, size=10),
        title_font=dict(color=CINZA, size=10),
    ),
)


# ─────────────────────────────────────────────
#  CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────
GENEROS_FOCO = [
    "acoustic", "pop", "rock", "hip-hop", "jazz",
    "classical", "r-n-b", "forro", "sertanejo",
    "pagode", "funk", "electronic", "indie", "blues", "country",
]


def obter_caminho_banco():
    # Verifica primeiro se o banco está na raiz atual (se rodar da raiz)
    if os.path.exists("spotify_brasil.db"):
        return "spotify_brasil.db"
    # Se rodar de dentro da pasta src/
    caminho_pai = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "spotify_brasil.db"))
    if os.path.exists(caminho_pai):
        return caminho_pai
    return "spotify_brasil.db"


def carregar_dados(db_path=None):
    if db_path is None:
        db_path = obter_caminho_banco()
    conn = sqlite3.connect(db_path)
    query = """
        SELECT
            f.nome       AS musica,
            art.nome     AS artista,
            f.genero,
            f.popularidade,
            a.danceability,
            a.energy,
            a.valence,
            a.tempo      AS bpm,
            a.loudness,
            a.acousticness
        FROM faixas f
        JOIN atributos_audio a ON f.id = a.faixa_id
        JOIN artistas art      ON f.artista_id = art.id
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df["categoria"] = pd.cut(
        df["popularidade"],
        bins=[-1, 30, 69, 100],
        labels=["Baixa (0–30)", "Média (31–69)", "Sucesso (70–100)"],
    )
    df["is_hit"] = (df["popularidade"] >= 70).astype(int)
    return df


df = carregar_dados()


# ─────────────────────────────────────────────
#  FEATURE IMPORTANCE (treinado uma vez)
# ─────────────────────────────────────────────
FEATURES       = ["danceability", "energy", "valence", "bpm", "loudness", "acousticness"]
FEATURES_LABEL = ["Dançabilidade", "Energia", "Alegria", "BPM", "Volume", "Acústica"]
FEAT_COLORS    = [ROXO, CIANO, VERDE, ROSA, LARANJA, CINZA]

_df_ml = df.dropna(subset=FEATURES + ["is_hit"]).copy()
_X = _df_ml[FEATURES]
_y = _df_ml["is_hit"]
_Xtr, _Xte, _ytr, _yte = train_test_split(_X, _y, test_size=0.2, random_state=42)
_modelo = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
_modelo.fit(_Xtr, _ytr)
IMPORTANCIAS = pd.Series(_modelo.feature_importances_, index=FEATURES_LABEL).sort_values()


# ─────────────────────────────────────────────
#  KPIs
# ─────────────────────────────────────────────
TOTAL_FAIXAS  = f"{len(df):,}".replace(",", ".")
TOTAL_GENEROS = str(df["genero"].nunique())
TAXA_HITS     = f"{df['is_hit'].mean() * 100:.1f}%"
BPM_MEDIO     = f"{df['bpm'].mean():.0f}"


def kpi_card(titulo, valor, cor):
    return html.Div(
        [
            html.P(titulo, style=TITLE_STYLE),
            html.P(valor, style={**VALUE_STYLE, "color": cor}),
        ],
        style={**CARD_STYLE, "flex": "1", "minWidth": "120px"},
    )


# ─────────────────────────────────────────────
#  FUNÇÕES DE GRÁFICO
# ─────────────────────────────────────────────

def fig_dna(atributo="danceability", label="Dançabilidade"):
    medias = (
        df.groupby("genero")[atributo]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig = go.Figure(
        go.Bar(
            x=medias[atributo],
            y=medias["genero"],
            orientation="h",
            marker=dict(
                color=medias[atributo],
                colorscale=[[0, BG_CARD2], [0.4, CINZA], [0.75, ROXO], [1, ROSA]],
                showscale=False,
            ),
            text=medias[atributo].round(2),
            textposition="outside",
            textfont=dict(size=9, color=CINZA),
            hovertemplate="<b>%{y}</b><br>" + label + ": %{x:.3f}<extra></extra>",
        )
    )
    layout = {
        **layout_base,
        "title": dict(text=f"DNA SONORO · {label.upper()}", font=dict(size=11, color=ROXO)),
        "xaxis": dict(**layout_base["xaxis"], range=[0, 1.05]),
        "height": 400,
    }
    fig.update_layout(**layout)
    return fig


def fig_scatter(genero_filtro=None):
    dados = df if genero_filtro is None else df[df["genero"] == genero_filtro]
    # Amostragem para preservar a performance do navegador em bases grandes
    if len(dados) > 2000:
        dados = dados.sample(2000, random_state=42)

    cat_map  = {"Baixa (0–30)": CINZA, "Média (31–69)": CIANO, "Sucesso (70–100)": ROSA}
    size_map = {"Baixa (0–30)": 4,     "Média (31–69)": 6,     "Sucesso (70–100)": 9}

    fig = go.Figure()
    for cat, cor in cat_map.items():
        sub = dados[dados["categoria"] == cat]
        fig.add_trace(
            go.Scatter(
                x=sub["danceability"],
                y=sub["energy"],
                mode="markers",
                name=cat,
                marker=dict(
                    color=cor,
                    size=size_map[cat],
                    opacity=0.55,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Artista: %{customdata[1]}<br>"
                    "Dance: %{x:.2f}  Energia: %{y:.2f}<br>"
                    "Popularidade: %{customdata[2]}<extra></extra>"
                ),
                customdata=sub[["musica", "artista", "popularidade"]].values if not sub.empty else np.empty((0, 3)),
            )
        )

    layout = {
        **layout_base,
        "title": dict(text="ENERGIA × DANÇABILIDADE", font=dict(size=11, color=ROXO)),
        "xaxis": dict(**layout_base["xaxis"], title="Dançabilidade", range=[-0.02, 1.05]),
        "yaxis": dict(**layout_base["yaxis"], title="Energia",       range=[-0.02, 1.05]),
        "height": 360,
        "legend": dict(**layout_base["legend"], title=dict(text="Popularidade", font=dict(color=CINZA, size=9))),
    }
    fig.update_layout(**layout)
    return fig


def fig_importancia():
    fig = go.Figure(
        go.Bar(
            x=IMPORTANCIAS.values,
            y=IMPORTANCIAS.index,
            orientation="h",
            marker=dict(color=FEAT_COLORS[:len(IMPORTANCIAS)]),
            text=[f"{v:.1%}" for v in IMPORTANCIAS.values],
            textposition="outside",
            textfont=dict(size=9, color=CINZA),
            hovertemplate="<b>%{y}</b><br>Importância: %{x:.3f}<extra></extra>",
        )
    )
    layout = {
        **layout_base,
        "title": dict(text="O QUE DEFINE UM HIT? · RANDOM FOREST", font=dict(size=11, color=ROXO)),
        "xaxis": dict(**layout_base["xaxis"], title="Importância relativa", tickformat=".0%"),
        "height": 310,
    }
    fig.update_layout(**layout)
    return fig


def fig_popularidade_genero():
    top10 = df.groupby("genero").size().sort_values(ascending=False).head(10).index
    dados = df[df["genero"].isin(top10)].copy()

    avg_pop  = dados.groupby("genero")["popularidade"].mean().sort_values(ascending=False)
    taxa_hit = (dados.groupby("genero")["is_hit"].mean() * 100).reindex(avg_pop.index)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Popularidade média",
            x=avg_pop.index,
            y=avg_pop.values,
            marker=dict(
                color=avg_pop.values,
                colorscale=[[0, BG_CARD2], [0.5, ROXO], [1, ROSA]],
                showscale=False,
            ),
            yaxis="y",
            hovertemplate="<b>%{x}</b><br>Pop. média: %{y:.1f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Taxa de hits (%)",
            x=taxa_hit.index,
            y=taxa_hit.values,
            mode="lines+markers",
            line=dict(color=CIANO, width=2, dash="dot"),
            marker=dict(color=CIANO, size=7, symbol="diamond"),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Taxa de hits: %{y:.1f}%<extra></extra>",
        )
    )
    layout = {
        **layout_base,
        "title": dict(text="POPULARIDADE & TAXA DE HITS POR GÊNERO", font=dict(size=11, color=ROXO)),
        "xaxis": dict(**layout_base["xaxis"], tickangle=-30),
        "yaxis": dict(**layout_base["yaxis"], title="Popularidade média"),
        "yaxis2": dict(
            overlaying="y",
            side="right",
            title="Taxa de hits (%)",
            gridcolor=BORDER,
            tickfont=dict(color=CIANO, size=10),
            title_font=dict(color=CIANO, size=10),
        ),
        "legend": dict(**layout_base["legend"], x=0.01, y=0.99),
        "height": 360,
        "barmode": "group",
    }
    fig.update_layout(**layout)
    return fig


def fig_histograma():
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=df["popularidade"],
            nbinsx=40,
            name="Faixas",
            marker=dict(
                color=df["popularidade"],
                colorscale=[[0, BG_CARD2], [0.55, ROXO], [0.9, ROSA], [1, "#ff5555"]],
                showscale=False,
                line=dict(width=0),
            ),
            opacity=0.85,
            hovertemplate="Popularidade ~%{x}<br>Faixas: %{y}<extra></extra>",
        )
    )
    fig.add_vline(
        x=70,
        line=dict(color=CIANO, width=1.5, dash="dash"),
        annotation=dict(
            text="limiar de hit (70)",
            font=dict(color=CIANO, size=10, family=FONT),
            bgcolor=BG_CARD,
            borderpad=4,
        ),
    )
    fig.add_vline(
        x=df["popularidade"].mean(),
        line=dict(color=VERDE, width=1, dash="dot"),
        annotation=dict(
            text=f"média ({df['popularidade'].mean():.0f})",
            font=dict(color=VERDE, size=10, family=FONT),
            bgcolor=BG_CARD,
            borderpad=4,
            yshift=-24,
        ),
    )
    layout = {
        **layout_base,
        "title": dict(text="DISTRIBUIÇÃO DE POPULARIDADE", font=dict(size=11, color=ROXO)),
        "xaxis": dict(**layout_base["xaxis"], title="Popularidade (0–100)"),
        "yaxis": dict(**layout_base["yaxis"], title="Nº de faixas"),
        "height": 310,
        "showlegend": False,
    }
    fig.update_layout(**layout)
    return fig


def fig_radar_genero(genero="pop"):
    attrs  = ["danceability", "energy", "valence", "acousticness"]
    labels = ["Dançabilidade", "Energia", "Alegria", "Acústica"]

    sub    = df[df["genero"] == genero][attrs].mean()
    global_= df[attrs].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(sub.values) + [sub.values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor=f"rgba(195,166,255,0.15)",
        line=dict(color=ROXO, width=2),
        name=genero,
    ))
    fig.add_trace(go.Scatterpolar(
        r=list(global_.values) + [global_.values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor=f"rgba(139,233,253,0.08)",
        line=dict(color=CIANO, width=1.5, dash="dot"),
        name="Média geral",
    ))
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(family=FONT, color=BRANCO, size=10),
        polar=dict(
            bgcolor=BG_CARD2,
            radialaxis=dict(
                visible=True, range=[0, 1],
                gridcolor=BORDER, tickcolor=CINZA,
                tickfont=dict(size=8, color=CINZA),
                linecolor=BORDER,
            ),
            angularaxis=dict(
                gridcolor=BORDER,
                tickfont=dict(size=10, color=BRANCO),
                linecolor=BORDER,
            ),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, color=CINZA),
        ),
        title=dict(text=f"RADAR · {genero.upper()}", font=dict(size=11, color=ROXO)),
        margin=dict(l=40, r=40, t=50, b=20),
        height=310,
    )
    return fig


# ─────────────────────────────────────────────
#  APP DASH
# ─────────────────────────────────────────────
app = dash.Dash(__name__, title="Spotify · Cyberpunk Dashboard")

GENEROS_LISTA = sorted(df["genero"].dropna().unique())
ATRIBUTOS = {
    "danceability": "Dançabilidade",
    "energy":       "Energia",
    "valence":      "Alegria",
    "bpm":          "BPM",
    "acousticness": "Acústica",
}

# ── Estilo do dropdown ──
dropdown_style = {
    "backgroundColor": BG_CARD2,
    "color":           BRANCO,
    "border":          f"1px solid {BORDER}",
    "borderRadius":    "6px",
    "fontFamily":      FONT,
    "fontSize":        "12px",
}

app.layout = html.Div(
    style={"background": BG_PAGE, "minHeight": "100vh", "padding": "24px 32px", "fontFamily": FONT},
    children=[

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
                        html.Span(
                            "CYBERPUNK EDITION",
                            style={"color": ROSA, "fontSize": "10px", "fontWeight": "600",
                                   "letterSpacing": "3px", "border": f"1px solid {ROSA}",
                                   "padding": "3px 10px", "borderRadius": "4px"},
                        ),
                    ],
                ),
                html.P(
                    "Análise interativa de 114.000 faixas do Spotify · DNA sonoro · gêneros · o que faz um hit",
                    style={"color": CINZA, "fontSize": "12px", "margin": "0"},
                ),
                html.Div(
                    style={"height": "1px", "background": f"linear-gradient(90deg, {ROXO}, {ROSA}, transparent)",
                           "marginTop": "16px"},
                ),
            ],
        ),

        # ── KPIs ────────────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "14px", "marginBottom": "20px", "flexWrap": "wrap"},
            children=[
                kpi_card("TOTAL DE FAIXAS",  TOTAL_FAIXAS,  ROXO),
                kpi_card("GÊNEROS ÚNICOS",   TOTAL_GENEROS, CIANO),
                kpi_card("TAXA DE HITS",     TAXA_HITS,     ROSA),
                kpi_card("BPM MÉDIO",        BPM_MEDIO,     VERDE),
                html.Div(
                    style={**CARD_STYLE, "flex": "2", "minWidth": "260px"},
                    children=[
                        html.P("FILTRO GLOBAL", style=TITLE_STYLE),
                        dcc.Dropdown(
                            id="filtro-genero",
                            options=[{"label": "Todos os gêneros", "value": "TODOS"}]
                                    + [{"label": g, "value": g} for g in GENEROS_LISTA],
                            value="TODOS",
                            clearable=False,
                            style=dropdown_style,
                        ),
                    ],
                ),
            ],
        ),

        # ── LINHA 1: DNA + SCATTER ───────────────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1.1fr", "gap": "16px", "marginBottom": "16px"},
            children=[

                # DNA com selector de atributo
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between",
                                   "alignItems": "center", "marginBottom": "12px"},
                            children=[
                                html.P("ATRIBUTO", style=TITLE_STYLE),
                                dcc.Dropdown(
                                    id="dna-atributo",
                                    options=[{"label": v, "value": k} for k, v in ATRIBUTOS.items()],
                                    value="danceability",
                                    clearable=False,
                                    style={**dropdown_style, "width": "160px"},
                                ),
                            ],
                        ),
                        dcc.Graph(id="graph-dna", config={"displayModeBar": False}),
                    ],
                ),

                # Scatter
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        dcc.Graph(id="graph-scatter", config={"displayModeBar": False}),
                    ],
                ),
            ],
        ),

        # ── LINHA 2: POPULARIDADE POR GÊNERO (full width) ─
        html.Div(
            style={**CARD_STYLE, "marginBottom": "16px"},
            children=[
                dcc.Graph(id="graph-pop-genero", figure=fig_popularidade_genero(),
                          config={"displayModeBar": False}),
            ],
        ),

        # ── LINHA 3: HISTOGRAMA + IMPORTÂNCIA ───────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
            children=[
                html.Div(style=CARD_STYLE, children=[
                    dcc.Graph(id="graph-hist", figure=fig_histograma(),
                              config={"displayModeBar": False}),
                ]),
                html.Div(style=CARD_STYLE, children=[
                    dcc.Graph(id="graph-imp", figure=fig_importancia(),
                              config={"displayModeBar": False}),
                ]),
            ],
        ),

        # ── LINHA 4: RADAR POR GÊNERO ───────────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 2fr", "gap": "16px", "marginBottom": "16px"},
            children=[
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.P("PERFIL SONORO — RADAR", style=TITLE_STYLE),
                        html.P(
                            "Selecione um gênero para comparar seu DNA sonoro com a média geral.",
                            style={"color": CINZA, "fontSize": "11px", "marginBottom": "12px"},
                        ),
                        dcc.Dropdown(
                            id="radar-genero",
                            options=[{"label": g, "value": g} for g in GENEROS_LISTA],
                            value="sertanejo",
                            clearable=False,
                            style=dropdown_style,
                        ),
                        html.Div(id="radar-stats", style={"marginTop": "16px"}),
                    ],
                ),
                html.Div(style=CARD_STYLE, children=[
                    dcc.Graph(id="graph-radar", config={"displayModeBar": False}),
                ]),
            ],
        ),

        # ── FOOTER ──────────────────────────────────────
        html.Div(
            style={"height": "1px", "background": f"linear-gradient(90deg, transparent, {ROXO}, {ROSA}, transparent)",
                   "marginBottom": "16px"},
        ),
        html.P(
            "◈ Spotify Cyberpunk Dashboard · dados: HuggingFace spotify-tracks-dataset · banco: SQLite local",
            style={"color": CINZA, "fontSize": "10px", "textAlign": "center", "letterSpacing": "1px"},
        ),
    ],
)


# ─────────────────────────────────────────────
#  CALLBACKS
# ─────────────────────────────────────────────

@app.callback(
    Output("graph-dna", "figure"),
    Input("dna-atributo", "value"),
    Input("filtro-genero", "value"),
)
def atualizar_dna(atributo, genero):
    dados = df if genero == "TODOS" else df[df["genero"] == genero]
    label = ATRIBUTOS.get(atributo, atributo)
    medias = dados.groupby("genero")[atributo].mean().sort_values(ascending=True).reset_index()
    fig = go.Figure(
        go.Bar(
            x=medias[atributo],
            y=medias["genero"],
            orientation="h",
            marker=dict(
                color=medias[atributo],
                colorscale=[[0, BG_CARD2], [0.4, CINZA], [0.75, ROXO], [1, ROSA]],
                showscale=False,
            ),
            text=medias[atributo].round(2),
            textposition="outside",
            textfont=dict(size=9, color=CINZA),
            hovertemplate=f"<b>%{{y}}</b><br>{label}: %{{x:.3f}}<extra></extra>",
        )
    )
    layout = {
        **layout_base,
        "title": dict(text=f"DNA SONORO · {label.upper()}", font=dict(size=11, color=ROXO)),
        "xaxis": dict(**layout_base["xaxis"], range=[0, 1.15] if atributo != "bpm" else None),
        "height": 400,
    }
    fig.update_layout(**layout)
    return fig


@app.callback(
    Output("graph-scatter", "figure"),
    Input("filtro-genero", "value"),
)
def atualizar_scatter(genero):
    g = None if genero == "TODOS" else genero
    return fig_scatter(g)


@app.callback(
    Output("graph-radar", "figure"),
    Output("radar-stats", "children"),
    Input("radar-genero", "value"),
)
def atualizar_radar(genero):
    fig = fig_radar_genero(genero)

    sub   = df[df["genero"] == genero]
    total = len(sub)
    hits  = sub["is_hit"].sum()
    taxa  = hits / total * 100 if total else 0
    pop   = sub["popularidade"].mean()

    stats = html.Div(
        style={"display": "flex", "flexDirection": "column", "gap": "8px"},
        children=[
            _stat_mini("Faixas",        f"{total:,}".replace(",", "."), CINZA),
            _stat_mini("Hits",          str(hits),                      ROSA),
            _stat_mini("Taxa de hit",   f"{taxa:.1f}%",                 VERDE),
            _stat_mini("Pop. média",    f"{pop:.0f}",                   ROXO),
        ],
    )
    return fig, stats


def _stat_mini(label, valor, cor):
    return html.Div(
        style={"display": "flex", "justifyContent": "space-between",
               "borderBottom": f"1px solid {BORDER}", "paddingBottom": "4px"},
        children=[
            html.Span(label, style={"color": CINZA,  "fontSize": "11px"}),
            html.Span(valor, style={"color": cor,     "fontSize": "11px", "fontWeight": "600"}),
        ],
    )


# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n* Spotify Cyberpunk Dashboard")
    print("  Acesse: http://127.0.0.1:8050\n")
    app.run(debug=False)
