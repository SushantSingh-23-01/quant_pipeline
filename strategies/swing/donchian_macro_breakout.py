import pandas as pd
import pandas_ta as ta
from backtesting import Strategy


class DonchianMacroBreakout(Strategy):
    """
    Donchian Channel Breakout with Macro SMA Filter Strategy.
    
    Triggers buy orders when the price prints a new multi-week high, provided 
    the faster macro SMA stays above the slower macro SMA. Exits the entire 
    position dynamically if the intermediate trend breaks down completely.
    """
    # Strategy hyper-parameters (Optimizable)
    n1 = 50                 # Intermediate structural SMA period
    n2 = 200                # Long-term macro baseline SMA period
    breakout_period = 20    # Lookback window for Donchian Channel entry
    atr_period = 14         # Average True Range period for initial risk
    atr_mul = 3.0           # Volatility multiplier for protective stop

    def init(self):
        """Initialize technical indicators using pandas_ta and register them with the engine."""
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        close = pd.Series(self.data.Close)
        
        # Macro structural filters
        self.sma1 = self.I(ta.sma, close, self.n1)
        self.sma2 = self.I(ta.sma, close, self.n2)
        
        # Entry trigger: New multi-bar high channel breakout.
        # .shift(1) handles execution mapping to prevent look-ahead bias.
        self.entry_high = self.I(
            lambda src, w: pd.Series(src).rolling(window=w).max().shift(1), 
            high, 
            self.breakout_period
        )
        
        # Volatility metric for initial positioning risk
        self.atr = self.I(ta.atr, high, low, close, self.atr_period)
        
    def next(self):
        """Execute step-by-step logic on every incoming historical bar."""
        
        # STATE LOCK: If a trade is currently live, manage exit targets only.
        if self.position:
            # Macro Exit: Trigger global close when price breaks intermediate trend
            if self.data.Close[-1] < self.sma1[-1]:
                self.position.close()
            return  # Halt calculation cycle for the day
            
        # --- ENTRY LOGIC (Executes only when flat) ---
        macro_bullish = self.sma1[-1] > self.sma2[-1]
        breakout_occurring = self.data.Close[-1] > self.entry_high[-1]
        
        if macro_bullish and breakout_occurring:
            # Set a deep cushion stop-loss to weather market noise over multiple weeks
            initial_sl = self.data.Close[-1] - (self.atr_mul * self.atr[-1])
            self.buy(sl=initial_sl)
