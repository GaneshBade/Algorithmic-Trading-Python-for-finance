from pyalgotrading.strategy.strategy_base import StrategyBase
from pyalgotrading.constants import *
import pandas


class StrategyRSICrossoverBracketOrder(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        # timeperiod variables
        self.RSI_PERIOD = self.strategy_parameters['RSI_PERIOD'] #14 days
        self.RSI_AVG_PERIOD = self.strategy_parameters['RSI_AVG_PERIOD'] #9 days

        self.ROCP_PERIOD = self.strategy_parameters['ROCP_PERIOD']  # 9 days
        self.ROCP_AVG_PERIOD = self.strategy_parameters['ROCP_AVG_PERIOD']  # 5 days

        self.HILO_HIGH_PERIOD = self.strategy_parameters['HILO_HIGH_PERIOD']  # 3 days
        self.HILO_LOW_PERIOD = self.strategy_parameters['HILO_LOW_PERIOD']  # 3 days

        self.MACD_FAST_PERIOD = self.strategy_parameters['MACD_FAST_PERIOD']  # 9 days
        self.MACD_SLOW_PERIOD = self.strategy_parameters['MACD_SLOW_PERIOD']  # 24 days
        self.MACD_SIGNAL_PERIOD = self.strategy_parameters['MACD_SIGNAL_PERIOD']  # 9 days

        # Order variables
        self.stoploss = self.strategy_parameters['stoploss_trigger']
        self.target = self.strategy_parameters['target_trigger']
        self.trailing_stoploss = self.strategy_parameters['trailing_stoploss_trigger']

        self.main_order = None  # empty dict

    def initialize(self):
        self.main_order = {}
        import pandas

    @staticmethod
    def name():
        return 'RSI Crossover Bracket Order Strategy'

    @staticmethod
    def versions_supported():
        return AlgoBullsEngineVersion.VERSION_3_2_0

    def get_rsi_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        rsi = talib.RSI(hist_data['close'], timeperiod=self.RSI_PERIOD)
        rsi_ema = talib.EMA(rsi, timeperiod=self.RSI_AVG_PERIOD)
        rsi_cv = self.utils.crossover(rsi, rsi_ema)

        return rsi_cv

    def get_rocp_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        rocp = talib.ROCP(hist_data['close'], timeperiod=self.ROCP_PERIOD)
        rocp_ema = talib.EMA(rocp, timeperiod=self.ROCP_AVG_PERIOD)
        rocp_cv = self.utils.crossover(rocp, rocp_ema)
        #rocp_cv_prev = self.utils.crossover(rocp.shift(1), rocp_ema.shift(1))
        return rocp_cv

    def GannHilo(self, high, low, close, high_length=None, low_length=None):
        """Indicator: Gann HiLo (HiLo) Activator"""
        high_length = int(high_length) if high_length and high_length > 0 else 3
        low_length = int(low_length) if low_length and low_length > 0 else 3

        # Calculate Result
        m = close.size
        hilo = talib._ta_lib.pandas.Series(talib._ta_lib.numpy.NaN, index=close.index)

        high_ma = talib.SMA(high, timeperiod=high_length)
        low_ma = talib.SMA(low, timeperiod=low_length)

        for i in range(1, m):
            if close.iloc[i] > high_ma.iloc[i - 1]:
                hilo.iloc[i] = low_ma.iloc[i]
            elif close.iloc[i] < low_ma.iloc[i - 1]:
                hilo.iloc[i] = high_ma.iloc[i]
            else:
                hilo.iloc[i] = hilo.iloc[i - 1]

        return hilo

    def get_Gann_Hilo_Value(self, instrument):
        hist_data = self.get_historical_data(instrument)
        hilo = self.GannHilo(high=hist_data['high'], low=hist_data['low'], close=hist_data['close'], high_length=self.HILO_HIGH_PERIOD, low_length=self.HILO_LOW_PERIOD)

        if (hist_data['close'].iloc[-1] > hilo.iloc[-1]):
            hilo_value = 1
        elif (hist_data['open'].iloc[-1] < hilo.iloc[-1]):
            hilo_value = -1
        else:
            hilo_value = 0
        return hilo_value

    def get_macd_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        macd, macdsignal, macdhist = talib.MACDEXT(hist_data['close'],fastperiod=self.MACD_FAST_PERIOD, \
                             slowperiod=self.MACD_SLOW_PERIOD, signalperiod=self.MACD_SIGNAL_PERIOD)
        macd_cv = self.utils.crossover(macd, macdsignal)

        return macd_cv, macdhist

    def get_STOCH_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        slowk, slowd = talib.STOCH(high=hist_data['high'], low=hist_data['low'], close=hist_data['close'], \
                                    fastk_period=5, slowk_period=3, slowk_matype=1, slowd_period=3, slowd_matype=1)
        #fastk_ema = talib.EMA(slowk, timeperiod=3)
        stoch_cv = self.utils.crossover(slowk, slowd)

        return stoch_cv

    def strategy_select_instruments_for_entry(self, candle, instruments_bucket):

        selected_instruments_bucket = []
        sideband_info_bucket = []

        for instrument in instruments_bucket:
            rsi_cv = self.get_rsi_crossover_value(instrument)
            #rocp_cv = self.get_rocp_crossover_value(instrument)

            if rsi_cv == 1:
                selected_instruments_bucket.append(instrument)
                sideband_info_bucket.append({'action': 'BUY'})
            elif rsi_cv == -1:
                if self.strategy_mode is StrategyMode.INTRADAY:
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'SELL'})

        return selected_instruments_bucket, sideband_info_bucket

    def strategy_enter_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'BUY':
            # qty = self.number_of_lots * instrument.lot_size
            qty = 1400
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
            qty=1400
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
                rsi_cv = self.get_rsi_crossover_value(instrument)
                stoch_cv = self.get_STOCH_crossover_value(instrument)
                rocp_cv = self.get_rocp_crossover_value(instrument)
                if ((rocp_cv in [1, -1]) or (rsi_cv in [1, -1])):
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'EXIT'})
        return selected_instruments_bucket, sideband_info_bucket

    def strategy_exit_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'EXIT':
            self.main_order[instrument].exit_position()
            self.main_order[instrument] = None
            return True

        return False
