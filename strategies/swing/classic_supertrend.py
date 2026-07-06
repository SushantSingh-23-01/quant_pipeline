import pandas as pd
import pandas_ta as ta
from backtesting import Strategy

def get_supertrend_signal(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        length: int,
        multiplier: float,
    ) -> pd.Series:
    st = ta.supertrend(
    high=high, low=low, close=close, 
    length=length, multiplier=multiplier
    )
    st_signal = f'SUPERTd_{length}_{multiplier}'
    return st[st_signal]

class ClassicSuperTrend(Strategy):
    """
    A simple trend-following strategy using the SuperTrend indicator.

    Trading Rules:
        - **Entry**: Go long when the SuperTrend direction flips to bullish (1), 
          signalling that the price closed above the upper band.
        - **Exit**: Close the long position when the SuperTrend direction flips 
          to bearish (-1), signalling that the price closed below the lower band.

    Attributes:
        length (int): The lookback period used for calculating the 
            Average True Range (ATR). Default is 14.
        multiplier (float): The value multiplied by the ATR to determine 
            the distance of the SuperTrend bands from the price. Default is 3.0.
    """
    length = 14
    multiplier = 3.0
    
    def init(self):
        low = pd.Series(self.data.Low)
        high = pd.Series(self.data.High)
        close = pd.Series(self.data.Close)
        
        self.supertrend = self.I(
            get_supertrend_signal, high, low, close, self.length, self.multiplier
            )
    
    def next(self):
        if not self.position:
            if self.supertrend[-1] == 1:
                self.buy()
        elif self.position:
            if self.supertrend[-1] == -1:
                self.position.close()
