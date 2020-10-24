#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 08:19:45 2020

@author: gb
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 09:29:06 2020

@author: gb
"""
from pyalgotrading.strategy.strategy_base import StrategyBase
from pyalgotrading.constants import *


class StrategyKSTROCEMABracketOrder(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # timeperiod variables
        self.ROC_Period1 = self.strategy_parameters['ROC_Period1']  # 6 days
        self.ROC_Period2 = self.strategy_parameters['ROC_Period2']  # 12 days
        self.ROC_Period3 = self.strategy_parameters['ROC_Period3']  # 18 days
        self.ROC_Period4 = self.strategy_parameters['ROC_Period4']  # 24 days

        self.ROC_SMA_Period1 = self.strategy_parameters['ROC_SMA_Period1']  # 10 days
        self.ROC_SMA_Period2 = self.strategy_parameters['ROC_SMA_Period2']  # 10 days
        self.ROC_SMA_Period3 = self.strategy_parameters['ROC_SMA_Period3']  # 10 days
        self.ROC_SMA_Period4 = self.strategy_parameters['ROC_SMA_Period4']  # 15 days

        self.RSI_AVG_PERIOD = self.strategy_parameters['RSI_AVG_PERIOD']  # 9 days

        # self.ROC_AVG_PERIOD = self.strategy_parameters['ROC_AVG_PERIOD']  # 9 days

        # self.PVT_PERIOD = self.strategy_parameters['PVT_PERIOD']          # 30 days
        # self.PVT_AVG_PERIOD = self.strategy_parameters['PVT_AVG_PERIOD']  # 8 days

        self.ROCP_PERIOD = self.strategy_parameters['ROCP_PERIOD']  # 10 days
        self.ROCP_AVG_PERIOD = self.strategy_parameters['ROCP_AVG_PERIOD']  # 9 days

        # Order variables
        self.stoploss = self.strategy_parameters['stoploss_trigger']
        self.target = self.strategy_parameters['target_trigger']
        self.trailing_stoploss = self.strategy_parameters['trailing_stoploss_trigger']

        self.main_order = None

    def initialize(self):
        self.main_order = {}

    @staticmethod
    def name():
        return 'RSI & EMA Bracket Order Strategy'

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

        volume_up = ((hist_data['volume'] > hist_data['volume'].shift(1)) & (hist_data['volume'].shift(1) > hist_data['volume'].shift(2)))

        volume_down = ((hist_data['volume'] < hist_data['volume'].shift(1)) & (hist_data['volume'].shift(1) < hist_data['volume'].shift(2)))

        obv = talib.OBV(hist_data['close'], hist_data['volume'])

        mfi = talib.MFI(hist_data['high'], hist_data['low'], hist_data['close'], hist_data['volume'], timeperiod=14)
        mfi_ema = talib.EMA(mfi, timeperiod=9)

        pvt = ((talib.ROC(hist_data['close'], timeperiod=30))
              * hist_data['volume']).cumsum()
        pvt_ema = talib.EMA(pvt, timeperiod=8)

        rocp = talib.ROCP(hist_data['close'], timeperiod=self.ROCP_PERIOD)
        rocp_ema = talib.EMA(rocp, timeperiod=self.ROCP_AVG_PERIOD)
        rocp_crossover_value = self.utils.crossover(rocp, rocp_ema)
        rocp_crossover_value_prev = self.utils.crossover(rocp.shift(1), rocp_ema.shift(1))

        rsi_rocp_buy_cond = ((rsi_crossover_value == 1) & (rocp_crossover_value == 1 | rocp_crossover_value_prev == 1))

        rsi_rocp_sell_cond = ((rsi_crossover_value == -1) & (rocp_crossover_value == -1 | rocp_crossover_value_prev == -1))

        buy_on_less_rsi = (rsi.iloc[-1] < rsi.shift(2).iloc[-1])
        sell_on_high_rsi = (rsi.iloc[-1] > rsi.shift(2).iloc[-1])

        if (rsi_rocp_buy_cond):
            crossover_value = 1
        elif (rsi_rocp_sell_cond):
            crossover_value = -1
        else:
            crossover_value = 0
        return crossover_value

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
        # if ((((((rsi_crossover_value == 1) & (rocp_crossover_value == 1)) | ((rsi_crossover_value_prev == 1) & (rocp_crossover_value_prev == 1))) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34))) & (volume_up.iloc[-1])) & (obv.iloc[-1] > (obv.shift(1).iloc[-1] + obv.shift(2).iloc[-1]/2))):
        #       crossover_value = 1
        # elif ((((((rsi_crossover_value == -1) & (rocp_crossover_value == -1)) | ((rsi_crossover_value_prev == -1) & (rocp_crossover_value_prev == -1))) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34))) & (volume_down.iloc[-1])) & (obv.iloc[-1] < (obv.shift(1).iloc[-1] + obv.shift(2).iloc[-1]/2))):
        #     crossover_value = -1
        # else:
        #       crossover_value = 0

        # return crossover_value

        # rsi_buy_cond = ((rsi_crossover_value == 1) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34)))
        # mfi_buy_cond1 = (mfi.iloc[-1] > mfi_ema.iloc[-1])
        # mfi_buy_cond2 = (mfi.shift(1).iloc[-1] > mfi_ema.shift(1).iloc[-1])

        # rsi_sell_cond = ((rsi_crossover_value == -1) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34)))
        # mfi_sell_cond1 = (mfi.iloc[-1] < mfi_ema.iloc[-1])
        # mfi_sell_cond2 = (mfi.shift(1).iloc[-1] < mfi_ema.shift(1).iloc[-1])

        # if (((((rsi_crossover_value == 1 | rsi_crossover_value_prev == 1) & (rocp_crossover_value == 1 | rocp_crossover_value_prev == 1))) & (volume_up.iloc[-1])) & (mfi_buy_cond1)):
        #       crossover_value = 1
        # elif (((((rsi_crossover_value == -1 | rsi_crossover_value_prev == -1) & (rocp_crossover_value == -1 | rocp_crossover_value_prev == -1))) & (volume_down.iloc[-1])) & (mfi_sell_cond1)):
        #     crossover_value = -1
        # else:
        #      crossover_value = 0
        # if ((((rsi_crossover_value == 1) & (rocp_crossover_value == 1 | rocp_crossover_value_prev == 1))
        #        & (volume_up.iloc[-1])) & (mfi.iloc[-1] > mfi_ema.iloc[-1])):
        #       crossover_value = 1
        # elif ((((rsi_crossover_value == -1) & (rocp_crossover_value == -1 | rocp_crossover_value_prev == -1))
        #        & (volume_down.iloc[-1])) & (mfi.iloc[-1] < mfi_ema.iloc[-1])):
        #     crossover_value = -1

        # if ((((rsi_crossover_value == 1) & (rocp_crossover_value == 1)) | ((rsi_crossover_value_prev == 1) & (rocp_crossover_value_prev == 1))) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34))):
        #       crossover_value = 1
        # elif ((((rsi_crossover_value == -1) & (rocp_crossover_value == -1)) | ((rsi_crossover_value_prev == -1) & (rocp_crossover_value_prev == -1))) & ((rsi.iloc[-1]<=28) | (rsi.iloc[-1]>=34))):
        #     crossover_value = -1
        # else:
        #      crossover_value = 0

        # return crossover_value

        # if ((rsi_crossover_value == 1) & ((rsi.iloc[-1]<=23) | (rsi.iloc[-1]>=35))):
        #       crossover_value = 1
        # elif ((rsi_crossover_value == -1) & ((rsi.iloc[-1]<=23) | (rsi.iloc[-1]>=35))):
        #     crossover_value = -1
        # else:
        #      crossover_value = 0

        # return crossover_value

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
            # qty = self.number_of_lots * instrument.lot_size
            qty = 3100
            ltp = self.broker.get_ltp(instrument)
            self.main_order[instrument] = \
                self.broker.BuyOrderBracket(instrument=instrument,
                                            order_code=BrokerOrderCodeConstants.INTRADAY,
                                            order_variety=BrokerOrderVarietyConstants.LIMIT,
                                            quantity=qty,
                                            price=ltp,
                                            stoploss_trigger=ltp - (ltp * self.stoploss),
                                            target_trigger=ltp + (ltp * self.target),
                                            trailing_stoploss_trigger=ltp * self.trailing_stoploss)

        elif sideband_info['action'] == 'SELL':
            # qty = self.number_of_lots * instrument.lot_size
            qty = 3100
            ltp = self.broker.get_ltp(instrument)
            self.main_order[instrument] = \
                self.broker.SellOrderBracket(instrument=instrument,
                                             order_code=BrokerOrderCodeConstants.INTRADAY,
                                             order_variety=BrokerOrderVarietyConstants.LIMIT,
                                             quantity=qty,
                                             price=ltp,
                                             stoploss_trigger=ltp + (ltp * self.stoploss),
                                             target_trigger=ltp - (ltp * self.target),
                                             trailing_stoploss_trigger=ltp * self.trailing_stoploss)
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
