import requests
import json

## Login para Sessao
# Define os parâmetros para a requisição de login
host = 'https://0.0.0.0:9910'
url_login = f'{host}/Login'
dados_login = {
    'usuario': 'usuario',
    'senha': 'senha',
    'identificador': 'identificador'
}

# Realiza a requisição de login
try:
    response_login = requests.post(url_login, data=dados_login, verify=False)
    print('Login realizado com sucesso')
    print(response_login.json())
except:
    print(response_login.json())

sessao = response_login.json().get('sessao')
id_usuario = response_login.json().get('id_usuario')

## Funcao Requisicao
# Define a função requisição para requisitar os dados em rotas listadas
def requisicao(rota):
    url_clientes = f'{host}/{rota}'
    dados_req = {
        'sessao': sessao,
        'idUsuario': id_usuario,
        'identificador': 'identificador'
    }
    # Realiza a requisição para obter clientes
    response = requests.post(url_clientes, data=dados_req, verify=False)
    
    try:
        dados = response.json()['dados']
        dados_acum = []
        dados_acum.extend(dados)
    
        if response.status_code == 200:
            print(f'Rota: {rota} repondida com sucesso')

            # Caminho onde o arquivo JSON será salvo
            caminho_completo = f'C:/Users/Weslley/OneDrive/Área de Trabalho/Projetos/dTel/Dados/{rota}.json'

            # Salva a resposta em um arquivo JSON
            with open(caminho_completo, 'w') as arquivo:
                json.dump(dados_acum, arquivo)

            print(f'Arquivo salvo em: {caminho_completo}')
        else:
            print(f'Erro ao traçar rota: {rota}', response.status_code)
    except:
        print(response.status_code)
        print(f'Rota: {rota} concluída.')

# Lista de rotas a serem requisitadas
rotas = ['ObterClientesServicos', 'ObterClientes', 'ObterContratos', 'Logout']
for i in rotas:
    requisicao(i)
