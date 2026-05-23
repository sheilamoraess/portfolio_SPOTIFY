import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURAÇÃO VISUAL GLOBAL DO DASHBOARD
# ============================================================

PALETA_PRINCIPAL = ['#1DB954', '#1ED760', '#169C40', '#0D6B2C', '#00BFFF', '#FF6B6B', '#FFD93D', '#C3A6FF']
COR_FUNDO = '#121212'
COR_PAINEL = '#1E1E1E'
COR_TEXTO = '#FFFFFF'
COR_TEXTO_SUAVE = '#B3B3B3'
COR_VERDE = '#1DB954'

plt.rcParams['figure.facecolor'] = COR_FUNDO
plt.rcParams['axes.facecolor'] = COR_PAINEL
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.labelcolor'] = COR_TEXTO
plt.rcParams['xtick.color'] = COR_TEXTO_SUAVE
plt.rcParams['ytick.color'] = COR_TEXTO_SUAVE
plt.rcParams['text.color'] = COR_TEXTO
plt.rcParams['grid.color'] = '#333333'
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['font.family'] = 'DejaVu Sans'


class DashboardSpotify:
    """
    Classe principal do Dashboard. Responsável por:
    - Carregar os dados do banco SQLite
    - Filtrar os gêneros mais representativos para análises justas
    - Gerar todos os gráficos e salvar a imagem final
    """

    GENEROS_FOCO = ['acoustic', 'pop', 'rock', 'hip-hop', 'jazz',
                    'classical', 'r-n-b', 'forro', 'sertanejo',
                    'pagode', 'funk', 'electronic', 'indie', 'blues', 'country']

    def __init__(self, db_path='spotify_brasil.db'):
        self.db_path = db_path
        self.df = self._carregar_dados()

    def _carregar_dados(self):
        """Carrega e filtra os dados relevantes do banco de dados."""
        print("Carregando dados do banco...")
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT
                f.nome AS musica,
                art.nome AS artista,
                f.genero,
                f.popularidade,
                a.danceability,
                a.energy,
                a.valence,
                a.tempo AS bpm,
                a.loudness,
                a.acousticness
            FROM faixas f
            JOIN atributos_audio a ON f.id = a.faixa_id
            JOIN artistas art ON f.artista_id = art.id
            WHERE f.genero IN ({})
        """.format(','.join([f"'{g}'" for g in self.GENEROS_FOCO]))
        df = pd.read_sql(query, conn)
        conn.close()

        # Cria coluna de categoria de hit
        df['categoria'] = pd.cut(
            df['popularidade'],
            bins=[-1, 30, 60, 100],
            labels=['Baixa (0-30)', 'Média (31-60)', 'Alta (61-100)']
        )
        print(f"Dados carregados: {len(df)} faixas, {df['genero'].nunique()} gêneros.")
        return df

    # ------------------------------------------------------------------ #
    # GRÁFICO 1 — Barras Horizontais: DNA Sonoro dos Gêneros             #
    # ------------------------------------------------------------------ #
    def grafico_dna_generos(self, ax):
        medias = (self.df.groupby('genero')[['danceability', 'energy', 'valence']]
                  .mean()
                  .sort_values('danceability', ascending=True))

        x = np.arange(len(medias))
        largura = 0.28

        ax.barh(x - largura, medias['danceability'], largura, label='Dançabilidade', color='#1DB954', alpha=0.9)
        ax.barh(x,           medias['energy'],       largura, label='Energia',       color='#00BFFF', alpha=0.9)
        ax.barh(x + largura, medias['valence'],      largura, label='Alegria',       color='#FFD93D', alpha=0.9)

        ax.set_yticks(x)
        ax.set_yticklabels(medias.index, fontsize=8)
        ax.set_xlim(0, 1)
        ax.set_title('DNA Sonoro por Gênero', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Valor médio (0 a 1)', fontsize=8)
        ax.legend(fontsize=7, loc='lower right', framealpha=0.2)
        ax.grid(axis='x', alpha=0.3)

    # ------------------------------------------------------------------ #
    # GRÁFICO 2 — Scatter Plot: Energia vs Dançabilidade (por popularidade)
    # ------------------------------------------------------------------ #
    def grafico_scatter_hits(self, ax):
        cores_cat = {'Baixa (0-30)': '#555555', 'Média (31-60)': '#00BFFF', 'Alta (61-100)': '#1DB954'}
        for cat, grp in self.df.groupby('categoria'):
            ax.scatter(grp['danceability'], grp['energy'],
                       c=cores_cat[cat], label=cat, alpha=0.4, s=10, edgecolors='none')

        ax.set_title('Energia × Dançabilidade por Popularidade', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Dançabilidade', fontsize=8)
        ax.set_ylabel('Energia', fontsize=8)
        ax.legend(title='Popularidade', fontsize=7, title_fontsize=8, framealpha=0.2)
        ax.grid(alpha=0.2)

    # ------------------------------------------------------------------ #
    # GRÁFICO 3 — Boxplot: Distribuição de BPM por Categoria de Hit      #
    # ------------------------------------------------------------------ #
    def grafico_bpm_hits(self, ax):
        categorias = ['Baixa (0-30)', 'Média (31-60)', 'Alta (61-100)']
        dados_box = [self.df[self.df['categoria'] == c]['bpm'].dropna() for c in categorias]
        cores_box = ['#555555', '#00BFFF', '#1DB954']

        bp = ax.boxplot(dados_box, patch_artist=True, widths=0.5,
                        medianprops=dict(color='white', linewidth=2))
        for patch, cor in zip(bp['boxes'], cores_box):
            patch.set_facecolor(cor)
            patch.set_alpha(0.7)

        ax.set_xticklabels(['Baixa\n(0-30)', 'Média\n(31-60)', 'Alta\n(61-100)'], fontsize=8)
        ax.set_title('Distribuição de BPM por Popularidade', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.set_ylabel('BPM', fontsize=8)
        ax.grid(axis='y', alpha=0.3)

    # ------------------------------------------------------------------ #
    # GRÁFICO 4 — Heatmap de Correlação entre Atributos                  #
    # ------------------------------------------------------------------ #
    def grafico_heatmap_correlacao(self, ax):
        colunas = ['popularidade', 'danceability', 'energy', 'valence', 'bpm', 'loudness', 'acousticness']
        renomear = {
            'popularidade': 'Popularidade', 'danceability': 'Dançabilidade',
            'energy': 'Energia', 'valence': 'Alegria',
            'bpm': 'BPM', 'loudness': 'Volume', 'acousticness': 'Acústica'
        }
        corr = self.df[colunas].corr().rename(columns=renomear, index=renomear)
        mask = np.triu(np.ones_like(corr, dtype=bool))

        sns.heatmap(corr, ax=ax, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
                    center=0, vmin=-1, vmax=1, annot_kws={'size': 7},
                    linewidths=0.5, cbar_kws={'shrink': 0.8})
        ax.set_title('Correlação entre Atributos', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.tick_params(axis='x', rotation=30, labelsize=7)
        ax.tick_params(axis='y', rotation=0, labelsize=7)

    # ------------------------------------------------------------------ #
    # GRÁFICO 5 — Barras agrupadas: Hits vs Não-Hits por Gênero          #
    # ------------------------------------------------------------------ #
    def grafico_hits_por_genero(self, ax):
        generos_top = (self.df.groupby('genero').size()
                       .sort_values(ascending=False).head(10).index)
        df_top = self.df[self.df['genero'].isin(generos_top)].copy()
        df_top['is_hit'] = df_top['popularidade'] >= 61

        taxa = (df_top.groupby('genero')['is_hit'].mean() * 100).sort_values(ascending=False)

        cores = [COR_VERDE if v >= taxa.mean() else '#555555' for v in taxa.values]
        barras = ax.bar(taxa.index, taxa.values, color=cores, alpha=0.85, edgecolor='none')

        # Linha da média
        ax.axhline(taxa.mean(), color='#FFD93D', linestyle='--', linewidth=1, label=f'Média: {taxa.mean():.1f}%')

        ax.set_title('Taxa de Hits por Gênero (%)', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.set_ylabel('% de Músicas Populares', fontsize=8)
        ax.tick_params(axis='x', rotation=35, labelsize=7)
        ax.legend(fontsize=7, framealpha=0.2)
        ax.grid(axis='y', alpha=0.3)

    # ------------------------------------------------------------------ #
    # GRÁFICO 6 — Feature Importance: O que define um Hit?               #
    # ------------------------------------------------------------------ #
    def grafico_feature_importance(self, ax):
        features = ['danceability', 'energy', 'valence', 'bpm', 'loudness', 'acousticness']
        nomes = ['Dançabilidade', 'Energia', 'Alegria', 'BPM', 'Volume', 'Acústica']

        df_ml = self.df.dropna(subset=features + ['popularidade']).copy()
        df_ml['hit'] = (df_ml['popularidade'] >= 61).astype(int)

        X = df_ml[features]
        y = df_ml['hit']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        modelo = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        modelo.fit(X_train, y_train)

        importancias = pd.Series(modelo.feature_importances_, index=nomes).sort_values()
        cores_imp = [COR_VERDE if v == importancias.max() else '#00BFFF' for v in importancias.values]

        importancias.plot(kind='barh', ax=ax, color=cores_imp, alpha=0.85, edgecolor='none')
        ax.set_title('O que define um Hit? (Machine Learning)', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Importância relativa', fontsize=8)
        ax.grid(axis='x', alpha=0.3)

        # Adiciona os valores nas barras
        for i, (val, nome) in enumerate(zip(importancias.values, importancias.index)):
            ax.text(val + 0.002, i, f'{val:.3f}', va='center', fontsize=7, color=COR_TEXTO_SUAVE)

    # ------------------------------------------------------------------ #
    # GRÁFICO 7 — Violino: Alegria (Valence) por Categoria de Hit        #
    # ------------------------------------------------------------------ #
    def grafico_violino_valence(self, ax):
        df_violin = self.df[['categoria', 'valence']].dropna()
        categorias = ['Baixa (0-30)', 'Média (31-60)', 'Alta (61-100)']
        cores_vl = ['#555555', '#00BFFF', '#1DB954']

        partes = ax.violinplot(
            [df_violin[df_violin['categoria'] == c]['valence'] for c in categorias],
            positions=[1, 2, 3], showmedians=True, showextrema=False
        )
        for pc, cor in zip(partes['bodies'], cores_vl):
            pc.set_facecolor(cor)
            pc.set_alpha(0.6)
        partes['cmedians'].set_color('white')

        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(['Baixa\n(0-30)', 'Média\n(31-60)', 'Alta\n(61-100)'], fontsize=8)
        ax.set_title('Alegria (Valence) por Popularidade', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.set_ylabel('Valência (0=Triste, 1=Alegre)', fontsize=8)
        ax.grid(axis='y', alpha=0.3)

    # ------------------------------------------------------------------ #
    # GRÁFICO 8 — Histograma: Distribuição de Popularidade               #
    # ------------------------------------------------------------------ #
    def grafico_distribuicao_popularidade(self, ax):
        ax.hist(self.df['popularidade'], bins=40, color=COR_VERDE, alpha=0.7, edgecolor='none')
        ax.axvline(61, color='#FFD93D', linestyle='--', linewidth=1.5, label='Limiar de Hit (61)')
        ax.axvline(self.df['popularidade'].mean(), color='#FF6B6B', linestyle='--',
                   linewidth=1.5, label=f"Média: {self.df['popularidade'].mean():.0f}")

        ax.set_title('Distribuição de Popularidade', color=COR_VERDE, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Popularidade (0 a 100)', fontsize=8)
        ax.set_ylabel('Quantidade de Músicas', fontsize=8)
        ax.legend(fontsize=7, framealpha=0.2)
        ax.grid(axis='y', alpha=0.3)

    # ------------------------------------------------------------------ #
    # MÉTODO PRINCIPAL: Monta e salva o dashboard completo               #
    # ------------------------------------------------------------------ #
    def gerar_dashboard(self, salvar_em='dashboard/dashboard_spotify.png'):
        print("Gerando o dashboard completo...")

        fig = plt.figure(figsize=(22, 24), facecolor=COR_FUNDO)
        fig.suptitle(
            'O ALGORITMO DO SUCESSO MUSICAL — Spotify Analysis Dashboard',
            color=COR_VERDE, fontsize=18, fontweight='bold', y=0.98
        )
        fig.text(0.5, 0.965, 'Uma análise do DNA sonoro de 114.000 faixas para entender o que faz uma música virar um hit',
                 ha='center', color=COR_TEXTO_SUAVE, fontsize=10)

        # Grade 4 linhas x 2 colunas
        gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.45, wspace=0.35,
                               left=0.07, right=0.97, top=0.95, bottom=0.04)

        # Linha 1
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        # Linha 2
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])
        # Linha 3
        ax5 = fig.add_subplot(gs[2, 0])
        ax6 = fig.add_subplot(gs[2, 1])
        # Linha 4
        ax7 = fig.add_subplot(gs[3, 0])
        ax8 = fig.add_subplot(gs[3, 1])

        # Chama cada gráfico
        self.grafico_dna_generos(ax1)
        self.grafico_scatter_hits(ax2)
        self.grafico_bpm_hits(ax3)
        self.grafico_heatmap_correlacao(ax4)
        self.grafico_hits_por_genero(ax5)
        self.grafico_feature_importance(ax6)
        self.grafico_violino_valence(ax7)
        self.grafico_distribuicao_popularidade(ax8)

        plt.savefig(salvar_em, dpi=150, bbox_inches='tight', facecolor=COR_FUNDO)
        print(f"\nDashboard salvo em '{salvar_em}'!")
        plt.show()


if __name__ == "__main__":
    dash = DashboardSpotify()
    dash.gerar_dashboard()
