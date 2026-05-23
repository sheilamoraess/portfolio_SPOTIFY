import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyExtractor:
    """
    Classe responsável por conectar na API do Spotify e extrair dados.
    """
    
    def __init__(self):
        load_dotenv()
        self.auth_manager = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        
    def buscar_musica_por_nome(self, nome_pesquisa):
        """
        Recebe o nome de uma música, pesquisa na API e retorna os atributos.
        """
        try:
            # 1. Faz uma pesquisa genérica (search) para encontrar a música
            resultados = self.sp.search(q=nome_pesquisa, type='track', limit=1)
            
            if not resultados['tracks']['items']:
                print("Nenhuma música encontrada com esse nome.")
                return None
                
            # 2. Pega a primeira música que apareceu no resultado
            track_info = resultados['tracks']['items'][0]
            nome_musica = track_info['name']
            artista = track_info['artists'][0]['name']
            track_id = track_info['id']
            
            # 3. Busca os atributos de áudio pelo ID dessa música
            audio_features = self.sp.audio_features(track_id)[0]
            
            # 4. Organiza os resultados
            dados = {
                'nome': nome_musica,
                'artista': artista,
                'energia': audio_features['energy'],
                'dancabilidade': audio_features['danceability'],
                'valencia': audio_features['valence'],
                'bpm': audio_features['tempo']
            }
            
            return dados
            
        except Exception as e:
            print(f"Ocorreu um erro na extração: {e}")
            return None


if __name__ == "__main__":
    print("Iniciando conexão com o Spotify (Modelo POO)...\n")
    
    extrator = SpotifyExtractor()
    
    # Em vez de um link aleatório que pode dar erro de URL, vamos pesquisar pelo nome
    pesquisa = 'Evidências Chitãozinho'
    resultado = extrator.buscar_musica_por_nome(pesquisa)
    
    if resultado:
        print(f"Sucesso! Conectado.")
        print(f"Música encontrada: {resultado['nome']} | Artista: {resultado['artista']}")
        print("\n--- Atributos de Áudio ---")
        print(f"Energia (0 a 1): {resultado['energia']}")
        print(f"Dançabilidade (0 a 1): {resultado['dancabilidade']}")
        print(f"Valência ou Alegria (0 a 1): {resultado['valencia']}")
        print(f"BPM ou Tempo: {resultado['bpm']}")
