import pandas as pd
import pandas_ta as ta
from backtesting import Strategy
from backtesting.lib import crossover

class ClassicEMACrossover(Strategy):
    """
        Implements Simple EMA Crossover Strategy
        Rules:
            - Entry(Golden Cross): Fast EMA crosses above the slow EMA.
            - Exit (Death Cross): Fast EMA crosses below the slow EMA.
    """
    fast_length = 9
    slow_length = 21    
    
    def init(self):
        close = pd.Series(self.data.Close)
        
        self.fast_ema = self.I(ta.ema, close, self.fast_length)
        self.slow_ema = self.I(ta.ema, close, self.slow_length)
    
    def next(self):
        # Check if the fast EMA just crossed ABOVE the slow EMA
        if crossover(self.fast_ema, self.slow_ema):
            if not self.position:
                self.buy()
                
        # Check if the fast EMA just crossed BELOW the slow EMA
        elif crossover(self.slow_ema, self.fast_ema):
            if self.position:
                self.position.close()
