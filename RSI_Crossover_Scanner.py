!pip3 install lxml>=4.4.2
!pip3 install yfinance --upgrade --no-cache-dir

import pandas as pd
import numpy as np
import pandas_ta as ta
import talib
import yfinance as yf
from yahoo_fin import stock_info
from datetime import datetime, timedelta
from time import sleep

stocks = ['^NSEI', '^NSEBANK', '^BSESN', 'NCC.NS', 'NBCC.NS',
          'DAAWAT.NS','GRAPHITE.NS','TATAMOTORS.NS', 'YESBANK.NS',
          'STRTECH.NS','RADIOCITY.NS', 'ICICIBANK.NS','SUPRAJIT.NS',
          'APTECHT.NS','ASHOKLEY.NS','HSCL.NS','EICHERMOT.NS','RELIANCE.NS',
          'TCS.NS','HDFCBANK.NS', 'HINDUNILVR.NS', 'INFY.NS', 'HDFC.NS',
          'BHARTIARTL.NS','KOTAKBANK.NS','ICICIBANK.NS', 'ITC.NS',
          'TITAN.NS', 'ULTRACEMCO.NS', 'HINDALCO.NS','TATASTEEL.NS',
          'LT.NS', 'SHREECEM.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS','COALINDIA.NS',
          'ZEEL.NS', 'HEROMOTOCO.NS', 'INDUSINDBK.NS','GAIL.NS','WIPRO.NS',
          'ONGC.NS', 'CIPLA.NS', 'NTPC.NS','JSWSTEEL.NS',
          'HDFCLIFE.NS', 'TECHM.NS','BHARTIARTL.NS']

def GetStockData(tickers):
    start = datetime.now() - timedelta(days=2)
    end = datetime.now()
    df1 = pd.DataFrame()
    test = pd.DataFrame()
    for stock in stocks:
        df = yf.download(stock, start=start, end=end, interval="15m")
        df['Stock'] = stock
        print(stock)
        ######################### RSI ################################
        df['RSI'] = talib.RSI(df.Close, timeperiod=14)
        df['RSI_EMA'] = talib.EMA(df.RSI, timeperiod=9)

        cross = ta.cross(series_a=df.RSI, series_b=df.RSI_EMA, above=True)
        cross_down = ta.cross(series_a=df.RSI, series_b=df.RSI_EMA, above=False)
        cross_down.replace(1, -1, inplace=True)

        for each in range(len(cross)):
            if cross_down.iloc[each] == -1:
                cross.iloc[each] = -1
        df['RSI_X'] = cross
        ################## shortlist for trade ########################
        test = test.append(df)
        if df.RSI_X.iloc[-1] in [1, -1]:
            if (df.RSI.iloc[-1] > 70) or (df.RSI.iloc[-1] < 30):
                df1 = df1.append(df.tail(1))
                appended_stock = df['Stock'].iloc[-1]
                print(f'record appended {appended_stock}')
    return df1

report = pd.DataFrame()
while True:
    data = GetStockData(tickers=stocks)
    report.append(data)
    # if data['Close'] < 200:
    #     qty=1000
    # elif data['Close'] < 300:
    #     qty=800
    # elif data['Close'] < 400:
    #     qty=600
    # elif data['Close'] < 500:
    #     qty=500
    # elif data['Close'] > 5000:
    #     qty=0
    # else:
    #     qty=100
    seconds = 300
    candle = datetime.now() + timedelta(seconds=seconds)
    candle = candle.strftime('%X')
    print(f'Waiting for candle to complete {candle}')
    sleep(seconds)

























while True:
    df1 = pd.DataFrame()

    for stock in stocks:
        start = datetime.now() - timedelta(days=2)
        end = datetime.now()
        df = yf.download(stock, start=start, end=end, group_by="ticker", interval="15m")
        df['Stock'] = stock

        print(stock)

        ######################### RSI ################################
        df['RSI'] = talib.RSI(df.Close, timeperiod=14)
        df['RSI_EMA'] = talib.EMA(df.RSI, timeperiod=9)

        cross = ta.cross(series_a=df.RSI, series_b=df.RSI_EMA, above=True)
        cross_down = ta.cross(series_a=df.RSI, series_b=df.RSI_EMA, above=False)
        cross_down.replace(1, -1, inplace=True)

        for each in range(len(cross)):
            if cross_down.iloc[each] == -1:
                cross.iloc[each] = -1

        df['RSI_X'] = cross
        ################## shortlist for trade ########################
        if (df.RSI.iloc[-1] > 70) or (df.RSI.iloc[-1] < 30):
            df1 = df1.append(df.tail(1))



df1 = df1[df1['RSI_X'] != 0]



test = yf.download("ITC.NS", start=start, end=end, group_by="ticker", interval="5m")











    if df.RSI_X.iloc[-1] == 1:
        df1.append(df['Stock'].iloc[-1])
        df2.append(df['RSI_X'].iloc[-1])
    elif df.RSI_X.iloc[-1] == -1:
        df1.append(df['Stock'].iloc[-1])
        df2.append(df['RSI_X'].iloc[-1])










    if df.RSI_X.iloc[-1] == 1:
        #if ((df.RSI_EMA.iloc[-1] <= 20) or (df.RSI.iloc[-1] <= 20)):
            shortlist.append(df.iloc[-1])
    elif df.RSI_X.iloc[-1] == -1:
        #if ((df.RSI_EMA.iloc[-1] >= 70) or (df.RSI.iloc[-1] >= 70)):
            shortlist.append(df.iloc[-1])








    # df['CCI'] = talib.CCI(df.High, df.Low, df.Close, timeperiod=20)
    # df['CCI_EMA'] = talib.EMA(df.CCI, timeperiod=9)

    # cross = ta.cross(series_a=df.CCI, series_b=df.CCI_EMA, above=True)
    # cross_down = ta.cross(series_a=df.CCI, series_b=df.CCI_EMA, above=False)
    # cross_down.replace(1, -1, inplace=True)

    # for each in range(len(cross)):
    #     if cross_down.iloc[each] == -1:
    #         cross.iloc[each] = -1

    # df['CCI_X'] = cross














