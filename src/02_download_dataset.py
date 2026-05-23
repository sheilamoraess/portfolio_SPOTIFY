import pandas as pd
import os

class DownloaderDataset:
    """
    Classe responsável por realizar o download do dataset de faixas do Spotify
    a partir de uma fonte remota do HuggingFace e salvá-lo localmente.
    """
    def __init__(self, url="https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset/resolve/main/dataset.csv",
                 caminho_salvar=os.path.join("data", "raw", "spotify_tracks.csv")):
        self.url = url
        self.caminho_salvar = caminho_salvar
        
    def executar_download(self):
        print("Iniciando o download do dataset...")
        print(f"Fonte remota: {self.url}")
        print("Isso pode demorar um ou dois minutos devido ao volume de dados (114 mil faixas)...\n")
        
        try:
            # O pandas lê os dados diretamente da URL fornecida
            df = pd.read_csv(self.url)
            
            # Garante que a pasta destino existe no ambiente local
            pasta_destino = os.path.dirname(self.caminho_salvar)
            if pasta_destino and not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)
                
            # Salva o arquivo localmente em formato CSV
            df.to_csv(self.caminho_salvar, index=False)
            
            print(f"Sucesso! Dataset salvo em: {self.caminho_salvar}")
            print(f"Total de músicas baixadas: {df.shape[0]}")
            print(f"Total de colunas (atributos): {df.shape[1]}")
            print("\nAlgumas das colunas extraídas:")
            print(list(df.columns[:10]))
            
        except Exception as e:
            print(f"Ocorreu um erro durante o processamento do download: {e}")

if __name__ == "__main__":
    downloader = DownloaderDataset()
    downloader.executar_download()
