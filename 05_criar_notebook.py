import nbformat as nbf
import os

print("Gerando o Jupyter Notebook da Fase 3...")

nb = nbf.v4.new_notebook()

# Células de Markdown e Código do Notebook
celulas = [
    nbf.v4.new_markdown_cell("# Análise Exploratória (EDA) - O Algoritmo do Sucesso\nNeste notebook, vamos analisar os dados salvos no nosso banco SQLite para descobrir o que faz uma música virar um hit no Spotify.\n\n_Dica: Clique na célula abaixo e aperte Shift + Enter para rodar o código._"),
    
    nbf.v4.new_code_cell("import pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport sqlite3\n\n# 1. Conectar ao banco de dados\nconn = sqlite3.connect('../spotify_brasil.db')\n\n# 2. Puxar todas as faixas e seus atributos\nquery = '''\nSELECT f.nome, f.popularidade, f.genero, a.danceability, a.energy, a.valence, a.tempo\nFROM faixas f\nJOIN atributos_audio a ON f.id = a.faixa_id\n'''\ndf = pd.read_sql(query, conn)\ndf.head()"),
    
    nbf.v4.new_markdown_cell("## 1. O DNA do Hit (Energia vs Popularidade)\nVamos criar um gráfico de distribuição separando o que é considerado um Hit (popularidade acima de 70) do restante das músicas."),
    
    nbf.v4.new_code_cell("# Cria uma nova coluna separando os Hits\ndf['is_hit'] = df['popularidade'] >= 70\n\nplt.figure(figsize=(10, 6))\nsns.histplot(data=df, x='energy', hue='is_hit', bins=30, kde=True)\nplt.title('Distribuição de Energia: Hits (Laranja) vs Resto (Azul)')\nplt.show()"),
    
    nbf.v4.new_markdown_cell("## 2. Machine Learning: Prevendo um Hit\nVamos treinar um modelo preditivo rápido (Random Forest) para ver qual atributo musical tem maior peso para definir se uma música entra no Top Charts."),
    
    nbf.v4.new_code_cell("from sklearn.ensemble import RandomForestClassifier\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.metrics import classification_report\n\nfeatures = ['energy', 'danceability', 'valence', 'tempo']\ndf_ml = df.dropna(subset=features + ['is_hit']).copy()\n\nX = df_ml[features]\ny = df_ml['is_hit']\n\n# Separa os dados de treino e de teste\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n# Treina a inteligência artificial\nmodel = RandomForestClassifier(n_estimators=100, random_state=42)\nmodel.fit(X_train, y_train)\n\n# Analisa qual característica foi mais decisiva para o sucesso\nimportances = pd.Series(model.feature_importances_, index=features).sort_values()\nimportances.plot(kind='barh', color='green', title='Importância de cada atributo para o Hit')\nplt.show()")
]

nb['cells'] = celulas

# Salva o arquivo dentro da pasta notebooks
caminho = os.path.join("notebooks", "01_eda_hits_brasil.ipynb")
with open(caminho, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Sucesso! Notebook criado em: {caminho}")
