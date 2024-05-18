# importação das bibliotecas
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Definição da função extrair_dados_acao a qual fará request no site fundamentus e retornará o HTML do site da respectiva ação
def extrair_dados_acao(acao):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(f'https://fundamentus.com.br/detalhes.php?papel={acao}', headers=headers)
    
    if response.status_code == 200:
        site = BeautifulSoup(response.content, 'html.parser')
        conteudo_geral = site.find('div', attrs={'class': 'conteudo clearfix'})
        spans = conteudo_geral.find_all('span', class_=['txt', 'oscil'])
        dados_extraidos = [span.get_text(strip=True) for span in spans]

        # Converte a lista de dados extraídos em um dicionário de pares chave-valor
        data_dict = {}
        for i in range(0, len(dados_extraidos), 2):
            chave = dados_extraidos[i]
            valor = dados_extraidos[i + 1] if i + 1 < len(dados_extraidos) else ''

            # Interrompe o loop se encontrar a chave específica
            if chave == 'Dados Balanço Patrimonial':
                break
            
            # Adiciona ao dicinario cada/valor
            data_dict[chave] = valor

        # Adiciona a data hora da requisicao
        data_dict['Data hora req.'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return data_dict
    else:
        print(f"Failed to retrieve page for {acao}. Status code: {response.status_code}")
        return None

# Definição da função main
def main():
    acoes = ['VALE3', 'PETR4', 'ITUB4', 'BBAS3']  # Adicione mais ações conforme necessário
    dataframes = []

    for acao in acoes:
        dados_acao = extrair_dados_acao(acao)
        if dados_acao:
            # Cria um DataFrame a partir do dicionário
            dataframes.append(pd.DataFrame([dados_acao]))

    if dataframes:
        df_final = pd.concat(dataframes, ignore_index=True)
        
        # Exibe o DataFrame
        display(df_final)
    else:
        print("Nenhum dado foi extraído.")

if __name__ == "__main__":
    main()
