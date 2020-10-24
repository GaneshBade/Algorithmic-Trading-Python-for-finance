#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 12:27:33 2020

@author: gb
"""
import pandas as pd
import numpy as np

def getCrossOver(data, x, y):


    short_window = 9
    long_window = 10

    signals = pd.DataFrame(data.index)
    signals['signal'] = 0.0

    signals['x'] = x
    signals['y'] = y

    signals['signal'] = np.where(signals['x'][long_window:] > signals['y'][long_window:])

    data['signal'] = signals['signal']
    data['Position'] = signals['signal'].diff()

    data['x'] = x
    data['x'] = y

    return data


import yfinance as yf
ibull = yf.download("IBULHSGFIN.NS", start="2020-09-01", end="2020-09-26", interval="15m")

import talib

import pandas_ta as ta

rsi = talib.RSI(ibull.Close, timeperiod=10)

rsi_ema = talib.EMA(rsi, timeperiod=9)

getCrossOver(data=ibull, series_a=rsi, series_b=rsi_ema, series_a_short_window=9, series_b_long_window=10)


import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf
import talib

import pandas_ta as ta

df = yf.download("IBULHSGFIN.NS", start="2010-01-01", end="2020-09-28", interval="1d")

def verify_series(series:pd.Series):
    """If a Pandas Series return it."""
    if series is not None and isinstance(series, pd.core.series.Series):
        return series

def get_drift(x:int):
    """Returns an int if not zero, otherwise defaults to one."""
    return int(x) if x and x != 0 else 1

def get_offset(x:int):
    """Returns an int, otherwise defaults to zero."""
    return int(x) if x else 0

def roc(close, length=None, offset=None, **kwargs):
    """Indicator: Rate of Change (ROC)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs['min_periods'] is not None else length
    offset = get_offset(offset)

    # Calculate Result
    roc = 100 * mom(close=close, length=length) / close.shift(length)

    # Offset
    if offset != 0:
        roc = roc.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        roc.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        roc.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    roc.name = f"ROC_{length}"
    roc.category = 'momentum'

    return roc

def mom(close, length=None, offset=None, **kwargs):
    """Indicator: Momentum (MOM)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    offset = get_offset(offset)

    # Calculate Result
    mom = close.diff(length)

    # Offset
    if offset != 0:
        mom = mom.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        mom.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        mom.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    mom.name = f"MOM_{length}"
    mom.category = 'momentum'

    return mom


def kstgb(close, roc1=None, roc2=None, roc3=None, roc4=None, sma1=None, sma2=None, sma3=None, sma4=None, signal=None, drift=None, offset=None, **kwargs):
    """Indicator: 'Know Sure Thing' (KST)"""
    # Validate arguments
    close.dropna(inplace=True)
    close = verify_series(close)
    roc1 = int(roc1) if roc1 and roc1 > 0 else 10
    roc2 = int(roc2) if roc2 and roc2 > 0 else 15
    roc3 = int(roc3) if roc3 and roc3 > 0 else 20
    roc4 = int(roc4) if roc4 and roc4 > 0 else 30

    sma1 = int(sma1) if sma1 and sma1 > 0 else 10
    sma2 = int(sma2) if sma2 and sma2 > 0 else 10
    sma3 = int(sma3) if sma3 and sma3 > 0 else 10
    sma4 = int(sma4) if sma4 and sma4 > 0 else 15

    signal = int(signal) if signal and signal > 0 else 9
    drift = get_drift(drift)
    offset = get_offset(offset)

    # Calculate Result
    rocma1 = talib.SMA(talib.ROC(close, timeperiod=roc1), timeperiod=sma1)
    rocma2 = talib.SMA(talib.ROC(close, timeperiod=roc2), timeperiod=sma2)
    rocma3 = talib.SMA(talib.ROC(close, timeperiod=roc3), timeperiod=sma3)
    rocma4 = talib.SMA(talib.ROC(close, timeperiod=roc4), timeperiod=sma4)

    kst = (rocma1) + (2 * rocma2) + (3 * rocma3) + (4 * rocma4)
    kst_signal = talib.SMA(kst, timeperiod=signal)

    # Offset
    if offset != 0:
        kst = kst.shift(offset)
        kst_signal = kst_signal.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        kst.fillna(kwargs['fillna'], inplace=True)
        kst_signal.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        kst.fillna(method=kwargs['fill_method'], inplace=True)
        kst_signal.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    kst.name = "kst"
    kst_signal.name = "kst_signal"
    kst.category = kst_signal.category = "momentum"

    # Prepare DataFrame to return
    data = {kst.name: kst, kst_signal.name: kst_signal}
    kstdf = pd.DataFrame(data)
    kstdf.name = f"KST_{roc1}_{roc2}_{roc3}_{roc4}_{sma1}_{sma2}_{sma3}_{sma4}_{signal}"
    kstdf.category = "momentum"

    return kstdf

kst = kstgb(df.Close)


kst1 = ta.kst(df.Close)



