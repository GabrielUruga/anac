# Importando dependências
from dotenv import load_dotenv
from os import getenv
import yaml
from utils_dev import JSON, DDL, DML, GCS

# Carregando variáveis de ambiente
load_dotenv()

# Definindo YAML em variáveis
yaml_path = getenv('YAML_PATH')
yaml_name = getenv('YAML_NAME')

# Leitura de arquivo YAML para recuperar parâmetros
with open(yaml_path, 'r') as file:
    bigquery_params = yaml.safe_load(file)

# Transformando parâmetros em Dicionário Python
config = {k: v for d in bigquery_params[yaml_name] for k, v in d.items()}

# Armazenando os parâmetros recuperados em variáveis 
bigquery_project = config.get('project-name')
bigquery_dataset = config.get('dataset-name')
bigquery_dataset_location = config.get('dataset-location')
url_link = config.get('url')
folder_path = config.get('folder-path')