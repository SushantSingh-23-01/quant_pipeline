import pandas as pd
import pandas_ta as ta
from backtesting import Strategy
from backtesting.lib import crossover
from typing import Tuple

def get_bollinger_bands(
    close: pd.Series,
    length: int,
    std: float
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
    bbands = ta.bbands(close, length=length, std=std)
    # Safely select columns based on their string names to avoid indexing mix-ups
    bbl = [col for col in bbands.columns if col.startswith('BBL')][0]
    bbm = [col for col in bbands.columns if col.startswith('BBM')][0]
    bbu = [col for col in bbands.columns if col.startswith('BBU')][0]
    return bbands[bbl], bbands[bbm], bbands[bbu]

class ClassicBBands(Strategy):
    """
        Implements simple Bollinger Bands mean reversion strategy.
        Rules:
            - Entry: Price closes below Lower Bollinger Band. (reversal UP expected)
            - Exit: Prices touches or crosses the middle Moving Average line.
        Attributes
            bb_length: Lookback period for Bollinger Bands.
            bb_std: Standard deviation for Bollinger Bands.
    """
    bb_length = 20
    bb_std = 2.0
    def init(self):
        close = pd.Series(self.data.Close)
        
        self.bbl, self.bbm, self.bbu = self.I(get_bollinger_bands, close, length=self.bb_length, std=self.bb_std)
        print(self.bbl[-1])
    
    def next(self):
        if not self.position:
            if self.data.Close[-1] < self.bbl[-1]:
                self.buy()
        else:
            if crossover(self.data.Close, self.bbm):
                self.position.close()
