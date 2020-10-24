%cd /home/gb/Desktop/Python-Algorithmic-Trading-Cookbook/Strategy Development

import inspect
from pyalgotrading.algobulls import AlgoBullsConnection
from StrategyRSICrossoverBracketOrder import StrategyRSICrossoverBracketOrder

algobulls_connection = AlgoBullsConnection()
algobulls_connection.get_authorization_url()

algobulls_connection.set_access_token('158ad8eea1db66a7897727f63b689a2de7330070')

print(inspect.getsource(StrategyRSICrossoverBracketOrder))

algobulls_connection.create_strategy(StrategyRSICrossoverBracketOrder, overwrite=True)

all_strategy_details = algobulls_connection.get_all_strategies()

strategy_code1 = all_strategy_details.iloc[3]['strategyCode']
strategy_details1 = algobulls_connection.get_strategy_details(strategy_code1)

from datetime import datetime as dt
from pyalgotrading.constants import *

instruments = algobulls_connection.search_instrument('IBULHSGFIN')

instrument = instruments[0]['value']

algobulls_connection.backtest(strategy_code=strategy_code1,
                              start_timestamp=dt(year=2020, month=9, day=14, hour=9, minute=15),
                              end_timestamp=dt(year=2020, month=10, day=13, hour=15, minute=15),
                              instrument=instrument,
                              lots=1,
                              strategy_parameters={
                                  'RSI_PERIOD': 14,
                                  'RSI_AVG_PERIOD': 9,
                                  'ROCP_PERIOD': 9,
                                  'ROCP_AVG_PERIOD': 5,
                                  'HILO_HIGH_PERIOD': 3,
                                  'HILO_LOW_PERIOD': 3,
                                  'MACD_FAST_PERIOD': 9,
                                  'MACD_SLOW_PERIOD': 24,
                                  'MACD_SIGNAL_PERIOD': 9,
                                  'target_trigger': 0.1,
                                  'stoploss_trigger': 0.01,
                                  'trailing_stoploss_trigger': 1
                              },
                              candle_interval=CandleInterval.MINUTES_5)

algobulls_connection.get_backtesting_job_status(strategy_code1)


logs = algobulls_connection.get_backtesting_logs(strategy_code1)
print(logs)

algobulls_connection.stop_backtesting_job(strategy_code1)

algobulls_connection.get_papertrading_job_status(strategy_code1)
algobulls_connection.stop_papertrading_job(strategy_code1)

