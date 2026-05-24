# Projeto: O Algoritmo do Sucesso Musical
Investigação do DNA sonoro por trás dos maiores hits do Spotify através de Python, SQL, Streamlit e Machine Learning.

## Contexto
A indústria da música é altamente competitiva. Milhares de faixas são lançadas diariamente, mas apenas uma pequena fração atinge o topo das paradas (Top Charts). Este projeto tem como objetivo investigar o "DNA sonoro" das músicas. Será que faixas mais enérgicas e dançantes têm mais chance de se tornarem hits? Como os diferentes gêneros se comportam em relação a esses atributos?

## Perguntas Respondidas
* Quais atributos de áudio (energia, dançabilidade, BPM) são mais comuns nas músicas populares?
* A "Guerra do Volume" (Loudness War) existe nas paradas de sucesso?
* É possível prever se uma música será um "Hit" com base em suas características acústicas?

## Fontes de Dados
* Spotify Tracks Dataset: Um conjunto de dados com mais de 114 mil faixas contendo as informações vitais de áudio extraídas diretamente da API oficial do Spotify (Energy, Danceability, Valence, Tempo, Loudness, Acousticness).

## Metodologia e Arquitetura
1. Coleta de Dados: Classe Python utilizando pandas para download e processamento do arquivo CSV bruto a partir de uma fonte remota.
2. Armazenamento e Modelagem (SQL): Criação de um banco de dados relacional local em SQLite com três tabelas conectadas (artistas, faixas, atributos_audio).
3. Qualidade de Dados (ETL): Tratamento de valores nulos (dados corrompidos) e injeção de dados usando SQLAlchemy no banco.
4. Machine Learning: Uso do algoritmo preditivo RandomForestClassifier para determinar quais características de áudio são mais decisivas para o sucesso de uma faixa.
5. Limpeza e Agrupamento de Gêneros: Classe Python executando atualizações SQL para consolidar micro-gêneros redundantes (como chicago-house, detroit-techno, latino, reggaeton, children) em macro-gêneros mais consistentes (techno/house, latin, kids).
6. Dashboard Interativo (Web App): Aplicação web estruturada em POO com Streamlit e Plotly sob um visual gamer escuro com realces neon verde e azul. A navegação proeminente permite alternar entre o Relatório Mundial, o Relatório Nacional e o Laboratório de Exploração.

## Principais Insights do Mercado Musical
1. O DNA Sonoro por Gênero: Gêneros urbanos (Hip-hop e Funk) lideram em dançabilidade, enquanto gêneros instrumentais/orgânicos (Sertanejo e Rock) dependem mais da energia e intensidade.
2. Mega Hits são Upbeat: Músicas comuns mantêm dançabilidade em 0.55, enquanto Mega Hits (popularidade acima de 70) saltam para 0.65 de dançabilidade e 0.66 de energia, revelando a forte preferência das massas por faixas animadas.
3. A Dançabilidade é Rei: O modelo de IA provou que a Dançabilidade (groove e cadência) é a variável com maior peso de importância técnica para prever se uma canção se tornará um sucesso.
4. A Guerra do Volume (Loudness War): Hits de sucesso possuem volume médio de -6.7 dB, significativamente mais alto do que faixas comuns (-8.5 dB), comprovando que masterizações mais barulhentas capturam a atenção imediata do ouvinte.
5. A Morte do Acústico no Mainstream: O índice de som acústico despenca de 0.33 em músicas comuns para apenas 0.22 em músicas de sucesso, consolidando o domínio de produções sintetizadas digitais.
6. O Nicho da Tristeza Pop: Músicas melancólicas (baixo índice de alegria/valência) encontram barreira para estourar, a menos que sigam o canal estratégico de gêneros com público receptivo a isso, como Alt-Rock e Indie-Pop.
7. Artistas de Elite e Catálogo (O Efeito Bad Bunny): A consistência de alguns artistas de ponta, como Bad Bunny (média de popularidade de 85.3 com 22 faixas), demonstra que o próprio algoritmo do Spotify age como catalisador de entrega contínua para catálogos consolidados.

## O Relatório Nacional de Insights
A segunda aba do dashboard é inteiramente dedicada ao cenário da música brasileira, trazendo uma análise com 3 insights focados nos gêneros nacionais (Sertanejo, Funk, Forró, Samba, Pagode e MPB):
* DNA Sonoro da Música Brasileira: Gráfico comparando dançabilidade, energia e nível acústico, demonstrando o apelo sintetizado e físico de Funk e Forró contra o caráter orgânico e instrumental do Samba, Pagode e MPB.
* A Velocidade e Pulsação do Ritmo (BPM): Gráfico de Boxplot comparando a velocidade em BPM, ilustrando o dinamismo e rapidez acelerada do Forró e do Funk contra o andamento moderado e relaxante da MPB e do Samba.
* Tração Comercial e Popularidade Média: Gráfico de barras horizontais demonstrando a aceitação média de cada gênero nacional nas playlists, destacando a liderança comercial do Sertanejo e do Funk no streaming.

## O Laboratório de Exploração Interativo
O projeto conta com um Laboratório Analítico dinâmico para que o usuário execute suas próprias investigações nos dados musicais do Spotify. Nele, é possível:
* Selecionar múltiplos gêneros específicos para comparação através de um menu de seleção.
* Ajustar uma barra de rolagem (slider) para delimitar o intervalo de popularidade desejado.
* Atualizar de forma automática e simultânea as seguintes 8 visualizações em tempo real:
  1. Distribuição: Energia vs Dançabilidade (Dispersão que separa hits de músicas comuns).
  2. Comparativo Sonoro por Gênero Selecionado (Barras agrupadas com médias de dançabilidade, energia e acústica).
  3. Ritmo e Intensidade: Hits vs Comuns (Comparação de médias de ritmo).
  4. Distribuição do Volume das Faixas (Boxplot demonstrando variação de decibéis).
  5. Índice de Acústica Médio: Hits vs Comuns (Gráfico de colunas medindo o nível de instrumentação orgânica).
  6. Distribuição de Alegria (Valência) das Faixas (Violin plot mostrando a distribuição da positividade musical).
  7. Gêneros por Volume de Hits Melancólicos (Gráfico de barras com quantidade de faixas tristes de sucesso).
  8. Top 10 Artistas por Popularidade Média (Ranking de consistência comercial dos artistas).

## Demonstração Visual do Dashboard
Abaixo estão as capturas de tela do aplicativo web interativo funcionando com o tema visual gamer:

### Relatório de Insights de Mercado
![Relatório de Insights](dashboard/print_relatorio.png)

### Laboratório de Exploração Interativo
![Laboratório de Exploração](dashboard/print_laboratorio.png)

## Como Rodar o Projeto Localmente
1. Clone este repositório no seu computador.
2. Instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```
3. Processamento de Dados (Execute apenas 1 vez para criar e limpar o banco local):
   * `python src/02_download_dataset.py` (Realiza o download dos dados brutos de forma automática)
   * `python src/03_carregar_banco.py` (Cria a modelagem relacional no SQLite e popula as tabelas)
   * `python src/09_limpeza_generos.py` (Executa o agrupamento de micro-gêneros redundantes no banco de dados)
4. Inicie o Servidor do Dashboard Interativo:
   ```bash
   streamlit run src/08_dashboard_interativo.py
   ```
5. O aplicativo web abrirá automaticamente no seu navegador no endereço `http://localhost:8501`.
