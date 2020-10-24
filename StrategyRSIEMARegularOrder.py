#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 09:29:06 2020

@author: gb
"""
from pyalgotrading.strategy.strategy_base import StrategyBase
from pyalgotrading.constants import *


class StrategyRSIEMARegularOrder(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # timeperiod variables
        self.RSI_PERIOD = self.strategy_parameters['RSI_PERIOD']          # 14 days

        self.RSI_AVG_PERIOD = self.strategy_parameters['RSI_AVG_PERIOD']  # 9 days

        self.ROC_AVG_PERIOD = self.strategy_parameters['ROC_AVG_PERIOD']  # 9 days

        # self.PVT_PERIOD = self.strategy_parameters['PVT_PERIOD']          # 30 days
        # self.PVT_AVG_PERIOD = self.strategy_parameters['PVT_AVG_PERIOD']  # 8 days

        self.ROCP_PERIOD = self.strategy_parameters['ROCP_PERIOD']  # 10 days
        self.ROCP_AVG_PERIOD = self.strategy_parameters['ROCP_AVG_PERIOD']  # 9 days

        self.main_order = None

    def initialize(self):
        self.main_order = {}

    @staticmethod
    def name():
        return 'RSI & EMA Regular Order Strategy'

    @staticmethod
    def versions_supported():
        return AlgoBullsEngineVersion.VERSION_3_2_0


    def get_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)
        ltp = self.broker.get_ltp(instrument)
        rsi = talib.RSI(hist_data['close'], timeperiod=self.RSI_PERIOD)
        ema = talib.EMA(rsi, timeperiod=self.RSI_AVG_PERIOD)
        rsi_crossover_value = self.utils.crossover(rsi, ema)
        rsi_crossover_value_prev = self.utils.crossover(rsi.shift(1), ema.shift(1))

#       pvt = ((talib.ROC(hist_data['close'], timeperiod=self.PVT_PERIOD))
#              * hist_data['volume']).cumsum().round(2)
#       pvt_ema = talib.EMA(hist_data['close'], timeperiod=self.PVT_AVG_PERIOD).round(2)

        rocp = talib.ROCP(hist_data['close'], timeperiod=self.ROCP_PERIOD)
        rocp_ema = talib.EMA(rocp, timeperiod=self.ROCP_AVG_PERIOD)
        rocp_crossover_value = self.utils.crossover(rocp, rocp_ema)
        rocp_crossover_value_prev = self.utils.crossover(rocp.shift(1), rocp_ema.shift(1))

        #engulfing = talib.CDLENGULFING(hist_data['open'],hist_data['high'], hist_data['low'], hist_data['close'])

        # if (((rsi_crossover_value == 1 | rsi_crossover_value_prev == 1) & (rocp_crossover_value == 1 | rocp_crossover_value_prev == 1)) & ((rsi.iloc[-1] < 20.0) & (rsi.shift(1).iloc[-1] < 20.0))):
        #       crossover_value = 1
        # elif (((rsi_crossover_value == -1 | rsi_crossover_value_prev == -1) & (rocp_crossover_value == -1 | rocp_crossover_value_prev == -1)) & ((rsi.iloc[-1] > 40.0) & (rsi.shift(1).iloc[-1] > 40.0))):
        #       crossover_value = -1
        # if (((rsi_crossover_value == 1 | rsi_crossover_value_prev == 1) & (rocp_crossover_value == 1 | rocp_crossover_value_prev == 1))):
        #       crossover_value = 1
        # elif (((rsi_crossover_value == -1 | rsi_crossover_value_prev == -1) & (rocp_crossover_value == -1 | rocp_crossover_value_prev == -1))):

        # if (((rsi_crossover_value == 1) | (rsi_crossover_value_prev == 1)) & ((rsi.iloc[-1] < 30.0) & (rsi.shift(1).iloc[-1] < rsi.iloc[-1]))):
        #       crossover_value = 1
        # elif (((rsi_crossover_value == -1) | (rsi_crossover_value_prev == -1)) & ((rsi.iloc[-1] > 40.0) & (rsi.shift(1).iloc[-1] > rsi.iloc[-1]))) :

        # if ((((rsi_crossover_value == 1) | (rsi_crossover_value_prev == 1)) & ((rsi.iloc[-1] < 30.0) & (rsi.shift(1).iloc[-1] < rsi.iloc[-1]))) & (engulfing.iloc[-1] == 100)):
        #       crossover_value = 1
        # elif ((((rsi_crossover_value == -1) | (rsi_crossover_value_prev == -1)) & ((rsi.iloc[-1] > 47.0) & (rsi.shift(1).iloc[-1] > rsi.iloc[-1]))) & (engulfing.iloc[-1] == -100)):
        #     crossover_value = -1
        if ((((rsi_crossover_value == 1) & (rocp_crossover_value == 1)) | ((rsi_crossover_value_prev == 1) & (rocp_crossover_value_prev == 1))) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34))):
              crossover_value = 1
        elif ((((rsi_crossover_value == -1) & (rocp_crossover_value == -1)) | ((rsi_crossover_value_prev == -1) & (rocp_crossover_value_prev == -1))) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34))):
            crossover_value = -1
        else:
             crossover_value = 0

        return crossover_value

#        if ((crossover_value == 1) & ((rsi.iloc[-1]<20.0) & (rsi.shift(1).iloc[-1]<23.0))
#            & (pvt.iloc[-1] > pvt.shift(1).iloc[-1])):
#            crossover_value = 1
#        elif ((crossover_value == -1) & ((rsi.iloc[-1]> 40.0) & (rsi.shift(1).iloc[-1]>=44.0))
#              & (pvt.iloc[-1] < pvt.shift(1).iloc[-1])):
#            crossover_value = -1
#        else:
#            crossover_value = 0
#        return crossover_value


    def strategy_select_instruments_for_entry(self, candle, instruments_bucket):

        selected_instruments_bucket = []
        sideband_info_bucket = []

        for instrument in instruments_bucket:
            crossover_value = self.get_crossover_value(instrument)
            if crossover_value == 1:
                selected_instruments_bucket.append(instrument)
                sideband_info_bucket.append({'action': 'BUY'})
            elif crossover_value == -1:
                if self.strategy_mode is StrategyMode.INTRADAY:
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'SELL'})

        return selected_instruments_bucket, sideband_info_bucket

    def strategy_enter_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'BUY':
            qty = self.number_of_lots * instrument.lot_size
            self.main_order[instrument] = \
                self.broker.BuyOrderRegular(instrument=instrument,
                                            order_code=BrokerOrderCodeConstants.INTRADAY,
                                            order_variety=BrokerOrderVarietyConstants.MARKET,
                                            quantity=qty)
        elif sideband_info['action'] == 'SELL':
            qty = self.number_of_lots * instrument.lot_size
            self.main_order[instrument] = \
                self.broker.SellOrderRegular(instrument=instrument,
                                             order_code=BrokerOrderCodeConstants.INTRADAY,
                                             order_variety=BrokerOrderVarietyConstants.MARKET,
                                             quantity=qty)
        else:
            raise SystemExit(f'Got invalid sideband_info value: {sideband_info}')

        return self.main_order[instrument]

    def strategy_select_instruments_for_exit(self, candle, instruments_bucket):
        selected_instruments_bucket = []
        sideband_info_bucket = []

        for instrument in instruments_bucket:
            if self.main_order.get(instrument) is not None:
                crossover_value = self.get_crossover_value(instrument)
                if crossover_value in [1, -1]:
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'EXIT'})
        return selected_instruments_bucket, sideband_info_bucket

    def strategy_exit_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'EXIT':
            self.main_order[instrument].exit_position()
            self.main_order[instrument] = None
            return True

        return False
