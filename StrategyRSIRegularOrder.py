#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 09:35:13 2020

@author: gb
"""

from pyalgotrading.strategy.strategy_base import StrategyBase
from pyalgotrading.constants import *
from pyalgotrading import constants


class StrategyRSIRegularOrder(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.timeperiod1 = self.strategy_parameters['RSI']
        self.timeperiod2 = self.strategy_parameters['EMA_1']
        self.timeperiod3 = self.strategy_parameters['EMA_2']
        self.main_order = None  # empty dict

    def initialize(self):
        self.main_order = {}

    @staticmethod
    def name():
        return 'RSI Regular Order Strategy'

    @staticmethod
    def versions_supported():
        return AlgoBullsEngineVersion.VERSION_3_2_0

    def get_rsi_value(self, instrument):
        hist_data = self.get_historical_data(instrument)
        rsi_value = (talib.RSI(hist_data['close'], timeperiod=self.timeperiod1)
                     .fillna(0)
                     .round())
        rsiSell = ((rsi_value.iloc[-1] > 70.0) & (rsi_value.shift(1).iloc[-1] <= 70))
        rsiBuy = ((rsi_value.iloc[-1] < 30) & (rsi_value.shift(1).iloc[-1] >= 30))
        return rsiBuy, rsiSell

    # def get_macd_value(self, instrument):
    #     pass
    #     return pass

    def get_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)
        ema_x = talib.EMA(hist_data['close'], timeperiod=self.timeperiod2)
        ema_y = talib.EMA(hist_data['close'], timeperiod=self.timeperiod3)
        crossover_value = self.utils.crossover(ema_x, ema_y)
        return crossover_value

    def strategy_select_instruments_for_entry(self, candle, instruments_bucket):
        selected_instruments_bucket = []
        sideband_info_bucket = []

        for instrument in instruments_bucket:
            rsiBuy, rsiSell = self.get_rsi_value(instrument)
            crossover_value = self.get_crossover_value(instrument)

            if (rsiBuy and crossover_value == 1):
                selected_instruments_bucket.append(instrument)
                sideband_info_bucket.append({'action': 'BUY'})
            elif (rsiSell and crossover_value == -1):
                if self.strategy_mode is StrategyMode.INTRADAY:
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'SELL'})
        return selected_instruments_bucket, sideband_info_bucket


    def strategy_enter_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'BUY':
            qty = self.number_of_lots * instrument.lot_size
            self.main_order[instrument] = \
            self.broker.BuyOrderRegular(instrument=instrument,order_code=BrokerOrderCodeConstants.INTRADAY,
                                 order_variety=BrokerOrderVarietyConstants.MARKET, quantity=qty)
        if sideband_info['action'] == 'SELL':
            qty = self.number_of_lots * instrument.lot_size
            self.main_order[instrument] = \
                self.broker.SellOrderRegular(instrument=instrument,
                                      order_code=BrokerOrderCodeConstants.INTRADAY,
                                      order_variety=BrokerOrderVarietyConstants.MARKET,
                                      quantity=qty)
        else:
            raise SystemExit(f'Got invalid sideband_info value:{sideband_info}')
            return self.main_order[instrument]

    def strategy_select_instruments_for_exit(self, candle, instruments_bucket):
        selected_instruments_bucket = []
        sideband_info_bucket = []

        for instrument in instruments_bucket:
            if self.main_order.get(instrument) is not None:
                rsiBuy, rsiSell = self.get_rsi_value(instrument)
                crossover_value = self.get_crossover_value(instrument)
                if ((rsiBuy and crossover_value == 1) or (rsiSell and crossover_value == -1)):
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'EXIT'})
        return selected_instruments_bucket, sideband_info_bucket

    def strategy_exit_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'EXIT':
            self.main_order[instrument].exit_position()
            self.main_order[instrument] = None
            return True
        return False