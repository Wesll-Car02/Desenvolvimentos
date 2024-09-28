# ------------------------------------------------ #
# Código criado por Weslley Carvalho               #
# Objetivo: Este script é destinado a automatizar  #
# a extração dos dados da ALEL.                    #
# ------------------------------------------------ #
import os
import requests
import mysql.connector  # pip install mysql-connector-python
from mysql.connector import Error
import json

# Define os parâmetros para a requisição de login
host = 'https://0.0.0.0:8080'
url_login = f'{host}/Login'
dados_login = {
    'usuario': 'user',
    'senha': 'senha',
    'identificador': 'identifcador'
}

# Realiza a requisição de login
try:
    response_login = requests.post(url_login, data=dados_login, verify=False)
    print('Login realizado com sucesso')
    print(response_login.json())
except Exception as e:
    print(f'Erro ao realizar login: {e}')
    exit()

sessao = response_login.json().get('sessao')
id_usuario = response_login.json().get('id_usuario')

# Função para analisar os dados JSON e retornar as colunas e tipos de dados
def analyze_json(data):
    first_record = data[0]
    columns = {}
    for key, value in first_record.items():
        if isinstance(value, int):
            columns[key] = 'INT'
        elif isinstance(value, float):
            columns[key] = 'FLOAT'
        elif isinstance(value, str):
            max_length = max(len(str(record.get(key, ""))) for record in data)
            if max_length < 1:
                max_length = 1  # Garantir comprimento mínimo de 1
            if max_length > 255:
                columns[key] = 'TEXT'
            else:
                columns[key] = f'VARCHAR({max_length})'
        elif isinstance(value, bool):
            columns[key] = 'BOOLEAN'
        elif isinstance(value, dict) or isinstance(value, list):
            columns[key] = 'JSON'
        else:
            columns[key] = 'TEXT'  # Tipo padrão

    return columns, data

# Função para criar a tabela dinamicamente
def create_table(table_name, columns, cur):
    column_defs = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});"
    print(f"Creating table with query: {create_table_query}")  # Debugging line
    cur.execute(create_table_query)

# Função para tratar valores vazios e nulos e converter dict/list para JSON string
def clean_data(record, columns):
    cleaned_record = []
    for col in columns:
        value = record.get(col, None)
        if value == "" and columns[col] in ['INT', 'FLOAT']:
            cleaned_record.append(None)
        elif isinstance(value, (dict, list)):
            cleaned_record.append(json.dumps(value))  # Convert dict/list to JSON string
        else:
            cleaned_record.append(value)
    return cleaned_record

# Função para inserir os dados na tabela
def insert_data(table_name, data, columns, cur):
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns.keys())
    insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    for record in data:
        cleaned_record = clean_data(record, columns)
        cur.execute(insert_query, cleaned_record)

# Função para requisitar dados e inserir no banco de dados
def requisicao_e_inserir(rota, conn, cur):
    url = f'{host}/{rota}'
    dados_req = {
        'sessao': sessao,
        'idUsuario': id_usuario,
        'identificador': 'identficador'
    }

    # Realiza a requisição para obter os dados
    response = requests.post(url, data=dados_req, verify=False)
    
    try:
        dados = response.json()['dados']
        
        if response.status_code == 200:
            print(f'Rota: {rota} respondida com sucesso')
            
            # Analisar os dados e obter colunas e tipos
            columns, data = analyze_json(dados)
            
            # Criar tabela dinamicamente
            table_name = rota.lower()
            create_table(table_name, columns, cur)
            
            # Limpar a tabela (opcional)
            cur.execute(f"DELETE FROM {table_name};")
            
            # Inserir os dados
            insert_data(table_name, data, columns, cur)
            
            print(f'Dados da rota {rota} inseridos com sucesso no banco de dados')
        else:
            print(f'Erro ao requisitar rota: {rota}', response.status_code)
    except Exception as e:
        print(f'Erro ao processar dados da rota: {rota} - {e}')
        conn.rollback()  # Rollback em caso de erro para garantir que a transação atual seja encerrada

# Conexão com o MariaDB
try:
    conn = mysql.connector.connect(
        host='localhost',
        database='xxx',
        user='user',
        password='password'
    )
    if conn.is_connected():
        print('Conexão com o MariaDB estabelecida com sucesso')
    
    cur = conn.cursor()

    # Lista de rotas a serem requisitadas
    rotas = ['ObterVendedores', 'ObterSuporte', 'ObterClientesServicos', 'ObterClientes']

    # Requisitar dados e inserir no banco de dados para cada rota
    for rota in rotas:
        requisicao_e_inserir(rota, conn, cur)
        # verificar_dados(rota.lower(), cur)  # Verificar os dados inseridos

    # Commit e fechamento da conexão
    conn.commit()
    cur.close()
    conn.close()

    print("Dados importados com sucesso!")

except Error as e:
    print(f'Erro ao conectar ao MariaDB: {e}')
