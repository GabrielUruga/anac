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