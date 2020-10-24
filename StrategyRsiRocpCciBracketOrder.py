from pyalgotrading.strategy.strategy_base import StrategyBase
from pyalgotrading.constants import *
import pandas


class StrategyRSIROCPCCIBracketOrder(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # timeperiod variables
        self.RSI_PERIOD = self.strategy_parameters['RSI_PERIOD']          # 14 days

        self.RSI_AVG_PERIOD = self.strategy_parameters['RSI_AVG_PERIOD']  # 9 days

        # self.ROC_AVG_PERIOD = self.strategy_parameters['ROC_AVG_PERIOD']  # 9 days

        # self.PVT_PERIOD = self.strategy_parameters['PVT_PERIOD']          # 30 days
        # self.PVT_AVG_PERIOD = self.strategy_parameters['PVT_AVG_PERIOD']  # 8 days

        self.ROCP_PERIOD = self.strategy_parameters['ROCP_PERIOD']  # 10 days
        self.ROCP_AVG_PERIOD = self.strategy_parameters['ROCP_AVG_PERIOD']  # 9 days

        self.MFI_PERIOD = self.strategy_parameters['MFI_PERIOD']  # 10 days
        self.MFI_AVG_PERIOD = self.strategy_parameters['MFI_AVG_PERIOD']  # 9 days

        self.OBV_AVG_PERIOD = self.strategy_parameters['OBV_AVG_PERIOD'] # 5 days

        # Order variables
        self.stoploss = self.strategy_parameters['stoploss_trigger']
        self.target = self.strategy_parameters['target_trigger']
        self.trailing_stoploss = self.strategy_parameters['trailing_stoploss_trigger']

        self.main_order = None

    def initialize(self):
        self.main_order = {}
        import pandas

    @staticmethod
    def name():
        return 'RSI, ROCP & CCI Bracket Order Strategy'

    @staticmethod
    def versions_supported():
        return AlgoBullsEngineVersion.VERSION_3_2_0

    def verify_series(series:pandas.Series):
        """If a Pandas Series return it."""
        if series is not None and isinstance(series, pandas.core.series.Series):
            return series

    def get_offset(x:int):
        """Returns an int, otherwise defaults to zero."""
        return int(x) if x else 0

    def zero(x):
        """If the value is close to zero, then return zero.  Otherwise return the value."""
        return 0 if -sys.float_info.epsilon < x and x < sys.float_info.epsilon else x

    def cross(series_a:pandas.Series, series_b:pandas.Series, above:bool =True, asint:bool =True, offset:int =None, **kwargs):
        series_a = verify_series(series_a)
        series_b = verify_series(series_b)
        offset = get_offset(offset)

        series_a.apply(zero)
        series_b.apply(zero)

        # Calculate Result
        current = series_a > series_b   # current is above
        previous = series_a.shift(1) < series_b.shift(1) # previous is below
        # above if both are true, below if both are false
        cross = current & previous if above else ~current & ~previous

        if asint:
            cross = cross.astype(int)

        # Offset
        if offset != 0:
            cross = cross.shift(offset)

        # Name & Category
        cross.name = f"{series_a.name}_{'XA' if above else 'XB'}_{series_b.name}"
        cross.category = 'utility'

        return cross

    def get_crossover_value(self, instrument):
        hist_data = self.get_historical_data(instrument)

        rsi = talib.RSI(hist_data['close'], timeperiod=self.RSI_PERIOD)
        ema = talib.EMA(rsi, timeperiod=self.RSI_AVG_PERIOD)
        rsi_cv = self.utils.crossover(rsi, ema)

        rsi_cv_gb = self.cross(series_a=rsi, series_b=rsi_ema, above=True)
        cross_down = self.cross(series_a=rsi, series_b=rsi_ema, above=False)
        cross_down.replace(1, -1, inplace=True)
        for each in range(len(rsi_cv_gb)):
            if cross_down.iloc[each] == -1:
                rsi_cv_gb.iloc[each] = -1

        # mfi = talib.MFI(hist_data['high'], hist_data['low'], hist_data['close'], hist_data['volume'], timeperiod=self.MFI_PERIOD)
        # mfi_ema = talib.EMA(mfi, timeperiod=self.MFI_AVG_PERIOD)
        # mfi_cv = self.utils.crossover(mfi, mfi_ema)

        # rocp = talib.ROCP(hist_data['close'], timeperiod=self.ROCP_PERIOD)
        # rocp_ema = talib.EMA(rocp, timeperiod=self.ROCP_AVG_PERIOD)
        # rocp_cv = self.utils.crossover(rocp, rocp_ema)

        # obv = talib.OBV(hist_data['close'],hist_data['volume'])
        # obv_ema = talib.EMA(obv, timeperiod=self.OBV_AVG_PERIOD)
        # obv_cv = self.utils.crossover(obv, obv_ema)

        # cci = talib.CCI(hist_data['high'], hist_data['low'], hist_data['close'], timeperiod=20)
        # cci_ema = talib.EMA(cci, timeperiod=9)
        # cci_cv = self.utils.crossover(obv, obv_ema)

        if rsi_cv_gb.iloc[-1] == 1:
            crossover_value = 1
        elif rsi_cv_gb.iloc[-1] == -1:
            crossover_value = -1
        else:
            crossover_value = 0
        return crossover_value

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
            qty = 100
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
            qty = 100
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
