import pandas as pd
import pandas_ta as ta
from backtesting import Strategy


class EmaChandelierTrend(Strategy):
    """
    EMA Cross with Chandelier Trailing Stop Strategy.
    
    Triggers long positions when a short-term EMA crossover aligns with a macro 
    bullish trend. Position risk is managed via a trailing volatility-based 
    stop-loss (ATR multiplier) tracked from the trade's highest price point.
    """
    # Strategy hyper-parameters (Optimizable)
    n1 = 10              # Fast EMA period
    n2 = 20              # Slow EMA period
    n3 = 200             # Macro structural SMA period
    atr_period = 14      # Average True Range period
    atr_mul = 4.0        # Chandelier Exit ATR multiplier

    def init(self):
        """Initialize technical indicators using pandas_ta and register them with the engine."""
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        close = pd.Series(self.data.Close)
        
        # Micro-trend indicators
        self.ema_s1 = self.I(ta.ema, close, self.n1)
        self.ema_s2 = self.I(ta.ema, close, self.n2)
        
        # Macro structural filter
        self.sma_l1 = self.I(ta.sma, close, self.n3)
        
        # Volatility metric for risk tracking
        self.atr = self.I(ta.atr, high, low, close, self.atr_period)
        
    def next(self):
        """Execute step-by-step logic on every incoming historical bar."""
        current_price = self.data.Close[-1]
        
        if not self.position:    
            # Condition 1: Short-term momentum is positive
            trend_up = self.ema_s1[-1] > self.ema_s2[-1]
            
            # Condition 2: Price resides above long-term macro baseline
            macro_up_trend = current_price > self.sma_l1[-1]
             
            if trend_up and macro_up_trend:
                # Calculate protective stop loss based on trailing volatility
                initial_sl = current_price - (self.atr_mul * self.atr[-1])
                self.buy(sl=initial_sl)
                
        else:
            # Chandelier Trailing Exit: Update stops dynamically
            for trade in self.trades:
                if trade.is_long:
                    # Calculate new exit floor using current bar high
                    new_trail_stop = self.data.High[-1] - (self.atr_mul * self.atr[-1])
                    
                    # Lock lock-in profits (Never move trailing stops down)
                    trade.sl = max(trade.sl, new_trail_stop)
