import pandas as pd
import pandas_ta as ta
from backtesting import Strategy
from backtesting.lib import crossover

def get_macd_lines(
    close: pd.Series,
    fast: int,
    slow: int,
    signal: int,
    ) -> tuple[pd.Series, pd.Series]:
    macd = ta.macd(close, fast=fast, slow=slow, signal=signal)
    # Target columns explicitly by name format
    macd_m = f'MACD_{fast}_{slow}_{signal}'
    macd_s = f'MACDs_{fast}_{slow}_{signal}'
    return macd[macd_m], macd[macd_s]
      

class ClassicMACDCrossover(Strategy):
    """
    Implements a Moving Average Convergence Divergence (MACD) crossover strategy.

    Rules:
        - Entry: Buy when the MACD line crosses ABOVE the signal line.
        - Exit: Close position when the MACD line crosses BELOW the signal line.

    Attributes:
        fast_length (int): Period for the fast Exponential Moving Average (default: 12).
        slow_length (int): Period for the slow Exponential Moving Average (default: 26).
        signal (int): Period for the signal line Exponential Moving Average (default: 9).
    """
    fast_length = 12
    slow_length = 26
    signal = 9
    def init(self):
        close = pd.Series(self.data.Close)
        
        self.macd_m, self.macd_s = self.I(
            get_macd_lines, close, self.fast_length, self.slow_length, self.signal
            )
            
    def next(self):
        if not self.position:
            # Entry: MACD crosses ABOVE signal line
            if crossover(self.macd_m, self.macd_s):
                self.buy()
        else:
            # Exit: MACD crosses BELOW signal line
            if crossover(self.macd_s,self. macd_m):
                self.position.close()
