import pandas as pd
import mysql.connector
from time import sleep

# Dados do banco e credenciais de acesso
dados = {
    'nomeBancos': ['Teste'],
    'usuarios': ['teste'],
    'senhas': ['teste'],
    'host': ['ixc.teste.com.br']
}

query_consulta_termos = """
                    SELECT 
                        ccat.id,
                        cc.id idContrato,
                        ccat.id_termo idTermo,
                        ccat.ativar_contrato ativaContrato
                    FROM 
                        cliente_contrato_assinatura_termo ccat
                        LEFT JOIN cliente_contrato cc ON cc.id = ccat.id_contrato
                    WHERE
                        cc.status = 'P'
                        AND data_cadastro_sistema = CURRENT_DATE()"""

def executa_update(id_contrato):
    executa_atualizacao = f"""
                        UPDATE 
                            cliente_contrato_assinatura_termo ccat
                            LEFT JOIN cliente_contrato cc ON cc.id = ccat.id_contrato
                        SET ativar_contrato = CASE WHEN ccat.id_termo = '128' THEN 'S' ELSE 'N' END
                        WHERE
                            cc.id = '{id_contrato}'
                            AND cc.status = 'P'
                            AND data_cadastro_sistema = CURRENT_DATE()""" 
    return executa_atualizacao

# Função de conexão ao banco
def conectar_banco(host, usuario, senha, banco='ixcprovedor'):
    """
    Função que define a conexão com o banco.
    Retorna a conexão estabelecida.
    """
    return mysql.connector.connect(
        host=host,
        user=usuario,
        password=senha,
        database=banco
    )

# Função de execução no banco
def executar_query_em_bancos(query):
    """
    Função que executa uma query sobre os bancos de dados das empresas.
    Retorna um DataFrame consolidado com os resultados de todos os bancos.
    """
    # Lista para armazenar cada DataFrame
    dataframes = []

    # Itera sobre as credenciais dos bancos
    for i in range(len(dados['nomeBancos'])):
        host = dados['host'][i]
        usuario = dados['usuarios'][i]
        senha = dados['senhas'][i]

        # Gerencia a conexão com o banco de dados
        with conectar_banco(host, usuario, senha) as conn:
            df = pd.read_sql_query(query, conn)
            df['nomeBanco'] = dados['nomeBancos'][i]
            dataframes.append(df)

    # Concatena todos os DataFrames de uma vez
    return pd.concat(dataframes, ignore_index=True)

tabela_termos = executar_query_em_bancos(query_consulta_termos)

for id in tabela_termos['idContrato'].unique():
    instrucao_update = executa_update(id)
    with conectar_banco(dados['host'][0], dados['usuarios'][0], dados['senhas'][0]) as conn:
        with conn.cursor() as cursor:
            cursor.execute(instrucao_update)
        conn.commit()  # Assegura que a alteração seja salva no banco
        
