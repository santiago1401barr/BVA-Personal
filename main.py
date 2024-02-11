 #Librerias a Importar
import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px
import stocknews as sn
import pandas_ta as ta
from datetime import datetime
from googletrans import Translator
translator = Translator()
import time
import random
import requests

#Api Keys
API_KEY_FMP = "XI4NPegcqzfwPKtPVCwM2xvPzMymjdUk"

#Codigo Principal
st.set_page_config( page_title = "Simulador BVA")
ticker_list = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/s-and-p-500-companies/master/data/constituents_symbols.txt')
ticker = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol
fecha_predeterminada = datetime(2020, 10, 10)
Fecha_Inicio = st.sidebar.date_input("Fecha de Inicio", fecha_predeterminada)
Fecha_Fin = st.sidebar.date_input("Fecha de Fin")
monto = 1000
texto = 'El precio actual de esta acción es '

#Grafico del movimiento de precios de la accion
tickerData = yf.Ticker(ticker)
nombre_empresa = tickerData.info['longName']
data = yf.download(ticker, start = Fecha_Inicio , end = Fecha_Fin )
fig = px.line(data, x = data.index, y = data['Adj Close'], title = nombre_empresa)
st.plotly_chart(fig)
status_text = st.empty()

#Objetos, Clases y Funciones
class Stock:
    def __init__(self, ticker, precio, Cantidad):
        self.ticker = ticker
        self.precio = precio
        self.Cantidad = Cantidad

class Portfolio:
    def __init__(self):
        self.stocks = []

    def add_stock(self, stock):
        self.stocks.append(stock)

    def remove_stock(self, ticker):
        for stock in self.stocks:
            if stock.ticker == ticker:
                self.stocks.remove(stock)

    def calcular_valor_portafolio(self):
        valor_total = 0
        for stock in self.stocks:
            valor_total += stock.precio * stock.Cantidad
        return valor_total

    def encontrar_stock(self, ticker):
        for stock in self.stocks:
            if stock.ticker == ticker:
                return stock
        return None
    def get_portfolio_info(self):
        portfolio_info = []
        for stock in self.stocks:
            portfolio_info.append((stock.ticker, stock.Cantidad))
        return portfolio_info

class User:
    def __init__(self, monto):
        self.balance = monto
        self.portfolio = Portfolio()
        self.invertido = []

    def comprar(self, Cantidad, precio,ticker):
        dinero_asignado = Cantidad * precio
        costo_transaccion = 0.025
        total_cost = dinero_asignado + costo_transaccion * dinero_asignado

        if self.balance >= total_cost:
            self.balance -= total_cost
            self.portfolio.add_stock(Stock(ticker, precio, Cantidad))
            if not self.invertido:
                self.invertido.append(dinero_asignado)
            else:
                self.invertido.append(dinero_asignado + self.invertido[-1])

    def vender(self, Cantidad, precio ,ticker):
        stock_por_vender = self.portfolio.encontrar_stock(ticker)
        if stock_por_vender and stock_por_vender.Cantidad >= Cantidad:
            dinero_asignado = Cantidad * precio
            costo_transaccion = 0.025
            total_proceeds = dinero_asignado - costo_transaccion * dinero_asignado

            self.balance += total_proceeds
            stock_por_vender.Cantidad -= Cantidad

            self.invertido.append(dinero_asignado + self.invertido[-1])

#Funciones

def conseguir_precio_actual(ticker):
    data_actual = yf.Ticker(ticker).history(period='1y')
    return {'': data_actual.iloc[-1].Close,}

user = User(monto)


informacion_empresa, informacion_financiera, noticias, Portafolio, Indicador_Tecnico = st.tabs(["¿De que trata la Empresa?", "Información Financiera", "Top 10 noticias", "Portafolio Personal","Indicador Tecnico"])

with informacion_empresa:
      if 'longBusinessSummary' in tickerData.info:
          resumen_empresa = tickerData.info['longBusinessSummary']
      else:
          Disponibilidad = 1
          resumen_empresa = "Information not available"

      resumen_traducido =  translator.translate(resumen_empresa, src='en', dest='es')
      st.info(resumen_traducido.text)

with informacion_financiera:
    st.header(f"Estados financieros de {ticker}")
    st.write("Este apartado tiene los datos de precios historicos la Acción ",ticker)
    data2 = data
    data2['% Change'] = data['Adj Close']/data['Adj Close'].shift(1) - 1
    data2.dropna(inplace = True)
    st.write(data2)
    retorno_anual = data2['% Change'].mean()*252*100
    st.write("El retorno anual de ", ticker," es ", retorno_anual, "%")
    desv_stand = np.std(data2["% Change"])*np.sqrt(252)
    st.write("La desviacion estandar de los precios de ",ticker," es ", desv_stand*100, "%")
    st.write("La rendimiento ajustado al riesgo de ",ticker, "es ", retorno_anual/(desv_stand*100))
    st.write("")
    st.write("")

    st.write("Este apartado tiene informacion extra de la Acción ",ticker)
    url_base = 'https://financialmodelingprep.com/api/v3'
    datos_financieros_extras = st.selectbox("Información Financiera extra ", options = ('income-statement','balance-sheet-statement','cash-flow-statement','income-statement-growth',
                                                                     'balance-sheet-statement-growth','cash-flow-statement-growth','ratios-ttm','ratios','financial-growth',
                                                                    'quote','rating','enterprise-values','key-metrics-ttm','key-metrics','historical-rating','discounted-cash-flow',
                                                                     'historical-discounted-cash-flow-statement'))
    url = f'{url_base}/{datos_financieros_extras}/{ticker}?apikey={API_KEY_FMP}'
    data_financiera = requests.get(url).json()
    df_financiero = pd.DataFrame(data_financiera)
    st.write(df_financiero)

with noticias:
    st.header(f"Noticias de {ticker}")
    sn = sn.StockNews(ticker, save_news = False)
    df_noticias = sn.read_rss()
    for i in range(10):
      st.subheader(f"Noticia {i + 1}")
      st.write(df_noticias['published'][i])
      titulo_traducido = translator.translate(df_noticias['title'][i], src='en', dest='es')
      st.write(titulo_traducido.text)
      resumen_traducido = translator.translate(df_noticias['summary'][i], src='en', dest='es')
      st.write(resumen_traducido.text)

with Portafolio:
    st.header("Portafolio del Usuario")
    boton_comprar = st.button("Comprar esta Acción")
    boton_vender = st.button("Vender esta Acción")
    Cantidad = st.slider("¿Cuantas acciones de este Empresa deseas Comprar/Vender?", 1, 100, 10)
    precio = conseguir_precio_actual(ticker)
    precio_actual = round(precio[''], 4) * random.uniform(0.995, 1.005)
    status_text.text(texto + str(precio_actual))

    if boton_comprar:
        user.comprar(Cantidad, precio_actual,ticker)
        user_balance = user.balance  # Obtener el balance actualizado
        portfolio_value = user.portfolio.calcular_valor_portafolio()
        investment_history = user.invertido
        st.text(f"Balance de Usuario: {user_balance}")
        st.text(f"Valor del Portafolio: {portfolio_value}")
        st.text(f"Historial de Inversiones o transacciones: {investment_history}")
        portfolio_info = user.portfolio.get_portfolio_info()
        for ticker, Cantidad in portfolio_info:
          st.text(f"ticker: {ticker}, Cantidad: {Cantidad}")

    if boton_vender:
        user.vender(Cantidad, precio_actual,ticker)
        user_balance = user.balance  # Obtener el balance actualizado
        portfolio_value = user.portfolio.calcular_valor_portafolio()
        investment_history = user.invertido
        st.text(f"Balance de Usuario: {user_balance}")
        st.text(f"Valor del Portafolio: {portfolio_value}")
        st.text(f"Historial de Inversiones o transacciones: {investment_history}")
        portfolio_info = user.portfolio.get_portfolio_info()
        for ticker, Cantidad in portfolio_info:
          st.text(f"ticker: {ticker}, Cantidad: {Cantidad}")    


with Indicador_Tecnico:
    st.subheader("Analisis Tecnico: ")
    df_indicators = pd.DataFrame()
    ind_list = df_indicators.ta.indicators(as_list = True)
    technical_indicator = st.selectbox("Indicador Tecnico ", options = ind_list)
    method = technical_indicator
    indicator = pd.DataFrame(getattr(ta,method)(low = data["Low"], close = data["Close"], high = data["High"], open = data["Open"], volume = data["Volume"]))
    indicator["Close"] = data["Close"]
    figw_ind_new = px.line(indicator)
    st.plotly_chart(figw_ind_new)
    st.write(indicator)


