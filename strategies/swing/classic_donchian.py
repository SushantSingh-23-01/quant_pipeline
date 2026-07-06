import pandas as pd
import pandas_ta as ta
from backtesting import Strategy, Backtest
from typing import Tuple

def get_donchian_channels(
        high: pd.Series, 
        low: pd.Series, 
        lower_length: int, 
        upper_length: int,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """    
    Args:
        high: Series of historical high prices.
        low: Series of historical low prices.
        lower_length: Lookback period for calculating the lower channel band.
        upper_length: Lookback period for calculating the upper channel band.
    
    Returns:
        A tuple containing (lower_band, middle_band, upper_band) as Pandas
        Series.
    """
      
    dct = ta.donchian(high=high, low=low, lower_length=lower_length, upper_length=upper_length)
      
    # Safely select columns based on their string names to avoid indexing mix-ups
    dcl_col = [col for col in dct.columns if col.startswith('DCL')][0]
    dcm_col = [col for col in dct.columns if col.startswith('DCM')][0]
    dcu_col = [col for col in dct.columns if col.startswith('DCU')][0]
    return dct[dcl_col], dct[dcm_col], dct[dcu_col]

class ClassicDonchian(Strategy):
    """
        Rules:
        - Entry: Buy when the current close breaks above yesterday's upper band
          (DCU).
        - Exit: Close the long position when the current close drops below
          yesterday's lower band (DCL).

        Attributes:
            upper_length: Lookback period for entry (default 10 for aggressive
              entries).
            lower_length: Lookback period for exit (default 20 for passive exits).
    """
    upper_length = 10     # Aggressive Entry
    lower_length = 20     # Passive Exit
    def init(self):
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        self.dcl, self.dcm, self.dcu = self.I(get_donchian_channels, high, low, self.lower_length, self.upper_length)
    
    def next(self):
        close = self.data.Close[-1]
        
        # Note: Exclude todays highs and lows, since close always lies in between them.
        if not self.position and close > self.dcu[-2]:
            self.buy()
        elif self.position and close < self.dcl[-2]:
            self.position.close()
