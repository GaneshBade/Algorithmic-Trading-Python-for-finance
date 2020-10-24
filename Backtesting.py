#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 11:31:09 2020

@author: gb
"""
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

stock_name = "TCS.NS"

df = yf.download(stock_name, start="2020-08-10", end="2020-10-01", interval='15m')

