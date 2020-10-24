#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 09:57:36 2020

@author: gb
"""

%cd /home/gb/Desktop/Python-Algorithmic-Trading-Cookbook/Strategy Development

import inspect
from pyalgotrading.algobulls import AlgoBullsConnection
from StrategyRSIEMARegularOrder import StrategyRSIEMARegularOrder



algobulls_connection = AlgoBullsConnection()
algobulls_connection.get_authorization_url()

algobulls_connection.set_access_token('b8e52fd1bc7474b03c00d135b7af0034dd93e0a8')

print(inspect.getsource(StrategyRSIEMARegularOrder))

algobulls_connection.create_strategy(StrategyRSIEMARegularOrder, overwrite=True)

all_strategy_details = algobulls_connection.get_all_strategies()

strategy_code1 = all_strategy_details.iloc[2]['strategyCode']
strategy_details1 = algobulls_connection.get_strategy_details(strategy_code1)

from datetime import datetime as dt
from pyalgotrading.constants import *

instruments = algobulls_connection.search_instrument('IBULHSGFIN')

instrument = instruments[0]['value']

algobulls_connection.backtest(strategy_code=strategy_code1,
                              start_timestamp=dt(year=2020, month=9, day=1, hour=9, minute=30),
                              end_timestamp=dt(year=2020, month=9, day=25, hour=15, minute=15),
                              instrument=instrument,
                              lots=1,
                              strategy_parameters={
                                  'RSI_PERIOD': 14,
                                  'RSI_AVG_PERIOD': 9,
                                  'ROC_AVG_PERIOD': 9,
                                  'ROCP_PERIOD': 10,
                                  'ROCP_AVG_PERIOD': 9
                              },
                              candle_interval=CandleInterval.MINUTES_15)



algobulls_connection.get_backtesting_job_status(strategy_code1)


logs = algobulls_connection.get_backtesting_logs(strategy_code1)
print(logs)

algobulls_connection.stop_backtesting_job(strategy_code1)

algobulls_connection.get_papertrading_job_status(strategy_code1)
algobulls_connection.stop_papertrading_job(strategy_code1)

