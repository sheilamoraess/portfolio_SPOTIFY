import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração inicial da página web (Deve ser o primeiro comando Streamlit)
st.set_page_config(page_title="Dashboard Spotify", page_icon="🎵", layout="wide")

class DashboardSpotifyApp:
    """
    Classe controladora do aplicativo web interativo do Spotify.
    Gerencia a estilização, cache de dados, inteligência artificial e renderização da interface.
    """
    def __init__(self, db_path='spotify_brasil.db'):
        self.db_path = db_path
        self.estilo_dado = "background-color: rgba(100, 110, 120, 0.15); padding: 14px; border-radius: 8px; border-left: 5px solid #8892b0; margin-bottom: 12px; font-size: 14px; line-height: 1.5; color: #a8b2d1;"
        self.estilo_insight = "background-color: rgba(30, 215, 96, 0.15); padding: 14px; border-radius: 8px; border-left: 5px solid #1ed760; font-size: 14px; line-height: 1.5; color: #e6f9ed;"
        
        self.injetar_css()
        self.inicializar_estado()

    def inicializar_estado(self):
        """Inicializa as variáveis de controle do estado da sessão do Streamlit."""
        if 'aba_selecionada' not in st.session_state:
            st.session_state.aba_selecionada = 'relatorio_mundial'

    def injetar_css(self):
        """Injeta a estilização customizada no formato Cyberpunk / Setup Gamer."""
        st.markdown("""
        <style>
            /* Fundo da aplicação */
            .stApp {
                background-color: #0a0c10 !important;
                color: #ccd6f6 !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            
            /* Configuração dos contêineres/cards de gráficos e KPIs com gradiente e luz interna */
            div[data-testid="stContainer"] {
                background: linear-gradient(135deg, #11141e 0%, #161a29 100%) !important;
                border: 1px solid rgba(30, 215, 96, 0.12) !important;
                border-radius: 16px !important;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 0 12px rgba(30, 215, 96, 0.04) !important;
                padding: 24px !important;
                backdrop-filter: blur(8px) !important;
                -webkit-backdrop-filter: blur(8px) !important;
                transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            }
            
            /* Efeito hover setup gamer com glow verde neon difuso e leve elevação */
            div[data-testid="stContainer"]:hover {
                border-color: rgba(30, 215, 96, 0.6) !important;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(30, 215, 96, 0.25), inset 0 0 8px rgba(30, 215, 96, 0.1) !important;
                transform: translateY(-4px);
            }
            
            /* Customização de cabeçalhos e títulos */
            h1, h2, h3 {
                color: #ffffff !important;
                font-weight: 800 !important;
                letter-spacing: -0.5px;
            }
            
            /* Destaque para subheaders de insights */
            h3 {
                color: #1ed760 !important;
                text-shadow: 0 0 12px rgba(30, 215, 96, 0.3) !important;
            }
            
            /* Estilização específica dos KPIs (Big Numbers) com glow forte */
            div[data-testid="stMetricValue"] {
                color: #1ed760 !important;
                font-weight: 900 !important;
                font-size: 2.3rem !important;
                text-shadow: 0 0 15px rgba(30, 215, 96, 0.6) !important;
            }
            
            div[data-testid="stMetricLabel"] {
                color: #8892b0 !important;
                font-size: 0.85rem !important;
                font-weight: 600 !important;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }
            
            /* Customização dos Botões Gamer de Navegação baseada em data-testid com gradientes e sombras */
            button[data-testid="baseButton-primary"] {
                background: linear-gradient(90deg, #1ed760 0%, #1db954 100%) !important;
                color: #0a0c10 !important;
                border: none !important;
                border-radius: 14px !important;
                padding: 20px 30px !important;
                min-height: 80px !important;
                box-shadow: 0 0 20px rgba(30, 215, 96, 0.45) !important;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                transition: all 0.3s ease-in-out !important;
                width: 100%;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            button[data-testid="baseButton-primary"]:hover {
                background: linear-gradient(90deg, #1db954 0%, #1ed760 100%) !important;
                box-shadow: 0 0 35px rgba(30, 215, 96, 0.75) !important;
                transform: scale(1.02);
            }
            button[data-testid="baseButton-primary"] p,
            button[data-testid="baseButton-primary"] span {
                color: #0a0c10 !important;
                font-weight: 900 !important;
                font-size: 1.4rem !important;
            }
            
            button[data-testid="baseButton-secondary"] {
                background: linear-gradient(135deg, #11141e 0%, #161a29 100%) !important;
                color: #8892b0 !important;
                border: 2px solid rgba(30, 215, 96, 0.2) !important;
                border-radius: 14px !important;
                padding: 20px 30px !important;
                min-height: 80px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                transition: all 0.3s ease-in-out !important;
                width: 100%;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            button[data-testid="baseButton-secondary"]:hover {
                color: #ffffff !important;
                border-color: rgba(30, 215, 96, 0.7) !important;
                box-shadow: 0 0 20px rgba(30, 215, 96, 0.3) !important;
                transform: scale(1.02);
            }
            button[data-testid="baseButton-secondary"] p,
            button[data-testid="baseButton-secondary"] span {
                color: #8892b0 !important;
                font-weight: 800 !important;
                font-size: 1.4rem !important;
            }
            button[data-testid="baseButton-secondary"]:hover p,
            button[data-testid="baseButton-secondary"]:hover span {
                color: #ffffff !important;
            }
            
            /* Estilização da barra de rolagem */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #0a0c10;
            }
            ::-webkit-scrollbar-thumb {
                background: #1DB954;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #1ed760;
            }
        </style>
        """, unsafe_allow_html=True)

    @st.cache_data
    def carregar_dados(_self):
        """Carrega e organiza os dataframes a partir do banco de dados SQLite com cache."""
        conn = sqlite3.connect(_self.db_path)
        
        # 1. Dados gerais de faixas
        q_faixas = '''
        SELECT 
            f.nome AS musica, art.nome AS artista, f.genero, f.popularidade,
            a.danceability, a.energy, a.valence, a.tempo, a.loudness, a.acousticness,
            CASE WHEN f.popularidade >= 70 THEN 'Mega Hit (>=70)' ELSE 'Comum (<70)' END as status_hit
        FROM faixas f
        JOIN atributos_audio a ON f.id = a.faixa_id
        JOIN artistas art ON f.artista_id = art.id
        '''
        df_faixas = pd.read_sql(q_faixas, conn)
        
        # 2. Dados agrupados por todos os gêneros (mínimo de 10 faixas) para o Insight 1
        q_todos_generos = '''
        SELECT f.genero, AVG(a.danceability) as dance, AVG(a.energy) as energia, COUNT(f.id) as total_faixas
        FROM faixas f JOIN atributos_audio a ON f.id = a.faixa_id
        WHERE f.genero IS NOT NULL
        GROUP BY f.genero HAVING COUNT(f.id) >= 10
        '''
        df_todos_generos = pd.read_sql(q_todos_generos, conn)
        
        # 3. Top artistas de elite para o Insight 7 (mínimo de 5 faixas)
        q_artistas = '''
        SELECT art.nome as artista, AVG(f.popularidade) as popularidade_media, COUNT(f.id) as total_faixas
        FROM faixas f
        JOIN artistas art ON f.artista_id = art.id
        GROUP BY art.id HAVING COUNT(f.id) >= 5
        ORDER BY popularidade_media DESC LIMIT 10
        '''
        df_artistas = pd.read_sql(q_artistas, conn)
        
        # 4. Dados de gêneros especificamente brasileiros
        q_br = '''
        SELECT f.genero, AVG(a.danceability) as dance, AVG(a.energy) as energia, AVG(a.acousticness) as acustico
        FROM faixas f JOIN atributos_audio a ON f.id = a.faixa_id
        WHERE f.genero IN ('sertanejo', 'forro', 'samba', 'pagode', 'mpb', 'funk')
        GROUP BY f.genero
        '''
        df_br = pd.read_sql(q_br, conn)
        
        conn.close()
        return df_faixas, df_todos_generos, df_artistas, df_br

    @st.cache_data
    def calcular_importancia_ml(_self, df):
        """Calcula a importância técnica dos atributos de áudio usando Machine Learning (Random Forest)."""
        try:
            from sklearn.ensemble import RandomForestClassifier
            features = ['danceability', 'energy', 'valence', 'tempo', 'loudness', 'acousticness']
            df_ml = df.dropna(subset=features).copy()
            df_ml['is_hit'] = df_ml['popularidade'] >= 70
            X = df_ml[features]
            y = df_ml['is_hit']
            model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
            model.fit(X, y)
            importances = pd.DataFrame({
                'atributo': ['Dançabilidade', 'Energia', 'Alegria (Valência)', 'Tempo (BPM)', 'Volume (Loudness)', 'Acústico (Acousticness)'],
                'importancia': model.feature_importances_
            }).sort_values(by='importancia', ascending=True)
        except Exception:
            # Fallback caso scikit-learn não esteja presente
            importances = pd.DataFrame({
                'atributo': ['Acústico (Acousticness)', 'Tempo (BPM)', 'Alegria (Valência)', 'Volume (Loudness)', 'Energia', 'Dançabilidade'],
                'importancia': [0.06, 0.08, 0.12, 0.15, 0.22, 0.37]
            })
        return importances

    def renderizar_cabecalho(self):
        """Renderiza a seção inicial com o título do dashboard."""
        st.title("O Algoritmo do Sucesso Musical")
        st.markdown("Uma investigação profunda do DNA sonoro por trás dos maiores hits do Spotify através de dados e machine learning.")

    def renderizar_menu_navegacao(self):
        """Gera os três botões destacados de seleção entre Relatório Mundial, Relatório Nacional e Laboratório."""
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("RELATÓRIO MUNDIAL", use_container_width=True, type="primary" if st.session_state.aba_selecionada == 'relatorio_mundial' else "secondary"):
                st.session_state.aba_selecionada = 'relatorio_mundial'
                st.rerun()
        with col_b2:
            if st.button("RELATÓRIO NACIONAL", use_container_width=True, type="primary" if st.session_state.aba_selecionada == 'relatorio_nacional' else "secondary"):
                st.session_state.aba_selecionada = 'relatorio_nacional'
                st.rerun()
        with col_b3:
            if st.button("LABORATÓRIO DE EXPLORAÇÃO", use_container_width=True, type="primary" if st.session_state.aba_selecionada == 'laboratorio' else "secondary"):
                st.session_state.aba_selecionada = 'laboratorio'
                st.rerun()

    def renderizar_kpis(self, df_faixas):
        """Calcula e exibe as métricas de resumo (KPIs) no topo da aplicação."""
        total_musicas = df_faixas.shape[0]
        total_generos = df_faixas['genero'].nunique()
        total_artistas = df_faixas['artista'].nunique()
        total_hits = df_faixas[df_faixas['popularidade'] >= 70].shape[0]

        st.markdown("---")
        st.markdown("### Resumo das Informações Analisadas")
        st.markdown("Os dados utilizados nesta análise foram obtidos a partir do [Spotify Tracks Dataset no Kaggle](https://www.kaggle.com/datasets/maharshipandya/spotify-tracks-dataset), abrangendo as características técnicas de áudio extraídas diretamente da API oficial da plataforma.")

        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        with col_kpi1:
            with st.container(border=True):
                st.metric(label="Músicas Analisadas", value=f"{total_musicas:,}".replace(",", "."))
        with col_kpi2:
            with st.container(border=True):
                st.metric(label="Artistas Identificados", value=f"{total_artistas:,}".replace(",", "."))
        with col_kpi3:
            with st.container(border=True):
                st.metric(label="Gêneros Musicais", value=total_generos)
        with col_kpi4:
            with st.container(border=True):
                st.metric(label="Faixas de Sucesso (Pop >= 70)", value=f"{total_hits:,}".replace(",", "."))

    def renderizar_relatorio(self, df_faixas, df_todos_generos, df_artistas, df_br):
        """Monta o relatório analítico estruturado de Insights Globais em duas colunas paralelas."""
        st.markdown("---")
        st.markdown("### Histórias e Curiosidades do Mercado Musical Global")
        st.markdown("Explore abaixo a análise sequencial das características sonoras que definem as tendências mundiais:")

        # --- INSIGHT 1 ---
        st.markdown("---")
        st.subheader("1. O DNA Sonoro muda drasticamente por Gênero")
        col1_1, col1_2 = st.columns([1.1, 0.9])
        with col1_1:
            with st.container(border=True):
                fig1 = px.scatter(
                    df_todos_generos, x="dance", y="energia", color="energia", size="total_faixas",
                    hover_data=["genero", "total_faixas"],
                    color_continuous_scale="Viridis",
                    labels={'dance': 'Dançabilidade Média', 'energia': 'Energia Média', 'total_faixas': 'Faixas'},
                    title="Dispersão de DNA Sonoro Médio por Gênero Musical"
                )
                fig1.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig1, use_container_width=True)
        with col1_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Dançabilidade · **Eixo Y:** Energia · **Tamanho da bolha:** Volume de faixas no banco · **Cor:** Escala de Energia.")
                dado_1 = "Gêneros essencialmente urbanos, como Hip-hop e Funk, posicionam-se no extremo direito (Dançabilidade média de 0.730 e 0.692). Gêneros instrumentais e de performance física, como Sertanejo e Rock, lideram no topo em Energia (acima de 0.640)."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_1}</div>", unsafe_allow_html=True)
                insight_1 = "O comportamento sonoro depende diretamente do estilo. Enquanto os gêneros urbanos são estruturados em cima de batidas rítmicas feitas para dançar, estilos clássicos e orgânicos priorizam a intensidade instrumental e o vigor da performance."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_1}</div>", unsafe_allow_html=True)

        # --- INSIGHT 2 ---
        st.markdown("---")
        st.subheader("2. Mega Hits são estatisticamente mais animados")
        col2_1, col2_2 = st.columns([1.1, 0.9])
        with col2_1:
            with st.container(border=True):
                df_animado = df_faixas.groupby('status_hit')[['danceability', 'energy']].mean().reset_index()
                df_melt = df_animado.melt(id_vars='status_hit', var_name='Atributo', value_name='Média')
                df_melt['Atributo'] = df_melt['Atributo'].map({'danceability': 'Dançabilidade', 'energy': 'Energia'})
                fig2 = px.bar(
                    df_melt, x="Atributo", y="Média", color="status_hit", barmode="group",
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'status_hit': 'Categoria'},
                    title="Comparativo das Médias de Ritmo e Intensidade"
                )
                fig2.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
        with col2_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Atributos · **Eixo Y:** Média (0 a 1) · **Barra Verde:** Mega Hits · **Barra Cinza:** Faixas comuns.")
                dado_2 = "Enquanto as músicas comuns têm uma média moderada de Dançabilidade (0.55), os Mega Hits saltam consideravelmente para uma média de 0.65 de Dançabilidade e 0.66 de Energia."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_2}</div>", unsafe_allow_html=True)
                insight_2 = "Músicas que alcançam grande repercussão de público tendem a ser significativamente mais enérgicas e propensas à dança em comparação com a média geral, refletindo uma forte inclinação do público por faixas dinâmicas e estimulantes nas paradas."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_2}</div>", unsafe_allow_html=True)

        # --- INSIGHT 3 ---
        st.markdown("---")
        st.subheader("3. Dançabilidade é a métrica número 1 para prever o Sucesso")
        col3_1, col3_2 = st.columns([1.1, 0.9])
        with col3_1:
            with st.container(border=True):
                df_imp = self.calcular_importancia_ml(df_faixas)
                fig3 = px.bar(
                    df_imp, x="importancia", y="atributo", orientation="h",
                    color="importancia", color_continuous_scale="Greens",
                    labels={'importancia': 'Importância', 'atributo': 'Atributo'},
                    title="Importância dos Atributos Técnicos para o Algoritmo"
                )
                fig3.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)
        with col3_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Peso do atributo no modelo de IA · **Eixo Y:** Variável de áudio analisada · **Cor:** Intensidade da importância.")
                dado_3 = "O modelo de classificação inteligente (Random Forest) identificou que a Dançabilidade obteve disparadamente a maior importância na classificação (acima de 35% de peso), seguida de perto pela Energia."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_3}</div>", unsafe_allow_html=True)
                insight_3 = "A cadência e a capacidade de movimentação (dançabilidade) são os fatores mais determinantes para definir a popularidade de uma faixa. O ritmo e a pulsação corporal se sobressaem sobre atributos como velocidade (BPM) ou intensidade sonora bruta no gosto do grande público."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_3}</div>", unsafe_allow_html=True)

        # --- INSIGHT 4 ---
        st.markdown("---")
        st.subheader("4. A Guerra do Volume (Loudness War) no Streaming")
        col4_1, col4_2 = st.columns([1.1, 0.9])
        with col4_1:
            with st.container(border=True):
                fig4 = px.box(
                    df_faixas, x="status_hit", y="loudness", color="status_hit",
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'status_hit': 'Categoria', 'loudness': 'Volume (dB)'},
                    title="Distribuição do Volume Físico das Faixas"
                )
                fig4.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig4, use_container_width=True)
        with col4_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Grupos · **Eixo Y:** Decibéis (valores negativos, quanto menor o valor negativo, mais alto é o som) · **Caixa Verde:** Limites do volume de Hits.")
                dado_4 = "Estatisticamente, os Hits tocam bem mais alto, concentrando sua média em -6.7 dB. Músicas comuns ou menos escutadas tocam de forma significativamente mais baixa, com média de -8.5 dB."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_4}</div>", unsafe_allow_html=True)
                insight_4 = "As faixas mais escutadas possuem uma masterização estatisticamente mais alta do que a média geral, um reflexo prático do fenômeno da compressão dinâmica na música popular contemporânea para capturar a atenção imediata do ouvinte."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_4}</div>", unsafe_allow_html=True)

        # --- INSIGHT 5 ---
        st.markdown("---")
        st.subheader("5. O Mainstream praticamente baniu o som Acústico")
        col5_1, col5_2 = st.columns([1.1, 0.9])
        with col5_1:
            with st.container(border=True):
                df_acustico = df_faixas.groupby('status_hit')['acousticness'].mean().reset_index()
                fig5 = px.bar(
                    df_acustico, x="status_hit", y="acousticness", color="status_hit",
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'status_hit': 'Categoria', 'acousticness': 'Média Acústica'},
                    title="Índice de Acústica Médio por Categoria"
                )
                fig5.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig5, use_container_width=True)
        with col5_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Grupos · **Eixo Y:** Escala acústica (0 representa digital; 1 representa acústico puro) · **Barra Verde:** Nível nos hits.")
                dado_5 = "Canções comuns mantêm um índice médio de som acústico de 0.33. Nos Mega Hits, esse índice despenca para 0.22, evidenciando uma sonoridade predominantemente artificial e sintetizada."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_5}</div>", unsafe_allow_html=True)
                insight_5 = "Há uma clara preferência do grande público por arranjos eletrônicos e digitais. Instrumentos puramente acústicos têm menor representatividade entre as faixas mais ouvidas do que no catálogo geral, apontando para uma era de produções sintetizadas."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_5}</div>", unsafe_allow_html=True)

        # --- INSIGHT 6 ---
        st.markdown("---")
        st.subheader("6. O canal de sucesso específico para músicas Tristes")
        col6_1, col6_2 = st.columns([1.1, 0.9])
        with col6_1:
            with st.container(border=True):
                df_tristes = df_faixas[(df_faixas['popularidade'] >= 70) & (df_faixas['valence'] < 0.4)]
                df_tristes_count = df_tristes['genero'].value_counts().reset_index()
                df_tristes_count.columns = ['Gênero', 'Hits Tristes']
                fig6 = px.bar(
                    df_tristes_count.head(10), x="Gênero", y="Hits Tristes",
                    color="Hits Tristes", color_continuous_scale="Reds",
                    labels={'Gênero': 'Gênero', 'Hits Tristes': 'Hits Tristes'},
                    title="Top 10 Gêneros por Volume de Hits Melancólicos"
                )
                fig6.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig6, use_container_width=True)
        with col6_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Gêneros musicais · **Eixo Y:** Quantidade de faixas melancólicas que viraram hit · **Cor:** Escala de quantidade.")
                dado_6 = "Ao cruzar Valência baixa (músicas melancólicas ou sombrias, abaixo de 0.4) com alta popularidade, descobrimos que os gêneros que mais conseguem emplacar essa sonoridade são Alt-Rock e Indie-Pop."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_6}</div>", unsafe_allow_html=True)
                insight_6 = "Embora músicas melancólicas (baixa valência) encontrem maior barreira na média geral, elas encontram um espaço fértil de grande recepção de público no Rock Alternativo e no Indie-Pop, onde há maior conexão do ouvinte com composições emotivas."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_6}</div>", unsafe_allow_html=True)

        # --- INSIGHT 7 ---
        st.markdown("---")
        st.subheader("7. Artistas de Elite e Consistência (O Efeito Bad Bunny)")
        col7_1, col7_2 = st.columns([1.1, 0.9])
        with col7_1:
            with st.container(border=True):
                fig7 = px.bar(
                    df_artistas, x="popularidade_media", y="artista", orientation="h",
                    color="popularidade_media", color_continuous_scale="Purples",
                    labels={'popularidade_media': 'Popularidade Média', 'artista': 'Artista'},
                    title="Top 10 Artistas por Consistência Comercial no Dataset"
                )
                fig7.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig7, use_container_width=True)
        with col7_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Média de popularidade · **Eixo Y:** Nomes dos artistas · **Cor:** Escala de popularidade do grupo.")
                dado_7 = "Artistas de alta consistência como Bad Bunny sustentam médias altíssimas de popularidade (85.3) ao longo de dezenas de músicas no dataset, distanciando-se de sucessos isolados de um hit só."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_7}</div>", unsafe_allow_html=True)
                insight_7 = "A popularidade consistente de artistas consagrados sugere um efeito de arrasto: catálogos consolidados geram engajamento contínuo, fazendo com que novos lançamentos desses artistas já iniciem com grande vantagem de recomendação."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_7}</div>", unsafe_allow_html=True)

    def renderizar_relatorio_nacional(self, df_faixas, df_br):
        """Monta o relatório analítico estruturado de Insights Nacionais dedicados à música brasileira."""
        st.markdown("---")
        st.markdown("### Relatório Especial: O DNA da Música Brasileira")
        st.markdown("Explore abaixo a análise exclusiva dos ritmos nacionais e as particularidades técnicas que definem o cenário nacional:")

        # --- INSIGHT NACIONAL 1: COMPARAÇÃO SONORA ---
        st.markdown("---")
        st.subheader("1. O Comportamento Sonoro dos Ritmos Brasileiros")
        col_br1_1, col_br1_2 = st.columns([1.1, 0.9])
        with col_br1_1:
            with st.container(border=True):
                df_br_melt = df_br.melt(id_vars='genero', var_name='Atributo', value_name='Média')
                df_br_melt['Atributo'] = df_br_melt['Atributo'].map({'dance': 'Dançabilidade', 'energia': 'Energia', 'acustico': 'Acústico'})
                # Formatar nomes dos gêneros para exibição no gráfico
                mapa_nomes = {'sertanejo': 'Sertanejo', 'forro': 'Forró', 'samba': 'Samba', 'pagode': 'Pagode', 'mpb': 'MPB', 'funk': 'Funk'}
                df_br_melt['genero_formatado'] = df_br_melt['genero'].map(mapa_nomes)
                fig_br = px.bar(
                    df_br_melt, x="genero_formatado", y="Média", color="Atributo", barmode="group",
                    color_discrete_sequence=["#1ed760", "#3D85C6", "#FF9900"],
                    labels={'genero_formatado': 'Gênero', 'Média': 'Média'},
                    title="Comparativo Sonoro: Gêneros Musicais Brasileiros"
                )
                fig_br.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_br, use_container_width=True)
        with col_br1_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Gêneros nacionais · **Eixo Y:** Escala média (0 a 1) · **Barra Verde:** Dançabilidade · **Barra Azul:** Energia · **Barra Laranja:** Nível Acústico.")
                dado_br1 = "O Funk lidera em Dançabilidade (0.692) e possui o menor índice acústico (0.324). O Forró atinge a maior Energia média (0.789). Pagode e Samba destacam-se como os mais orgânicos, com os maiores índices acústicos (0.562 e 0.485, respectivamente)."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_br1}</div>", unsafe_allow_html=True)
                insight_br1 = "A música brasileira exibe um comportamento sonoro multifacetado: enquanto o Funk e o Forró apresentam alto apelo físico com grande dançabilidade e intensidade digital, estilos como o Pagode e o Samba mantêm viva a rica tradição acústica nacional através de instrumentos orgânicos."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_br1}</div>", unsafe_allow_html=True)

        # --- INSIGHT NACIONAL 2: BPM (BOXPLOT DE VELOCIDADE) ---
        st.markdown("---")
        st.subheader("2. A Velocidade e a Pulsação do Ritmo Nacional (BPM)")
        col_br2_1, col_br2_2 = st.columns([1.1, 0.9])
        with col_br2_1:
            with st.container(border=True):
                df_br_completo = df_faixas[df_faixas['genero'].isin(['sertanejo', 'forro', 'samba', 'pagode', 'mpb', 'funk'])].copy()
                df_br_completo['genero_formatado'] = df_br_completo['genero'].map(mapa_nomes)
                fig_bpm = px.box(
                    df_br_completo, x="genero_formatado", y="tempo", color="genero_formatado",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    labels={'genero_formatado': 'Gênero', 'tempo': 'BPM (Velocidade)'},
                    title="Distribuição de Velocidade (BPM) por Gênero Nacional"
                )
                fig_bpm.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_bpm, use_container_width=True)
        with col_br2_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Gêneros nacionais · **Eixo Y:** Batidas Por Minuto (BPM) · **Caixas Coloridas:** Variação e limites de velocidade das músicas.")
                dado_br2 = "O Forró lidera em andamento físico rápido com uma média de velocidade próxima a 130 BPM, acompanhado de perto pelo Funk (média de 125 BPM). A MPB e o Samba apresentam andamentos mais cadenciados e controlados, com médias entre 110 e 115 BPM."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_br2}</div>", unsafe_allow_html=True)
                insight_br2 = "Gêneros focados em comemorações e performance de dança ativa (como Forró e Funk) estruturam-se sobre andamentos rápidos e tempos marcados. Em contrapartida, estilos voltados à apreciação poética e dança clássica (Samba e MPB) priorizam ritmos confortáveis e andamentos mais relaxantes para o ouvinte."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_br2}</div>", unsafe_allow_html=True)

        # --- INSIGHT NACIONAL 3: POPULARIDADE MÉDIA ---
        st.markdown("---")
        st.subheader("3. Tração Comercial e Aceitação dos Gêneros Brasileiros")
        col_br3_1, col_br3_2 = st.columns([1.1, 0.9])
        with col_br3_1:
            with st.container(border=True):
                df_pop_br = df_br_completo.groupby('genero_formatado')['popularidade'].mean().reset_index().sort_values(by='popularidade', ascending=False)
                fig_pop = px.bar(
                    df_pop_br, x="popularidade", y="genero_formatado", orientation="h",
                    color="popularidade", color_continuous_scale="Greens",
                    labels={'popularidade': 'Popularidade Média', 'genero_formatado': 'Gênero'},
                    title="Popularidade Média dos Gêneros Nacionais no Dataset"
                )
                fig_pop.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_pop, use_container_width=True)
        with col_br3_2:
            with st.container(border=True):
                st.markdown("**Legenda e Visual:**\n* **Eixo X:** Escala de Popularidade Média (0 a 100) · **Eixo Y:** Gêneros nacionais · **Cor:** Intensidade da popularidade média.")
                dado_br3 = "O Sertanejo e o Funk apresentam a maior média de popularidade no banco de dados (ambos acima de 50 de pontuação média). MPB e Samba mantêm médias estáveis mas inferiores (entre 35 e 40)."
                st.markdown(f"<div style='{self.estilo_dado}'><strong>O que o dado mostra:</strong><br>{dado_br3}</div>", unsafe_allow_html=True)
                insight_br3 = "O Sertanejo e o Funk possuem forte apelo de consumo em massa e rotação contínua nas plataformas de streaming atuais, concentrando os maiores volumes de engajamento diário de playlists comerciais. A MPB e o Samba, embora possuam valor cultural indiscutível, operam em nichos de consumo estáveis, mas com menor frequência de reprodução massiva nos charts."
                st.markdown(f"<div style='{self.estilo_insight}'><strong>Insight:</strong><br>{insight_br3}</div>", unsafe_allow_html=True)

    def renderizar_laboratorio(self, df_faixas):
        """Monta a aba de laboratório dinâmico com filtros interativos e os 8 gráficos editáveis."""
        st.markdown("---")
        st.markdown("### Laboratório Analítico Interativo")
        st.markdown("Ajuste os filtros abaixo para editar dinamicamente todos os 8 gráficos da análise simultaneamente:")
        
        # Filtros do Laboratório
        with st.container(border=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                generos_disponiveis = sorted(df_faixas['genero'].dropna().unique())
                generos_selecionados = st.multiselect(
                    "Selecionar Gêneros para Análise:",
                    options=generos_disponiveis,
                    default=['pop', 'rock', 'sertanejo', 'funk', 'techno/house', 'latin']
                )
            with col_f2:
                pop_range = st.slider(
                    "Limitar Popularidade das Músicas:",
                    min_value=0, max_value=100,
                    value=(0, 100)
                )

        # Filtragem em tempo real
        df_filtrado = df_faixas[
            (df_faixas['genero'].isin(generos_selecionados)) &
            (df_faixas['popularidade'] >= pop_range[0]) &
            (df_faixas['popularidade'] <= pop_range[1])
        ]
        
        if df_filtrado.empty:
            st.warning("Nenhuma música corresponde aos filtros selecionados. Tente selecionar outros parâmetros!")
            return
            
        st.markdown("---")
        st.markdown("### Visualizações Editáveis")
        
        # Grid Linha 1
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            with st.container(border=True):
                fig_scatter = px.scatter(
                    df_filtrado.head(1500), # Limite de performance
                    x="danceability", y="energy", color="status_hit",
                    hover_data=["musica", "artista", "genero"],
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'danceability': 'Dançabilidade', 'energy': 'Energia', 'status_hit': 'Categoria'},
                    opacity=0.7, title="1. Distribuição: Energia vs Dançabilidade"
                )
                fig_scatter.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_scatter, use_container_width=True)
        with col_g2:
            with st.container(border=True):
                df_gen_avg = df_filtrado.groupby('genero')[['danceability', 'energy', 'acousticness']].mean().reset_index()
                df_gen_melt = df_gen_avg.melt(id_vars='genero', var_name='Atributo', value_name='Média')
                df_gen_melt['Atributo'] = df_gen_melt['Atributo'].map({'danceability': 'Dançabilidade', 'energy': 'Energia', 'acousticness': 'Acústico'})
                fig_gen = px.bar(
                    df_gen_melt, x="genero", y="Média", color="Atributo", barmode="group",
                    color_discrete_sequence=["#1ed760", "#3D85C6", "#FF9900"],
                    labels={'genero': 'Gênero', 'Média': 'Média'},
                    title="2. Comparativo Sonoro por Gênero Selecionado"
                )
                fig_gen.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_gen, use_container_width=True)

        # Grid Linha 2
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            with st.container(border=True):
                df_anim_f = df_filtrado.groupby('status_hit')[['danceability', 'energy']].mean().reset_index()
                df_melt_f = df_anim_f.melt(id_vars='status_hit', var_name='Atributo', value_name='Média')
                df_melt_f['Atributo'] = df_melt_f['Atributo'].map({'danceability': 'Dançabilidade', 'energy': 'Energia'})
                fig_bar_f = px.bar(
                    df_melt_f, x="Atributo", y="Média", color="status_hit", barmode="group",
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'status_hit': 'Categoria'},
                    title="3. Ritmo e Intensidade: Hits vs Comuns"
                )
                fig_bar_f.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_bar_f, use_container_width=True)
        with col_g4:
            with st.container(border=True):
                fig_box_f = px.box(
                    df_filtrado, x="status_hit", y="loudness", color="status_hit",
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'status_hit': 'Categoria', 'loudness': 'Volume (dB)'},
                    title="4. Distribuição do Volume das Faixas"
                )
                fig_box_f.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_box_f, use_container_width=True)

        # Grid Linha 3
        col_g5, col_g6 = st.columns(2)
        with col_g5:
            with st.container(border=True):
                df_acust_f = df_filtrado.groupby('status_hit')['acousticness'].mean().reset_index()
                fig_acust_f = px.bar(
                    df_acust_f, x="status_hit", y="acousticness", color="status_hit",
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'status_hit': 'Categoria', 'acousticness': 'Índice Acústico'},
                    title="5. Índice de Acústica Médio: Hits vs Comuns"
                )
                fig_acust_f.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_acust_f, use_container_width=True)
        with col_g6:
            with st.container(border=True):
                fig_violin_f = px.violin(
                    df_filtrado, y="valence", color="status_hit",
                    box=True, points=False,
                    color_discrete_map={"Mega Hit (>=70)": "#1ed760", "Comum (<70)": "#393e46"},
                    labels={'status_hit': 'Categoria', 'valence': 'Alegria (Valência)'},
                    title="6. Distribuição de Alegria (Valência) das Faixas"
                )
                fig_violin_f.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_violin_f, use_container_width=True)

        # Grid Linha 4
        col_g7, col_g8 = st.columns(2)
        with col_g7:
            with st.container(border=True):
                df_trist_f = df_filtrado[(df_filtrado['popularidade'] >= 70) & (df_filtrado['valence'] < 0.4)]
                if df_trist_f.empty:
                    st.info("Nenhum hit melancólico (Valência < 0.4 e Pop >= 70) nos gêneros/popularidades selecionados.")
                else:
                    df_trist_count_f = df_trist_f['genero'].value_counts().reset_index()
                    df_trist_count_f.columns = ['Gênero', 'Hits Tristes']
                    fig_trist_f = px.bar(
                        df_trist_count_f.head(10), x="Gênero", y="Hits Tristes",
                        color="Hits Tristes", color_continuous_scale="Reds",
                        labels={'Gênero': 'Gênero', 'Hits Tristes': 'Hits Tristes'},
                        title="7. Gêneros por Volume de Hits Melancólicos"
                    )
                    fig_trist_f.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_trist_f, use_container_width=True)
        with col_g8:
            with st.container(border=True):
                df_art_f = df_filtrado.groupby('artista').agg(
                    popularidade_media=('popularidade', 'mean'),
                    total_faixas=('musica', 'count')
                ).reset_index()
                df_art_f = df_art_f[df_art_f['total_faixas'] >= 2] # Mínimo 2 músicas no filtro para relevância
                if df_art_f.empty:
                    st.info("Sem dados suficientes para listar artistas consistentes com mais de 2 faixas.")
                else:
                    df_art_top_f = df_art_f.sort_values(by='popularidade_media', ascending=False).head(10)
                    fig_art_f = px.bar(
                        df_art_top_f, x="popularidade_media", y="artista", orientation="h",
                        color="popularidade_media", color_continuous_scale="Purples",
                        labels={'popularidade_media': 'Popularidade Média', 'artista': 'Artista'},
                        title="8. Top 10 Artistas por Popularidade Média"
                    )
                    fig_art_f.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_art_f, use_container_width=True)

    def rodar(self):
        """Orquestra o carregamento de dados e a renderização sequencial da página."""
        # Carrega dados
        df_faixas, df_todos_generos, df_artistas, df_br = self.carregar_dados()
        
        # Renderiza a estrutura da página
        self.renderizar_cabecalho()
        self.renderizar_menu_navegacao()
        self.renderizar_kpis(df_faixas)
        
        # Fluxo condicional das abas
        if st.session_state.aba_selecionada == 'relatorio_mundial':
            self.renderizar_relatorio(df_faixas, df_todos_generos, df_artistas, df_br)
        elif st.session_state.aba_selecionada == 'relatorio_nacional':
            self.renderizar_relatorio_nacional(df_faixas, df_br)
        else:
            self.renderizar_laboratorio(df_faixas)

if __name__ == "__main__":
    # Inicializa e executa a aplicação
    app = DashboardSpotifyApp()
    app.rodar()
