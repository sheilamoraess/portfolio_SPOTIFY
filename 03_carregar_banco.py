import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import os

class BancoDeDadosSpotify:
    """
    Classe responsável por preparar os dados brutos e alimentá-los no Banco de Dados SQL.
    """
    def __init__(self, db_path='spotify_brasil.db'):
        self.db_path = db_path
        
    def inicializar_tabelas(self, schema_path):
        """Lê o script schema.sql e cria as tabelas em branco."""
        # Se o banco já existir e deu erro antes, nós apagamos para começar do zero!
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        print(f"1. Criando o banco de dados em '{self.db_path}'...")
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, 'r', encoding='utf-8') as f:
                script_sql = f.read()
            conn.executescript(script_sql)
        print("Tabelas SQL criadas com sucesso!")

    def carregar_dados(self, csv_path):
        """Lê o CSV, organiza as tabelas (Artistas, Faixas, Atributos) e envia pro SQLite."""
        print(f"\n2. Lendo os dados brutos de '{csv_path}'...")
        df = pd.read_csv(csv_path)
        
        # Limpeza dos dados: 
        print("Realizando limpeza avançada (removendo duplicatas e valores nulos/vazios)...")
        df = df.drop_duplicates(subset=['track_id'])
        # Aqui está a correção do erro! Algumas músicas vieram sem nome de artista (vazias).
        # Nós excluímos essas linhas problemáticas antes de tentar inserir no banco.
        df = df.dropna(subset=['track_id', 'track_name', 'artists'])
        
        print("\n3. Separando os dados para cada tabela relacional:")
        
        # -- TABELA ARTISTAS --
        artistas_unicos = df[['artists']].drop_duplicates().reset_index(drop=True)
        artistas_unicos['id'] = artistas_unicos.index + 1
        artistas_unicos = artistas_unicos.rename(columns={'artists': 'nome'})
        
        df = df.merge(artistas_unicos, left_on='artists', right_on='nome')
        df = df.rename(columns={'id': 'artista_id'})
        
        # -- TABELA FAIXAS --
        faixas = df[['track_id', 'track_name', 'artista_id', 'popularity', 'track_genre']].copy()
        faixas = faixas.rename(columns={'track_id': 'id', 'track_name': 'nome', 'popularity': 'popularidade', 'track_genre': 'genero'})
        
        # -- TABELA ATRIBUTOS --
        atributos = df[['track_id', 'danceability', 'energy', 'valence', 'tempo', 'acousticness', 'loudness']].copy()
        atributos = atributos.rename(columns={'track_id': 'faixa_id'})
        
        print("\n4. Inserindo no SQLite (isso pode demorar uns 10 segundos)...")
        engine = create_engine(f'sqlite:///{self.db_path}')
        
        artistas_unicos.to_sql('artistas', engine, if_exists='append', index=False)
        print("- Tabela de Artistas carregada!")
        
        faixas.to_sql('faixas', engine, if_exists='append', index=False)
        print("- Tabela de Faixas carregada!")
        
        atributos.to_sql('atributos_audio', engine, if_exists='append', index=False)
        print("- Tabela de Atributos carregada!")
        
        print("\nProcesso concluído com sucesso! Banco populado.")

if __name__ == "__main__":
    schema = os.path.join("sql", "schema.sql")
    csv = os.path.join("data", "raw", "spotify_tracks.csv")
    
    banco = BancoDeDadosSpotify()
    banco.inicializar_tabelas(schema_path=schema)
    banco.carregar_dados(csv_path=csv)
