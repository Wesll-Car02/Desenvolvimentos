import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Função derivada simplificada (delta de preço)
def price_derivative(t, P, prices, volatility):
    t = int(t)
    
    if t > 0 and t < len(prices) - 1:
        return (prices[t+1] - prices[t-1]) / 2
    elif t == len(prices) - 1:
        return (prices[t] - prices[t-1])
    else:
        return volatility * np.random.normal()

# Método de Runge-Kutta 4ª Ordem
def runge_kutta_4th_order(P0, t0, h, n_steps, volatility, prices, n_dias):
    P = np.zeros(n_steps + n_dias)
    P[:n_steps] = prices  # Preenche os preços históricos
    
    t = t0
    
    for i in range(n_steps, len(P)):
        k1 = h * price_derivative(t, P[i-1], P[:n_steps], volatility)
        k2 = h * price_derivative(t + h/2, P[i-1] + k1/2, P[:n_steps], volatility)
        k3 = h * price_derivative(t + h/2, P[i-1] + k2/2, P[:n_steps], volatility)
        k4 = h * price_derivative(t + h, P[i-1] + k3, P[:n_steps], volatility)
        
        P[i] = P[i-1] + (k1 + 2*k2 + 2*k3 + k4) / 6
        t += h
    
    return P

# Função geral para prever e plotar os preços
def predict_stock_price(ticker, start_date, end_date, n_dias):
    # Baixar dados históricos
    data = yf.download(ticker, start=start_date, end=end_date)
    prices = data['Close'].values
    
    # Parâmetros para Runge-Kutta
    h = 1  # Intervalo de tempo (um dia)
    n_steps = len(prices)
    P0 = prices[0]  # Preço inicial
    t0 = 0  # Tempo inicial
    volatility = np.std(np.diff(prices))  # Usar a volatilidade histórica dos preços
    
    # Prever preços com Runge-Kutta
    predicted_prices = runge_kutta_4th_order(P0, t0, h, n_steps, volatility, prices, n_dias)
    
    # Plotar resultados
    plt.figure(figsize=(14,7))
    plt.plot(np.arange(len(prices)), prices, label=f'Preços Reais - Papel: {ticker}')
    plt.plot(np.arange(len(predicted_prices)), predicted_prices, label= f'Previsão Runge-Kutta (Incluindo +{n_dias} dias)', linestyle='--')
    plt.axvline(x=len(prices)-1, color='r', linestyle=':', label='Início da Previsão')
    plt.title(f'Previsão de Preços da {ticker} usando Runge-Kutta 4ª Ordem com Volatilidade')
    plt.xlabel('Tempo (dias)')
    plt.ylabel('Preço de Fechamento (R$)')
    plt.legend()
    plt.show()
    
    # Criar DataFrame com a previsão dos próximos n_dias
    forecast_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=n_dias, freq='B')  # Dias úteis
    forecast_df = pd.DataFrame({'Data': forecast_dates, 'Previsão de Preço': predicted_prices[-n_dias:]})
    
    return forecast_df

# Exemplo de uso:
ticker = 'VALE3.SA'
start_date = "2022-01-01"
end_date = "2024-12-31"
n_dias = 180

previsao_df = predict_stock_price(ticker, start_date, end_date, n_dias)
print(f"Previsão dos próximos {n_dias} dias:")
display(previsao_df.head(60))
