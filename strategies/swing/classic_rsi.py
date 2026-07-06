import pandas as pd
import pandas_ta as ta
from backtesting import Backtest

class ClassicRSI(Strategy):
    """
        Implements simple RSI momentum strategy.
        Rules:
            - Entry: RSI drops below 30 (oversold) and then crosses above 30.
            - Exit: RSI rises above 70 (overbought) and then crosses back below 70.
    """
    length = 14
    def init(self):
        close = pd.Series(self.data.Close)
        
        self.rsi = self.I(ta.rsi, close, self.length)
    
    def next(self):
        if not self.position:
            # RSI crossover ABOVE 30
            if self.rsi[-2] < 30 and self.rsi[-1] > 30:
                self.buy()
        elif self.position:
            # RSI crossover BELOW 70
            if self.rsi[-2] > 70 and self.rsi[-1] < 70:
                self.position.close()
