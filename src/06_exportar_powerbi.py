import pandas as pd
import sqlite3
import os

class PowerBIExport:
    """
    Classe para consultar os dados finais no SQLite e exportá-los 
    para CSVs limpos na pasta data/processed, prontos para o Power BI.
    """
    def __init__(self, db_path='spotify_brasil.db'):
        self.db_path = db_path
        self.pasta_destino = os.path.join('data', 'processed')
        
        # Garante que a pasta existe
        if not os.path.exists(self.pasta_destino):
            os.makedirs(self.pasta_destino)
            
    def exportar_csvs(self):
        print(f"Conectando ao banco de dados '{self.db_path}'...")
        
        with sqlite3.connect(self.db_path) as conn:
            
            # Tabela 1: DNA Sonoro por Gênero (Para gráficos de barras agregados)
            print("Exportando 'dna_generos.csv'...")
            query1 = '''
            SELECT 
                f.genero,
                ROUND(AVG(a.danceability), 3) AS media_dancabilidade,
                ROUND(AVG(a.energy), 3) AS media_energia,
                ROUND(AVG(a.valence), 3) AS media_alegria,
                ROUND(AVG(a.tempo), 1) AS bpm_medio,
                COUNT(f.id) AS total_musicas
            FROM faixas f
            JOIN atributos_audio a ON f.id = a.faixa_id
            WHERE f.genero IS NOT NULL
            GROUP BY f.genero
            HAVING total_musicas > 50
            '''
            df1 = pd.read_sql(query1, conn)
            df1.to_csv(os.path.join(self.pasta_destino, 'dna_generos.csv'), index=False)
            
            # Tabela 2: Tabela Principal (Para o Scatter Plot e cruzar atributos)
            print("Exportando 'todas_faixas_powerbi.csv'...")
            query2 = '''
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
                CASE 
                    WHEN f.popularidade >= 70 THEN 'Hit'
                    ELSE 'Normal'
                END AS status_hit
            FROM faixas f
            JOIN atributos_audio a ON f.id = a.faixa_id
            JOIN artistas art ON f.artista_id = art.id
            '''
            df2 = pd.read_sql(query2, conn)
            df2.to_csv(os.path.join(self.pasta_destino, 'todas_faixas_powerbi.csv'), index=False)
            
            # Tabela 3: Top Artistas (Para os cartões de KPI)
            print("Exportando 'top_artistas.csv'...")
            query3 = '''
            SELECT 
                art.nome AS artista,
                COUNT(f.id) AS total_musicas,
                ROUND(AVG(f.popularidade), 1) AS popularidade_media
            FROM artistas art
            JOIN faixas f ON art.id = f.artista_id
            GROUP BY art.id
            HAVING total_musicas > 5
            ORDER BY popularidade_media DESC
            '''
            df3 = pd.read_sql(query3, conn)
            df3.to_csv(os.path.join(self.pasta_destino, 'top_artistas.csv'), index=False)
            
        print("\nSucesso! Todos os arquivos CSV para o Power BI foram gerados na pasta 'data/processed/'.")

if __name__ == "__main__":
    exportador = PowerBIExport()
    exportador.exportar_csvs()
