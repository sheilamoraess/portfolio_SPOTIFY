import sqlite3
import pandas as pd
import os

class AnalistaSQL:
    """
    Classe responsável por se conectar ao banco de dados e rodar nossas consultas SQL
    para exibir os resultados na tela.
    """
    def __init__(self, db_path='spotify_brasil.db'):
        self.db_path = db_path
        
    def executar_analises(self, arquivo_sql):
        print(f"Iniciando a análise dos dados usando '{arquivo_sql}'...\n")
        
        # Lê o arquivo que tem as consultas SQL
        with open(arquivo_sql, 'r', encoding='utf-8') as f:
            script_sql = f.read()
            
        # O arquivo tem duas consultas separadas por ponto e vírgula ";"
        consultas = script_sql.split(';')
        
        # Conecta no banco
        with sqlite3.connect(self.db_path) as conn:
            
            # --- Roda a Consulta 1 ---
            print("==================================================")
            print(" ANÁLISE 1: DNA SONORO DOS GÊNEROS (Mais dançantes)")
            print("==================================================")
            # Usa o pandas (read_sql) para enviar o SQL para o banco e trazer como tabela
            df_generos = pd.read_sql(consultas[0].strip() + ";", conn)
            print(df_generos.to_string(index=False)) # Imprime a tabela bonita
            
            print("\n")
            
            # --- Roda a Consulta 2 ---
            print("==================================================")
            print(" ANÁLISE 2: O SEGREDO DO HIT (Mais populares = mais animadas?)")
            print("==================================================")
            df_hits = pd.read_sql(consultas[1].strip() + ";", conn)
            print(df_hits.to_string(index=False))
            print("==================================================")

if __name__ == "__main__":
    analista = AnalistaSQL()
    analista.executar_analises(r"sql\analytics.sql")
