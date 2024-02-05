#Librerias a Importar
import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px
from datetime import datetime
import stocknews as sn
from googletrans import Translator
import pandas_ta as ta
from pyChatGPT import ChatGPT
translator = Translator()
import time
import random

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


informacion_empresa, informacion_precios, noticias, Portafolio, Indicador_Tecnico, Openai1 = st.tabs(["¿De que trata la Empresa?", "Datos de precios", "Top 10 noticias", "Portafolio Personal", "Indicador Tecnico", "Información Extra"])

with informacion_empresa:
      if 'longBusinessSummary' in tickerData.info:
          resumen_empresa = tickerData.info['longBusinessSummary']
      else:
          Disponibilidad = 1
          resumen_empresa = "Information not available"

      resumen_traducido =  translator.translate(resumen_empresa, src='en', dest='es')
      st.info(resumen_traducido.text)

with informacion_precios:
      st.header("Movimiento de Precios de la Acción")
      st.write(data)
      st.write("Open: El precio al que se inició la negociación de acciones en un día específico.")
      st.write("High: El precio más alto de la acción durante un día específico. Es decir, el precio más alto al que se habían vendido las acciones en el mercado ese día.")
      st.write("Low: El precio de la acción en su punto más bajo durante un día en particular. En otras palabras, el precio más bajo al que se habían vendido las acciones en el mercado ese día.")
      st.write("Close: El precio al que finalizó la negociación de acciones en un día de mercado específico.")
      st.write("Adj Close: El precio de cierre (Close) de la acción se resta de los dividendos o divisiones que se declararon sobre las acciones durante el día de negociación para llegar a este precio.")
      st.write("Volume: Número total de acciones vendidas en el mercado durante un determinado día. Es un indicador crucial de la actividad del mercado y puede mostrar la fuerza y ​​dirección del movimiento del precio de una acción")

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
    df = pd.DataFrame()
    ind_list = df.ta.indicators(as_list = True)
    technical_indicator = st.selectbox("Indicador Tecnológico ", options = ind_list)
    method = technical_indicator
    indicator = pd.DataFrame(getattr(ta,method)(low = data["Low"], close = data["Close"], high = data["High"], open = data["Open"], volume = data["Volume"]))
    indicator["Close"] = data["Close"]
    figw_ind_new = px.line(indicator)
    st.plotly_chart(figw_ind_new)
    st.write(indicator)


session_token = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..oEYZtHmse77fiAWJ.ti3tzy0uU5Cu4nxz_wcAFOoMt8-yO9fL9RG__2AZD0MPwpfXzyYridtAgBPH3M_BwuM6FNQxqlQ7wQS-CnisUjab2c4-ZFGGI3SWPXuKikkyczNWcxy8ZrIk37K7NEI1o6HqohvSjrr7mqFXyeCzgaWFWstnoV4jYHBNv0L38CSGPOEvTquFE__GCiTYOm6762Ef_W9Gtu3ZGQEb9cGgU-A_m1JpyMmF2WPTAvBwWh1dAqDgQG2F-_chSNi7MPb2rqPIG1feGoNUZOnroKR0iNe7o6yRYihSf2lqIc39fYmd5rKA7AUiT8vJ9XBAcQWFsosbW0jTWyoBjZfGG1fzJH-SNGnSncmLv3HhDpujpkT_divne0auLT-BUNh-IIkvoM_rKZbdQkd1oc_xydkncfN3xBPz3FHuCrV9W1tHNG9jy0AfWbypcAKWHK4wkmu9beg83RMi0JbP108UqHNav4V0A3szq5Pbo2DNGI-LpXmL7heyqNEu7yrugabSeQWSUIA7Ovwgw7t3x9pd1LMzwo-YKscQqqK9AencxfOtqh4uwT_CUca8QvzheGfu2YPynva19Lt3TJ6NtNYSx5dE8L7qdsZcOinL5BMi8i9_H1gFKNlPuZYTRrzaSKNzZ0H_KCTpxyY2U9WLRJwSscJmSW_aDWfqC14ObfZ79b62PK8nlFtPUDvUo0VezWr_NKNYcs8KwuAO81TNrsxgpwyltjbGzB7x8GE33lXBthNn0j7r88uQ_SC0Zdl0sdAW2w0dLUYjSBeb8qBxJtYy4uNCG4gpup4Xq9q6y9MzrnYS21mx7vnqqb3iLkM8OY_1akH2mz5vLkNFfDlzwheUQdMLtTpAEcKQS6Fr20bNe03T7UXFchQh__RJ-EINr10c-dvxbPAFHpHT0I0CP7hO7PMrTHF85FDOYUlUYJWY8nObsOTWnnDcQtaQslPfy-8cwnPg4Z4lQm_39W8pYbyVGUPkjOG3yUw-E2ZyEds_qjYv4Y2DScLE2r-ss7PkURSPcn0WjtJ4VlNJ8sApbQshvLGoppQtCjCYih5I9ixB5Km-klnT5mwdGsioK0Ft78JzLii9wUba8JIo24hp9L7RLf6-WkInr9dD5ixFxOxAhmBjgtPavhRMcTM68Y_CYtoo-OV2_YMCf_ZoHWmx4Pqvx0PAhgT2wh_G84hSpt0a1eGc3Qo8IDA4KzShTIBMlzbHs80qbwWyblmRpu-2wDbA4vKV7yGCg8iMAW-zcI5UR2RvZH7Tjquge7BhN-OYqzzCIJ-IbUwyPhr-2ZJhkGlgPc56-efSoBHRNkU5LXzrZCN-Kg-8uBASlKeQdDTwt5oWkHOKIgwT1HwyNVkLQTJcpLjHwGG2RUPKOhsdZZg2mfAL4crOss0VyjnIdrmVnohoA-9FPwUM5gtdFnFkJ7xHxahYUQlFvCxJE6hbknm-4P-JLmh_4VHMyJaOKHE3wXDo8dMmM3WR0dRC0PaKpQaVr2vGjpgfue5hX01JAdBZCr57-iSdWLTfNtbyRTqIOetklmVd3j29T2NtT_nbyo2EpHEf74XHAKTve4XJFfBIlX68I5UStisFY3BQWLrT02v2qPT7eMIbXkZQaAG7CBPXI9b7q-YRQBraRpvb1Nle7vSOshWU_wIJByTxB-tcXgPj5MkKOWJJgVbTx1HC2R8nNF2XigsaCeXhlmm8b97Lpem3UdBrddgXX5fs1wQxThlE0wwP2Ju08SBPuUGhlc48Plbi_sFFX9bjMmA9_tumABVDu-si00U50abUXQMDP2LqVypBwo42yt5J9_Msg-bBCMaUoTRiGrYhwOaj82G3b4MsXktJlN86OQ1q3CquUhFAPtSrRLPRwKNhbYuKVrz7Mn7rNbFFAmIni2tMbmUUT-B347FXPHxc7q4eofXL0gXYge-jHKJQ8cSO8O2rDHc4cAqkjM4ZXfQe7OLl59z-j46WB1QkRToJUpCa_-7qKY_8bYHWGyfbDiTlku7IY49wx1HnYX7cmBoxajgXewj0P3y3-l1I5YgmhrcpAxVUYptDhxy_QMJYFJ80cLmvfcPMgFfDPlxxkQZHoYV8PDSe-5z_E0qul3V871wXDMcH_gF3qTN9m-q09YgUTzpiDhsNoKjtVfC7z9s2dPRuKhRoTU4hEOipRa3wtO5FnYBA42xqvXnc8BZLlOUmTAx2T0EYLf0raGsDfwZonW--QFvuUUqJsx-E5Tw9RtejttZv50-pxNXmvSV4q4r135uyF6-42yhz0KGJkN7JwH-aSMvIUdmNazDXyZZBCTmiQgL1F2E1_nabyyfkkPX7t2qChO_TTkW5BF93mswpuWOIj5GxpdoCfjrzTcBPLPLse926wc3T21k0dWCqQpQjCCrccvwqX_WJLLDy9PAd-dx682bfpUvtucrcOt3DLKVfiC24g0CMSKu_S0KPAnseUmvdCdBA5p5eVYFtIXc7Ww9NJn1USPlmXO8X9B-hTFj_LJhbaiCbsw1jmJDE6L8J1nCTudWcq-4N1wCpIGplPxjeyAtTo_563I-GM_Tr5Kc3VCDndB-0uzfMAih3sXrXHctqa9wikRGSntBiNnlkTxCr8Qeq2nk7oUYs5v7o4vqDKTRxGRd9bcaOlXH_7s7gN13fRC578LChcErUuH-zdxIYoAjDB5GNIP9DaodED0qmOY76N5yv5el1nVssP88LXWSsRDhZfhmuUMKTDe-keeKqdkSbieKqkilRy8Rb_Q2TWT0Orq_8ndxn2yoSpu0TeDAiwISxCbZ_92eaXTjmU_A9uqrqwLYxKBHQkcHi-_cfsTsomX04brdSpKKA0ZJE0uNFWAcbvW_e6LM.UYvIP5Q7ecG_c2iB8uCyUw'
api2 = ChatGPT(session_token)
comprar_razones = api2.send_message(f' 3 Razones para comprar stocks de {ticker} ')
vender_razones = api2.send_message(f' 3 Razones para vender stocks de {ticker} ')
SWOT = api2.send_message(f' Realiza un Analisis SWOT del stocks {ticker} ')

with Openai1:
    tab_razon_vender, tab_razon_comprar, tab_SWOT =  st.tabs(['3 Razones para comprar', '3 Razones para vender', 'Analisis SWOT'])

    with tab_razon_vender:
        st.subheader(f' 3 Razones para comprar acciones de {ticker} ')
        st.write(comprar_razones['message'])

    with tab_razon_comprar:
        st.subheader(f' 3 Razones para vender acciones de {ticker} ')
        st.write(vender_razones['message'])

    with tab_SWOT:
        st.subheader(f' Analisis SWOT ')
        st.write(SWOT['message'])


