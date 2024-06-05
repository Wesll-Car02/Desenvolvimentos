import mysql.connector
import pandas as pd
from datetime import date

# Define algumas listas de variaveis para fazer a requisicao
nomeBancos = ['XX']
usuarios = ['XXX']
senhas = ['XXXX']
dbs = ['XXX']
nomedb = 'XXX'

# Conexao com o banco
conn = mysql.connector.connect(
    host=dbs[0],
    user=usuarios[0],
    password=senhas[0],
    database=nomedb
)

# // Editar - ---------------------------
cidade = 1690
diaVencimento = 25
carteiraCobranca = 76   # Carteira de cobrança de interesse

# Obter a data de hoje e formatar como string
dataHoje = date.today().strftime('%Y-%m-%d')

# Query utilizada para requisicao
queryContrato = f"""
            SELECT 
                cc.id,
                cc.id_carteira_cobranca
            FROM cliente_contrato cc
            WHERE cc.id IN
            ( -- Contratos dos títulos a serem ajustados
                SELECT  
                    CASE
                        WHEN fa.id_contrato IS NULL THEN fa.id_contrato_avulso
                        WHEN fa.id_contrato = 0 THEN fa.id_contrato_avulso
                        ELSE fa.id_contrato
                    END id_contrato
                FROM 
                    fn_areceber fa
                    LEFT JOIN cliente_contrato cc ON 
                        (CASE
                            WHEN fa.id_contrato IS NULL THEN fa.id_contrato_avulso
                            WHEN fa.id_contrato = 0 THEN fa.id_contrato_avulso
                            ELSE fa.id_contrato
                        END) = cc.id
                    LEFT JOIN cliente c ON fa.id_cliente = c.id
                    LEFT JOIN cliente_contrato_tipo cct ON cc.id_tipo_contrato = cct.id
                    LEFT JOIN condicoes_pagamento cp ON cp.id = cct.id_condicoes_pagamento
                WHERE 
                    fa.status = 'A' -- Status do título a receber
                    AND (CASE 
                                WHEN cc.cidade IS NULL THEN c.cidade
                                WHEN cc.cidade = 0 THEN c.cidade
                                ELSE cc.cidade
                            END) = {cidade} -- 1690: Joaquim Gomes & 1727: Porto Calvo
                    AND fa.id_carteira_cobranca != {carteiraCobranca} -- Carteira de faturamento diferente de GCP
                    AND cc.status = 'A' -- Status do contrato 
                    AND c.id_tipo_cliente = 4
                    AND cp.dia_fixo = {diaVencimento}
                    AND fa.data_vencimento >= '{dataHoje}')
                AND cc.id_carteira_cobranca != {carteiraCobranca}"""

# Query utilizada para requisicao fn_areceber
queryReceber = f"""
            WITH tabelaContasReceber AS (
                SELECT 
                    fa.id, 
                    CASE
                        WHEN fa.id_contrato IS NULL THEN fa.id_contrato_avulso
                        WHEN fa.id_contrato = 0 THEN fa.id_contrato_avulso
                        ELSE fa.id_contrato
                    END id_contrato,
                    fa.id_cliente,
                    fa.valor_aberto,
                    fa.data_cancelamento,
                    fa.id_mot_cancelamento,
                    fa.valor_cancelado,
                    fa.status,
                    fa.tipo_recebimento,
                    fa.filial_id,
                    CASE 
                        WHEN cc.cidade IS NULL THEN c.cidade
                        WHEN cc.cidade = 0 THEN c.cidade
                        ELSE cc.cidade
                    END id_cidade
                FROM 
                    fn_areceber fa
                    LEFT JOIN cliente_contrato cc ON 
                        (CASE
                            WHEN fa.id_contrato IS NULL THEN fa.id_contrato_avulso
                            WHEN fa.id_contrato = 0 THEN fa.id_contrato_avulso
                            ELSE fa.id_contrato
                        END) = cc.id
                    LEFT JOIN cliente c ON fa.id_cliente = c.id
                    LEFT JOIN cliente_contrato_tipo cct ON cc.id_tipo_contrato = cct.id
                    LEFT JOIN condicoes_pagamento cp ON cp.id = cct.id_condicoes_pagamento
                WHERE 
                    fa.status = 'A' -- Status do título a receber
                    AND (CASE 
                                WHEN cc.cidade IS NULL THEN c.cidade
                                WHEN cc.cidade = 0 THEN c.cidade
                                ELSE cc.cidade
                            END) = {cidade} -- 1690: Joaquim Gomes & 1727: Porto Calvo
                    AND fa.id_carteira_cobranca != {carteiraCobranca} -- Carteira de faturamento diferente de GCP
                    AND cc.status = 'A' -- Status do contrato 
                    AND c.id_tipo_cliente = 4
                    AND cp.dia_fixo = {diaVencimento}
                    AND fa.data_vencimento >= '{dataHoje}'
            ) SELECT * FROM tabelaContasReceber"""

# Faz a requisicao do contrato e contas a receber e fecha a conexão com o banco
df = pd.read_sql_query(queryContrato, conn)
dfr = pd.read_sql_query(queryReceber, conn)
conn.close()

df['update'] = 'UPDATE ixcprovedor.cliente_contrato'
df['set'] = df['id_carteira_cobranca'].apply(lambda x: f'SET id_carteira_cobranca = {x}')
df['where'] = df['id'].apply(lambda x: f'WHERE id = {x}') + ' ;'

# Cria o DataFrame do rollback
rollback_df = df[['id', 'id_carteira_cobranca', 'update', 'set', 'where']]

# Instrução UPDATE para os contratos completa
update_instruction = f"""
            UPDATE cliente_contrato cc
            SET cc.id_carteira_cobranca = {carteiraCobranca}
            WHERE cc.id IN(
                SELECT 
                    CASE
                        WHEN fa.id_contrato IS NULL THEN fa.id_contrato_avulso
                        WHEN fa.id_contrato = 0 THEN fa.id_contrato_avulso
                        ELSE fa.id_contrato
                    END id_contrato
                FROM 
                    fn_areceber fa
                    LEFT JOIN cliente_contrato cc ON 
                        (CASE
                            WHEN fa.id_contrato IS NULL THEN fa.id_contrato_avulso
                            WHEN fa.id_contrato = 0 THEN fa.id_contrato_avulso
                            ELSE fa.id_contrato
                        END) = cc.id
                    LEFT JOIN cliente c ON fa.id_cliente = c.id
                    LEFT JOIN cliente_contrato_tipo cct ON cc.id_tipo_contrato = cct.id
                    LEFT JOIN condicoes_pagamento cp ON cp.id = cct.id_condicoes_pagamento
                WHERE 
                    fa.status = 'A' -- Status do título a receber
                    AND  (CASE 
                                WHEN cc.cidade IS NULL THEN c.cidade
                                WHEN cc.cidade = 0 THEN c.cidade
                                ELSE cc.cidade
                            END) = {cidade} -- 1690: Joaquim Gomes & 1727: Porto Calvo
                    AND fa.id_carteira_cobranca != {carteiraCobranca} -- Carteira de faturamento diferente de GCP
                    AND cc.status = 'A' -- Status do contrato 
                    AND c.id_tipo_cliente = 4
                    AND cp.dia_fixo = {diaVencimento}
                    AND fa.data_vencimento >= '{dataHoje}');"""

# Cria um DataFrame com a instrução UPDATE
update_df = pd.DataFrame({'Update Instruction': [update_instruction]})

dfr['update'] = 'UPDATE ixcprovedor.fn_areceber'
dfr['set'] = 'SET data_cancelamento IS NULL, id_mot_cancelamento IS NULL' + dfr['valor_cancelado'].apply(lambda x: f', valor_cancelado = {x}') + dfr['status'].apply(lambda x: f", status = '{x}'")
dfr['where'] = dfr['id'].apply(lambda x: f'WHERE id = {x}') + ' ;'

# Cria o DataFrame do rollback
rollback_dfr = dfr[['id', 'id_contrato', 'id_cliente', 'valor_aberto', 'data_cancelamento', 'id_mot_cancelamento', 'valor_cancelado',  'status', 'tipo_recebimento', 'filial_id', 'id_cidade', 'update', 'set', 'where']]

# Instrução UPDATE para os contas a receber completa
update_instruction_receber = f"""
            UPDATE fn_areceber fa
                LEFT JOIN cliente_contrato cc ON 
                    (CASE
                        WHEN fa.id_contrato IS NULL THEN fa.id_contrato_avulso
                        WHEN fa.id_contrato = 0 THEN fa.id_contrato_avulso
                        ELSE fa.id_contrato
                    END) = cc.id
                LEFT JOIN cliente c ON fa.id_cliente = c.id
                LEFT JOIN cliente_contrato_tipo cct ON cc.id_tipo_contrato = cct.id
                LEFT JOIN condicoes_pagamento cp ON cp.id = cct.id_condicoes_pagamento    
            SET fa.data_cancelamento = '{dataHoje}', fa.id_mot_cancelamento = 72, fa.status = 'C', fa.valor_cancelado = fa.valor_aberto
            WHERE 
                    fa.status = 'A' -- Status do título a receber
                    AND (CASE 
                                WHEN cc.cidade IS NULL THEN c.cidade
                                WHEN cc.cidade = 0 THEN c.cidade
                                ELSE cc.cidade
                            END) = {cidade} -- 1690: Joaquim Gomes & 1727: Porto Calvo
                    AND fa.id_carteira_cobranca != {carteiraCobranca} -- Carteira de faturamento diferente de GCP
                    AND cc.status = 'A' -- Status do contrato 
                    AND c.id_tipo_cliente = 4
                    AND cp.dia_fixo = {diaVencimento}
                    AND fa.data_vencimento >= '{dataHoje}';"""

# Cria um DataFrame com a instrução UPDATE
update_dfr= pd.DataFrame({'Update Instruction Receber': [update_instruction_receber]})

# Cria um novo DataFrame chamado 'df_contratos_impactados' contendo os valores únicos da coluna 'id_contrato' do DataFrame 'dfr'
df_contratos_impactados = pd.DataFrame(dfr['id_contrato'].unique())

# Exporta para um arquivo Excel com duas abas
with pd.ExcelWriter('dados_para_mudanca.xlsx') as writer:
    rollback_df.to_excel(writer, sheet_name='Rollback_Contrato', index=False)
    update_df.to_excel(writer, sheet_name='Update_Contrato', index=False)
    rollback_dfr.to_excel(writer, sheet_name='Rollback_Receber', index=False)
    update_dfr.to_excel(writer, sheet_name='Update_Receber', index=False)
    df_contratos_impactados.to_excel(writer, sheet_name='Contratos_Impactados', index=False)

print("Arquivo Excel criado com sucesso!")
