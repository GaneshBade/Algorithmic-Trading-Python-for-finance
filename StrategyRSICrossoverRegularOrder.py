from pyalgotrading.strategy.strategy_base import StrategyBase
from pyalgotrading.constants import *
from pyalgotrading import constants


class StrategyRSICrossoverRegularOrder(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.RSI_PERIOD = self.strategy_parameters['RSI_PERIOD'] #14 days
        self.RSI_AVG_PERIOD = self.strategy_parameters['RSI_AVG_PERIOD'] #9 days

        self.HILO_HIGH_PERIOD = self.strategy_parameters['HILO_HIGH_PERIOD']  # 3 days
        self.HILO_LOW_PERIOD = self.strategy_parameters['HILO_LOW_PERIOD']  # 3 days

        self.MACD_FAST_PERIOD = self.strategy_parameters['MACD_FAST_PERIOD']  # 12 days
        self.MACD_SLOW_PERIOD = self.strategy_parameters['MACD_SLOW_PERIOD']  # 24 days
        self.MACD_SIGNAL_PERIOD = self.strategy_parameters['MACD_SIGNAL_PERIOD']  # 9 days

        self.main_order = None  # empty dict

    def initialize(self):
        self.main_order = {}

    @staticmethod
    def name():
        return 'RSI crossover Strategy'

    @staticmethod
    def versions_supported():
        return AlgoBullsEngineVersion.VERSION_3_2_0

    def get_rsi_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        rsi = (talib.RSI(hist_data['close'], timeperiod=self.RSI_PERIOD)
                     .fillna(0))
        rsi_ema = (talib.EMA(rsi, timeperiod=self.RSI_AVG_PERIOD)
                   .fillna(0))

        rsi_cv = self.utils.crossover(rsi, rsi_ema)

        rsi_c = rsi.iloc[-1]
        rsi_p = rsi.shift(1).iloc[-1]
        rsi_2p = rsi.shift(2).iloc[-1]

        if ((rsi_cv == 1) &
            (((rsi_c > 40) | (rsi_c < 30)) & ((rsi_c > rsi_p) | (rsi_c > rsi_2p)))
            ):
            rsi_buy = 1
        elif ((rsi_cv == 1) &
              (((rsi_c > 40) | (rsi_c < 30)) & ((rsi_c > rsi_p) | (rsi_c > rsi_2p)))
             ):
            rsi_sell = 1
        else:
            rsi_buy = 0
            rsi_sell = 0


        return rsi_cv

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
            macd_cv, macdhist = self.get_macd_crossover_value(instrument)

            if ((rsi_cv == 1) & (macdhist.iloc[-1] > 0)):
                selected_instruments_bucket.append(instrument)
                sideband_info_bucket.append({'action': 'BUY'})
            elif ((rsi_cv == -1) & (macdhist.iloc[-1] < 0)):
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
                stoch_cv = self.get_STOCH_crossover_value(instrument)
                rsi_cv = self.get_rsi_crossover_value(instrument)
                if ((stoch_cv in [1, -1]) or (rsi_cv in [1, -1])):
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'EXIT'})
        return selected_instruments_bucket, sideband_info_bucket

    def strategy_exit_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'EXIT':
            self.main_order[instrument].exit_position()
            self.main_order[instrument] = None
            return True
        return False
