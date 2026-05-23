import sqlite3
import pandas as pd

conn = sqlite3.connect('spotify_brasil.db')

print("=== TABELAS NO BANCO ===")
tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(tabelas.to_string(index=False))

print("\n=== AMOSTRA DOS DADOS COMPLETOS ===")
query = """
SELECT f.nome, art.nome AS artista, f.genero, f.popularidade,
       a.danceability, a.energy, a.valence, a.tempo, a.loudness, a.acousticness
FROM faixas f
JOIN atributos_audio a ON f.id = a.faixa_id
JOIN artistas art ON f.artista_id = art.id
LIMIT 5
"""
df = pd.read_sql(query, conn)
print(df.to_string())

print("\n=== TOP 20 GENEROS POR QUANTIDADE ===")
gen = pd.read_sql("""
    SELECT genero, COUNT(*) as total FROM faixas
    WHERE genero IS NOT NULL
    GROUP BY genero ORDER BY total DESC LIMIT 20
""", conn)
print(gen.to_string(index=False))

print("\n=== ESTATISTICAS DE POPULARIDADE ===")
stats = pd.read_sql("""
    SELECT 
        MIN(popularidade) as minimo,
        MAX(popularidade) as maximo,
        ROUND(AVG(popularidade), 1) as media
    FROM faixas
""", conn)
print(stats.to_string(index=False))
