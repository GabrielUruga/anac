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

class DDL:
    @staticmethod
    def create_bigquery_dataset(project_name : str, dataset_name:str, dataset_location:str):
                  
        # Definindo o nome do dataset
        dataset_id = f"{project_name}.{dataset_name}"

        # Definindo instância do Dataset 
        dataset = bigquery.Dataset(dataset_id)

        # Definindo local de armazenamento do Dataset no Google Cloud
        dataset.location = dataset_location
        
        try:
            # Verificando se o dataset já existe no projeto 
            BigQueryClient.get_dataset(dataset_name)
            
            # Mensagem para log de sucesso
            message = f'O dataset `{dataset_name}` já existe no projeto`{project_name}`'
            logging.info(message)

            return dataset_name
        
        except exceptions.NotFound:
            # Mensagem para log de sucesso
            message = f'O dataset {dataset_name} não existe no projeto `{project_name}` e será criado'
            logging.info(message)
            
            try:
                # Instanciando função para criar dataset no projeto do BigQuery
                create_bigquery_dataset = BigQueryClient.create_dataset(dataset, timeout = 30)
                
                # Mensagem para log de sucesso
                message = f'Dataset `{dataset_name}` criado com sucesso no projeto `{project_name}`' 
                logging.info(message)

                return dataset_name

            except Exception as e:
                # Mensagem para log de erro
                message = f'Erro ao executar criação do dataset `{dataset_name}` no projeto `{project_name}`'
                logging.error(message, exc_info = True)

    @staticmethod
    def delete_bigquery_dataset(project_name:str, dataset_name:str):
        try:
            # Verificando se o dataset existe no projeto 
            BigQueryClient.get_dataset(dataset_name)
            
            # Mensagem para log caso o dataset não exista no projeto
            message = f'Não foi possível deletar o dataset `{dataset_name}`, pois o dataset não existe no projeto`{project_name}`'
            logging.info(message)
            
        except exceptions.NotFound:
            message = f'O dataset `{dataset_name}` existe no projeto `{project_name}` e será deletado'
            logging.info(message)

            try:
                # Requisição no Projeto GCP para deletar Dataset e todo seu conteúdo
                BigQueryClient.delete_dataset(dataset=dataset_name, delete_contents=True)

                # Mensagem de Sucesso após deleção com sucesso do Dataset definido 
                message = f'Dataset `{dataset_name}` deletado com sucesso do projeto `{project_name}`' 
                logging.info(message)
            
            except Exception as e:
                # Mensagem para log de erro
                message = f'Erro ao deletar o dataset `{dataset_name}` do projeto `{project_name}`'
                logging.error(message, exc_info=True)
        
    @staticmethod
    def create_bigquery_table_by_json(project_name:str, dataset_name:str, url:str, json_file:str):
        """
            Método para criar tabela no BigQuery, em dataset e projeto definidos, através de um arquivo JSON
        """
        # Importando dependências
        from urllib.parse import urlparse, unquote
        from pathlib import PurePosixPath
        import re
        
        # definindo a URL em que o arquivo JSON será extraído
        json_url = url

        # Extraindo o Path da URL  
        json_path = PurePosixPath(urlparse(json_url).path)
        
        # Extraindo apenas nome do Path da URL removendo espaços e caracteres especiais
        json_path_name = re.sub(r"\W+", "", unquote(json_path.stem))

        # Definindo o nome do Path da URL como nome da tabela
        table_name = f'{project_name}.{dataset_name}.{json_path_name}'

        try:
            # Verificando se tabela já existe
            BigQueryClient.get_table(table_name)

            # Mensagem para log de tabela já existente
            message = f'A tabela `{table_name}` não será criada, pois a tabela já existe'
            logging.info(message)
            
            # Retornando nome da tabela, caso ela já exsita
            return table_name
        # Excessão para criar tabela, caso ela não exista
        except exceptions.NotFound:     
            # Transformar a string decodificada em um dicionário/lista Python
            json_data = json_file

            # Extraindo as chaves do JSON para utilizar como nome no Schema da tabela
            keys = json_data[0].keys()          

            # Definindo chaves extraídas do JSON como campos no schema da tabela
            schema = [bigquery.SchemaField(f"{key}", "STRING", mode="NULLABLE") for key in keys] 

            # Definindo variável com nome e schema da tabela que será criada no BigQuery
            table = bigquery.Table(table_name, schema=schema,)

            # Requisição para criar tabela definida
            create_table = BigQueryClient.create_table(table=table)
            
            # Bloco Try/Catch para enviar a Requisição para criação da tabela no BigQuery
            try:
                create_table
                
                # Mensagem para log de sucesso
                message = f'Tabela `{table_name}` criada com sucesso'
                logging.info(message)
                
                return table_name
                
            except Exception:
                # Mensagem para log de erro 
                message = f'Erro ao criar tabela `{table_name}`'
                logging.error(message, exc_info=True)