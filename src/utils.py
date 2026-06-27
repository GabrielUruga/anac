# Importação de dependências
from dotenv import load_dotenv
from os import getenv
import logging
from google.cloud import bigquery, exceptions, storage

# Carregando variáveis de ambiente para recuperar arquivo de Logs
load_dotenv()

# Recuperando o Path do para realização de Logs
logs = getenv('LOGS')

# Configuração de Logs de Execução
logging.basicConfig(
    level=logging.DEBUG, # Define o nível mínimo
    filename= logs,
    encoding='utf-8',
    filemode='w',        # 'a' adiciona ao arquivo, 'w' sobrescreve
    format='{asctime} [{levelname}] {filename}:{lineno} - {message}',
    style='{'
)

# Instaciando o Clients do BigQuery e Storage para execução dos métodos que necessitam de Autenticação do GCP
BigQueryClient = bigquery.Client()
StorageClient = storage.Client()

class JSON:
    @staticmethod
    def extract_data_from_json_url(url:str):
        # Importando dependências
        import requests
        import json
        import warnings

        warnings.filterwarnings("ignore")
        try:
            # definindo a URL em que o arquivo JSON será extraído
            json_url = url
            
            # Envio de Requisição na URL definida
            response = requests.get(json_url, verify=False)
            
            # Decodificação (O arquivo foi salvo com BOM, que indica a Ordem dos bytes, se for feita utilizando apenas p utf=8, é retornado um erro)
            content = response.content.decode('utf-8-sig')

            # Transformar a string decodificada em um dicionário/lista Python
            json_data = json.loads(content)
            
            if not json_data:
                message = f'O arquivo JSON extraído não possui registros'
                logging.error(message, exc_info=True)
            else:
                # Contabilizando itens presentes no JSON
                total_itens = len(json_data)
                
                # Mensagem para log de sucesso
                message = f'{total_itens} itens extraídos do JSON com sucesso via requisição na URL "{url}"' 
                logging.info(message)
                
                return json_data

        except Exception:
            # Mensagem para log de erro
            message = f'Falha ao enviar requisição na URL "{url}"'
            logging.error(message, exc_info=True)

    @staticmethod
    def extract_json_url_from_subfolder(url:str):
        # Importação de dependências
        import requests
        from bs4 import BeautifulSoup
        
        try:
            # Definindo sessão única para conexão com servidor 
            with requests.Session() as session:
                message = f'A sessão foi iniciada em {url}'
                logging.info(message)

                # Extraindo a link das Subpastas
                response = session.get(url)
                soup_folder = BeautifulSoup(response.text, 'html.parser')
                
                # Extraindo as referência das subpastas da pasta da URL
                subfolders_links = soup_folder.find_all('a')
                
                # Contagem de referências de Subpastas encontrados
                subfolders_links_count = len(subfolders_links)

                if subfolders_links_count == 0:
                    # Log de erro quando não há subpastas
                    message =  f' Nenhuma subpasta encontrada em :{url}'
                    logging.error(message)

                else:
                    # Extraindo URL dos links das subpastas
                    subfolders_url = [f"{url}{link.get('href')}" for link in subfolders_links if link.get('href').endswith('/') and link.get('href') != '../']
                    
                    # Contagem de URL extraídas das Subpastas encontradas
                    subfolders_url_count = len(subfolders_url)

                    # Log de sucesso na extração das URLs das Subpastas
                    message =  f'{subfolders_url_count} URLs extraídas de Subpastas com sucesso'
                    logging.info(message)

                    # Extraindo o JSON de cada URL das Subpastas 

                    json_url_list = []

                    for subfolder in subfolders_url:
                        response = session.get(subfolder)
                        soup_json = BeautifulSoup(response.text, 'html.parser')

                        json_links = soup_json.find_all('a')

                        json_url =  [f'{subfolder}{link.get('href')}' for link in json_links if link.get('href') and link.get('href').lower().endswith('.json')]

                        json_url_count = len(json_url)

                        if json_url_count == 0:
                            # Log de erro quando não há URLs dos JSONs nas subpastas
                            message =  f' Nenhuma URL de JSON encontrada nas subpastas em :{url}'
                            logging.error(message)
                        else:
                            json_url_list.extend(json_url)

                            message = f'{json_url_count} JSON encontrado nas Subpasta, URL extraída com sucesso'
                            logging.info(message)

                    return json_url_list
        except Exception as e:
            message = f'{e}'
            logging.error(message, exc_info=True)