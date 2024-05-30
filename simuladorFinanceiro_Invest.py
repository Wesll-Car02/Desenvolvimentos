import matplotlib.pyplot as plt

# Solicitação dos valores iniciais
vlrAplicar = vlrInicial = float(input('Digite quanto você vai aplicar inicialmente: R$ '))
vlrAcao = float(input('Digite o valor da ação: R$ '))
vlrDividendo = float(input('Digite o valor do dividendo por ação: R$ '))
aporteMensal = float(input('Digite o valor do aporte mensal: R$ '))
numMeses = int(input('Quantos meses você quer simular? '))

# Inicialização das variáveis
Resto = vlrAplicar % vlrAcao
qtdAcoes = (vlrAplicar - Resto) / vlrAcao
Dividendo = DividendoAcum = 0
ListaDivAcum = []
ListaDiv = []
ListaMeses = []

# Verificação se o valor inicial é suficiente para comprar pelo menos uma ação
if vlrAplicar >= vlrAcao:
    for i in range(numMeses + 1):
        ListaMeses.append(i)
        
        if i > 0:
            Dividendo = qtdAcoes * vlrDividendo
            RestoDividendo = Dividendo % vlrAcao
            vlrAplicar = Resto + Dividendo + aporteMensal
            Resto = vlrAplicar % vlrAcao
            
            if vlrAplicar >= vlrAcao:
                qtdAcoes += (vlrAplicar - Resto) / vlrAcao
            
            DividendoAcum += Dividendo
            print(f'Seu dividendo no mês {i} foi de R$ {Dividendo:.2f} e você possui {qtdAcoes:.2f} ações.')
        
        ListaDivAcum.append(DividendoAcum)
        ListaDiv.append(Dividendo)
else:
    print('O valor que você deseja aplicar é menor que o valor da ação.')

# Removendo o primeiro mês, que é a condição inicial
del ListaDivAcum[0]
del ListaMeses[0]
del ListaDiv[0]

# Exibição dos resultados acumulados
print(ListaDivAcum)
print(ListaMeses)

# Plotagem dos resultados em gráfico de colunas
fig, ax = plt.subplots()
ax.bar(ListaMeses, ListaDivAcum, label='Dividendo Acumulado', alpha=0.7)
ax.bar(ListaMeses, ListaDiv, label='Dividendo Mensal', alpha=0.7)

# Configurações do gráfico
ax.set_xlabel('Meses')
ax.set_ylabel('Valor (R$)')
ax.set_title('Evolução dos Dividendos ao Longo dos Meses')
ax.legend()

plt.show()

# Exibição do resultado final
print(f'O valor total apenas de dividendos é de R$ {DividendoAcum:.2f}, com uma quantidade de {qtdAcoes:.2f} ações, e o total com a aplicação inicial e aporte mensal é de R$ {(aporteMensal*numMeses) + vlrInicial + DividendoAcum:.2f} 🤑.')
