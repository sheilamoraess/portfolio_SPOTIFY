# Projeto: O Algoritmo do Sucesso Musical
Investigacao do DNA sonoro por tras dos maiores hits do Spotify atraves de Python, SQL, Streamlit e Machine Learning.

## Contexto
A industria da musica e altamente competitiva. Milhares de faixas sao lancadas diariamente, mas apenas uma pequena fracao atinge o topo das paradas (Top Charts). Este projeto tem como objetivo investigar o "DNA sonoro" das musicas. Sera que faixas mais energicas e dancantes tem mais chance de se tornarem hits? Como os diferentes generos se comportam em relacao a esses atributos?

## Perguntas Respondidas
* Quais atributos de audio (energia, dancabilidade, BPM) sao mais comuns nas musicas populares?
* A "Guerra do Volume" (Loudness War) existe nas paradas de sucesso?
* E possivel prever se uma musica sera um "Hit" com base em suas caracteristicas acusticas?

## Fontes de Dados
* Spotify Tracks Dataset: Um conjunto de dados com mais de 114 mil faixas contendo as informacoes vitais de audio extraidas diretamente da API oficial do Spotify (Energy, Danceability, Valence, Tempo, Loudness, Acousticness).

## Metodologia e Arquitetura
1. Coleta de Dados: Classe Python utilizando pandas para download e processamento do arquivo CSV bruto a partir de uma fonte remota.
2. Armazenamento e Modelagem (SQL): Criacao de um banco de dados relacional local em SQLite com tres tabelas conectadas (artistas, faixas, atributos_audio).
3. Qualidade de Dados (ETL): Tratamento de valores nulos (dados corrompidos) e injecao de dados usando SQLAlchemy no banco.
4. Machine Learning: Uso do algoritmo preditivo RandomForestClassifier para determinar quais caracteristicas de audio sao mais decisivas para o sucesso de uma faixa.
5. Limpeza e Agrupamento de Generos: Classe Python executando atualizacoes SQL para consolidar micro-generos redundantes (como chicago-house, detroit-techno, latino, reggaeton, children) em macro-generos mais consistentes (techno/house, latin, kids).
6. Dashboard Interativo (Web App): Aplicacao web estruturada em POO com Streamlit e Plotly sob um visual gamer escuro com realces neon verde e azul. A navegacao permite alternar entre o Relatorio de Insights e o Laboratorio de Exploracao.

## Principais Insights do Mercado Musical
1. O DNA Sonoro por Genero: Generos urbanos (Hip-hop e Funk) lideram em dancabilidade, enquanto generos instrumentais/organicos (Sertanejo e Rock) dependem mais da energia e intensidade.
2. Mega Hits sao Upbeat: Musicas comuns mantem dancabilidade em 0.55, enquanto Mega Hits (popularidade acima de 70) saltam para 0.65 de dancabilidade e 0.66 de energia, revelando a forte preferencia das massas por faixas animadas.
3. A Dancabilidade e Rei: O modelo de IA provou que a Dancabilidade (groove e cadencia) e a variavel com maior peso de importancia tecnica para prever se uma cancao se tornara um sucesso.
4. A Guerra do Volume (Loudness War): Hits de sucesso possuem volume medio de -6.7 dB, significativamente mais alto do que faixas comuns (-8.5 dB), comprovando que masterizacoes mais barulhentas capturam a atencao imediata do ouvinte.
5. A Morte do Acustico no Mainstream: O indice de som acustico despenca de 0.33 em musicas comuns para apenas 0.22 em musicas de sucesso, consolidando o dominio de producoes sintetizadas digitais.
6. O Nicho da Tristeza Pop: Musicas melancolicas (baixo indice de alegria/valencia) encontram barreira para estourar, a menos que sigam o canal estrategico de generos com publico receptivo a isso, como Alt-Rock e Indie-Pop.
7. Artistas de Elite e Catalogo (O Efeito Bad Bunny): A consistencia de alguns artistas de ponta, como Bad Bunny (media de popularidade de 85.3 com 22 faixas), demonstra que o proprio algoritmo do Spotify age como catalisador de entrega continua para catalogos consolidados.
8. Destaque Nacional (O DNA da Musica Brasileira): O Funk se consolidou como o ritmo mais dancante (0.69) e sintetizado/digital (baixo acustico de 0.32), enquanto o Forró e o Sertanejo registram as maiores intensidades energicas (acima de 0.70). Pagode e Samba preservam sua tradicional instrumentacao organica, registrando os maiores indices acusticos (acima de 0.48).

## O Laboratorio de Exploracao Interativo
O projeto conta com um Laboratorio Analitico dinamico para que o usuario execute suas proprias investigacoes nos dados musicais do Spotify. Nele, e possivel:
* Selecionar multiplos generos especificos para comparacao atraves de um menu de selecao.
* Ajustar uma barra de rolagem (slider) para delimitar o intervalo de popularidade desejado.
* Atualizar de forma automatica e simultanea as seguintes 8 visualizacoes em tempo real:
  1. Distribuiçao: Energia vs Dancabilidade (Dispersao que separa hits de musicas comuns).
  2. Comparativo Sonoro por Genero Selecionado (Barras agrupadas com medias de dancabilidade, energia e acustica).
  3. Ritmo e Intensidade: Hits vs Comuns (Comparacao de medias de ritmo).
  4. Distribuiçao do Volume das Faixas (Boxplot demonstrando variacao de decibeis).
  5. Indice de Acustica Medio: Hits vs Comuns (Grafico de colunas medindo o nivel de instrumentacao organica).
  6. Distribuiçao de Alegria (Valencia) das Faixas (Violin plot mostrando a distribuicao da positividade musical).
  7. Generos por Volume de Hits Melancolicos (Grafico de barras com quantidade de faixas tristes de sucesso).
  8. Top 10 Artistas por Popularidade Media (Ranking de consistencia comercial dos artistas).

## Como Rodar o Projeto Localmente
1. Clone este repositorio no seu computador.
2. Instale as bibliotecas necessarias:
   ```bash
   pip install -r requirements.txt
   ```
3. Processamento de Dados (Execute apenas 1 vez para criar e limpar o banco local):
   * `python 02_download_dataset.py` (Realiza o download dos dados brutos de forma automatica)
   * `python 03_carregar_banco.py` (Cria a modelagem relacional no SQLite e popula as tabelas)
   * `python 09_limpeza_generos.py` (Executa o agrupamento de micro-generos redundantes no banco de dados)
4. Inicie o Servidor do Dashboard Interativo:
   ```bash
   streamlit run 08_dashboard_interativo.py
   ```
5. O aplicativo web abrira automaticamente no seu navegador no endereço `http://localhost:8501`.
