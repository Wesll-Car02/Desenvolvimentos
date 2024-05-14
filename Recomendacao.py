import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Criação do DataFrame a partir do dataset
df = pd.DataFrame(dataset)

# Criação da matriz de utilidade com pivot
matriz_utilidade = df.pivot_table(index='CustomerKey', columns='ProductKey', values='SalesAmount', fill_value=0)

# Cálculo da matriz de similaridade usando cosseno
matriz_similaridade = cosine_similarity(matriz_utilidade)

# Criação de um DataFrame para a matriz de similaridade
df_similaridade = pd.DataFrame(matriz_similaridade, index=matriz_utilidade.index, columns=matriz_utilidade.index)

# Adição da coluna 'CustomerKey' para referência
df_similaridade['CustomerKey'] = df_similaridade.index

# Reordenação das colunas para que 'CustomerKey' seja a primeira
cols = ['CustomerKey'] + [col for col in df_similaridade.columns if col != 'CustomerKey']
df_similaridade = df_similaridade[cols]

# Exibição do DataFrame final
print(df_similaridade)
