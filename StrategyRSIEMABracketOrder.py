from pyalgotrading.strategy.strategy_base import StrategyBase
from pyalgotrading.constants import *

class StrategyRSIEMABracketOrder(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # timeperiod variables
        self.RSI_PERIOD = self.strategy_parameters['RSI_PERIOD']          # 14 days
        self.RSI_AVG_PERIOD = self.strategy_parameters['RSI_AVG_PERIOD']  # 9 days

        self.ROCP_PERIOD = self.strategy_parameters['ROCP_PERIOD']  # 10 days
        self.ROCP_AVG_PERIOD = self.strategy_parameters['ROCP_AVG_PERIOD']  # 9 days

        self.AD_AVG_PERIOD = self.strategy_parameters['AD_AVG_PERIOD']  # 5 or 9 days

        self.MFI_PERIOD = self.strategy_parameters['MFI_PERIOD']  # 10 days
        self.MFI_AVG_PERIOD = self.strategy_parameters['MFI_AVG_PERIOD']  # 9 days

        self.MACD_FAST_PERIOD = self.strategy_parameters['MACD_FAST_PERIOD']  # 12 days
        self.MACD_SLOW_PERIOD = self.strategy_parameters['MACD_SLOW_PERIOD']  # 29 days
        self.MACD_SIGNAL_PERIOD = self.strategy_parameters['MACD_SIGNAL_PERIOD']  # 9 days

        self.HILO_HIGH_PERIOD = self.strategy_parameters['HILO_HIGH_PERIOD']  # 3 days
        self.HILO_LOW_PERIOD = self.strategy_parameters['HILO_LOW_PERIOD']  # 3 days

        # Order variables
        self.stoploss = self.strategy_parameters['stoploss_trigger']
        self.target = self.strategy_parameters['target_trigger']
        self.trailing_stoploss = self.strategy_parameters['trailing_stoploss_trigger']

        self.main_order = None

        self.check_buy_sell = None

    def initialize(self):
        self.main_order = {}
        self.check_buy_sell = {}

    @staticmethod
    def name():
        return 'RSI & EMA Bracket Order Strategy'

    @staticmethod
    def versions_supported():
        return AlgoBullsEngineVersion.VERSION_3_2_0


    def get_rsi_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        rsi = talib.RSI(hist_data['close'], timeperiod=self.RSI_PERIOD)
        ema = talib.EMA(rsi, timeperiod=self.RSI_AVG_PERIOD)
        rsi_cv = self.utils.crossover(rsi, ema)
        rsi_cv_prev = rsi.shift(1).iloc[-1]

        return rsi_cv,rsi_cv_prev

    def get_rocp_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        rocp = talib.ROCP(hist_data['close'], timeperiod=self.ROCP_PERIOD)
        rocp_ema = talib.EMA(rocp, timeperiod=self.ROCP_AVG_PERIOD)
        rocp_cv = self.utils.crossover(rocp, rocp_ema)
        rocp_cv_prev = self.utils.crossover(rocp.shift(1), rocp_ema.shift(1))
        return rocp_cv, rocp_cv_prev

    def get_ad_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        ad = talib.AD(hist_data['high'], hist_data['low'], hist_data['close'],hist_data['volume'])
        ad_ema = talib.EMA(ad, timeperiod=self.AD_AVG_PERIOD)
        ad_cv = self.utils.crossover(ad, ad_ema)
        ad_cv_prev = self.utils.crossover(ad.shift(1), ad_ema.shift(1))

        return ad_cv, ad_cv_prev

    def get_mfi_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        mfi = talib.MFI(hist_data['high'], hist_data['low'], hist_data['close'],hist_data['volume'], \
                        timeperiod=self.MFI_PERIOD)
        mfi_ema = talib.EMA(mfi, timeperiod=self.MFI_AVG_PERIOD)
        mfi_ema_x = talib.EMA(mfi_ema, timeperiod=3)
        mfi_cv = self.utils.crossover(mfi_ema, mfi_ema_x)

        return mfi_cv

    def get_macd_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        macd, macdsignal, macdhist = talib.MACDEXT(hist_data['close'],fastperiod=self.MACD_FAST_PERIOD, \
                             slowperiod=self.MACD_SLOW_PERIOD, signalperiod=self.MACD_SIGNAL_PERIOD)
        # macd = talib.EMA(macd, timeperiod=9)
        # macdsignal = talib.EMA(macdsignal, timeperiod=9)
        # macdhist = talib.EMA(macdhist, timeperiod=9)
        macd_cv = self.utils.crossover(macd, macdsignal)

        # macd, macdsignal, macdhist = talib.MACDEXT(hist_data['close'],fastperiod=self.MACD_FAST_PERIOD, \
        #                      slowperiod=self.MACD_SLOW_PERIOD, signalperiod=self.MACD_SIGNAL_PERIOD)
        # macd_cv = self.utils.crossover(macd, macdsignal)

        # macd, macdsignal, macdhist = talib.MACDEXT(hist_data['close'],fastperiod=self.MACD_FAST_PERIOD, \
        #                      slowperiod=self.MACD_SLOW_PERIOD, signalperiod=self.MACD_SIGNAL_PERIOD)
        # macd_cv = self.utils.crossover(macd, macdsignal)

        # macd, macdsignal, macdhist = talib.MACDEXT(hist_data['close'],fastperiod=self.MACD_FAST_PERIOD, \
        #                      slowperiod=self.MACD_SLOW_PERIOD, signalperiod=self.MACD_SIGNAL_PERIOD)
        # macd_cv = self.utils.crossover(macd, macdsignal)

        return macd_cv, macdhist

    def get_candle_color(self, instrument):
        hist_data = self.get_historical_data(instrument)

        green_candle = hist_data['close'].iloc[-1] > hist_data['open'].iloc[-1]
        prev_green_candle = hist_data['close'].shift(1).iloc[-1] > hist_data['open'].shift(1).iloc[-1]
        red_candle = hist_data['close'].iloc[-1] < hist_data['open'].iloc[-1]
        prev_red_candle = hist_data['close'].shift(1).iloc[-1] < hist_data['open'].shift(1).iloc[-1]

        if green_candle:
            candle = 1
        elif red_candle:
            candle = -1
        else:
            candle = 0
        return candle

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

        if (hist_data['open'].iloc[-1] > hilo.iloc[-1]):
            hilo_value = 1
        elif (hist_data['open'].iloc[-1] < hilo.iloc[-1]):
            hilo_value = -1
        else:
            hilo_value = 0
        return hilo_value

    def get_DEMA_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)
        dema_x = talib.DEMA(hist_data['close'], timeperiod=3)
        dema_y = talib.DEMA(hist_data['close'], timeperiod=5)
        dema_cv = self.utils.crossover(dema_x, dema_y)

        return dema_cv

    def vwma(self, close, volume, timeperiod=None):
        """Indicator: Volume Weighted Moving Average (VWMA)"""
        # Validate Arguments
        timeperiod = int(timeperiod) if timeperiod and timeperiod > 0 else 5

        # Calculate Result
        pv = close * volume
        vwma = (talib.SMA(pv, timeperiod=timeperiod) / talib.SMA(volume, timeperiod=timeperiod))

        return vwma

    def getVWMA_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)
        vwma = self.vwma(close=hist_data['close'], volume=hist_data['volume'], timeperiod=5)
        vwma_ema = talib.EMA(vwma, timeperiod=3)
        vwma_cv = self.utils.crossover(vwma, vwma_ema)

        return vwma_cv

    def getHaramiCandle(self,instrument):
        hist_data = self.get_historical_data(instrument)
        harami = talib.CDLHARAMI(hist_data['open'], hist_data['high'], hist_data['low'], hist_data['close'])
        return harami

    def getEngulfingCandle(self,instrument):
        hist_data = self.get_historical_data(instrument)
        engulfing = talib.CDLENGULFING(hist_data['open'], hist_data['high'], hist_data['low'], hist_data['close'])
        return engulfing

    def getBuySellSignal(self, instrument):
        rsi_cv, rsi_cv_prev = self.get_rsi_crossover_value(instrument)
        rocp_cv, rocp_cv_prev = self.get_rocp_crossover_value(instrument)
        macd_cv, macdhist = self.get_macd_crossover_value(instrument)
        hilo_value = self.get_Gann_Hilo_Value(instrument)
        mfi_cv = self.get_mfi_crossover_value(instrument)
        dema_cv = self.get_DEMA_crossover_value(instrument)
        vwma_cv = self.getVWMA_crossover_value(instrument)
        harami = self.getHaramiCandle(instrument)
        engulfing = self.getEngulfingCandle(instrument)

        if ((rsi_cv == 1) & (macd_cv == 1)):
            rsi_macd = 1
        elif ((rsi_cv == -1) and (macd_cv == -1)):
            rsi_macd = -1
        else:
            rsi_macd = 0

        if ((mfi_cv == 1) and (vwma_cv == 1)):
            mfi_vwma = 1
        elif ((mfi_cv == -1) and (vwma_cv == -1)):
            mfi_vwma = -1
        else:
            mfi_vwma = 0

        if ((rsi_cv == 1) and (harami.iloc[-1] == 100)):
            rsi_harami = 1
        elif ((rsi_cv == -1) and (harami.iloc[-1] == -100)):
            rsi_harami = -1
        else:
            rsi_harami = 0

        if ((rsi_cv == 1) and (engulfing.iloc[-1] == 100)):
            rsi_engulfing = 1
        elif ((rsi_cv == -1) and (engulfing.iloc[-1] == -100)):
            rsi_engulfing = -1
        else:
            rsi_engulfing = 0

        return rsi_macd, mfi_vwma, rsi_harami, rsi_engulfing

    def strategy_select_instruments_for_entry(self, candle, instruments_bucket):

        selected_instruments_bucket = []
        sideband_info_bucket = []

        for instrument in instruments_bucket:
            #rsi_cv, rsi_cv_prev = self.get_rsi_crossover_value(instrument)
            #rocp_cv, rocp_cv_prev = self.get_rocp_crossover_value(instrument)
            # ad_cv, ad_cv_prev = self.get_ad_crossover_value(instrument)
            #macd_cv, macdhist = self.get_macd_crossover_value(instrument)
            #hilo_value = self.get_Gann_Hilo_Value(instrument)
            #mfi_cv = self.get_mfi_crossover_value(instrument)
            rsi_macd, mfi_vwma, rsi_harami, rsi_engulfing = self.getBuySellSignal(instrument)
            if ((rsi_macd == 1) and (mfi_vwma == 1)):
                selected_instruments_bucket.append(instrument)
                sideband_info_bucket.append({'action': 'BUY'})
            elif ((rsi_macd == -1) and (mfi_vwma == -1)):
                if self.strategy_mode is StrategyMode.INTRADAY:
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'SELL'})

        return selected_instruments_bucket, sideband_info_bucket

    def strategy_enter_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'BUY':
            # qty = self.number_of_lots * instrument.lot_size
            qty = 200
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
            self.check_buy_sell[instrument] = "BUY"

        elif sideband_info['action'] == 'SELL':
            # qty = self.number_of_lots * instrument.lot_size
            qty = 200
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
            self.check_buy_sell[instrument] = "SELL"
        else:
            raise SystemExit(f'Got invalid sideband_info value: {sideband_info}')

        return self.main_order[instrument]

    def strategy_select_instruments_for_exit(self, candle, instruments_bucket):
        selected_instruments_bucket = []
        sideband_info_bucket = []

        for instrument in instruments_bucket:
            if self.main_order.get(instrument) is not None:
                rsi_cv, rsi_cv_prev = self.get_rsi_crossover_value(instrument)
                # ad_cv, ad_cv_prev = self.get_ad_crossover_value(instrument)
                rocp_cv, rocp_cv_prev = self.get_rocp_crossover_value(instrument)
                #mfi_cv = self.get_mfi_crossover_value(instrument)
                # pvol_value = self.get_price_volume_value(instrument)
                #macd_cv = self.get_macd_crossover_value(instrument)
                #mfi_cv = self.get_mfi_crossover_value(instrument)
                #hilo_value = self.get_Gann_Hilo_Value(instrument)
                if ((rsi_cv in [1, -1]) or (rocp_cv in [1, -1])):
                    selected_instruments_bucket.append(instrument)
                    sideband_info_bucket.append({'action': 'EXIT'})
        return selected_instruments_bucket, sideband_info_bucket

    def strategy_exit_position(self, candle, instrument, sideband_info):
        if sideband_info['action'] == 'EXIT':
            self.main_order[instrument].exit_position()
            self.main_order[instrument] = None
            self.check_buy_sell[instrument] = None
            return True

        return False
