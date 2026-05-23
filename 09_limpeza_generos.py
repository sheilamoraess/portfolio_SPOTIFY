import sqlite3

class LimpadorGeneros:
    """
    Classe responsável por consolidar e agrupar micro-gêneros dispersos no banco de dados SQLite.
    """
    def __init__(self, db_path='spotify_brasil.db'):
        self.db_path = db_path
        self.mapeamento = {
            'chicago-house': 'techno/house',
            'deep-house': 'techno/house',
            'detroit-techno': 'techno/house',
            'minimal-techno': 'techno/house',
            'latino': 'latin',
            'reggaeton': 'latin',
            'children': 'kids'
        }
        
    def executar_limpeza(self):
        print("Iniciando o agrupamento de macro-gêneros no banco de dados...")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for antigo, novo in self.mapeamento.items():
                    cursor.execute("UPDATE faixas SET genero = ? WHERE genero = ?", (novo, antigo))
                    print(f"[{antigo}] --> agrupado dentro de [{novo}]")
                conn.commit()
            print("\nLimpeza finalizada! Banco de dados atualizado permanentemente.")
        except Exception as e:
            print(f"Ocorreu um erro ao atualizar os gêneros no banco: {e}")

if __name__ == "__main__":
    limpador = LimpadorGeneros()
    limpador.executar_limpeza()
