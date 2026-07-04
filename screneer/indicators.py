from typing import Tuple
import pandas as pd
import pandas_ta as ta
from .config import Config

def calculate_technical_indicators(
    df: pd.DataFrame,
    config: Config
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:  
    """Calculates SMA, ATR, RSI, and Relative Volume indicators for a stock.

    Args:
        df: DataFrame containing standard OHLCV data columns.
        config: Configuration instance defining indicator lengths.

    Returns:
        A tuple containing five pandas Series in order:
        (micro_sma, macro_sma, atr, rsi, relative_volume).
    """
    low = df['Low']
    high = df['High']
    close = df['Close']
    volume = df['Volume']
    
    micro_sma = ta.sma(close=close, length=config.micro_sma_length)
    macro_sma = ta.sma(close=close, length=config.macro_sma_length)
    
    atr = ta.atr(high=high, low=low, close=close, length=config.atr_length)
    rsi = ta.rsi(close=close, length=config.rsi_length)
    rovl = volume / ta.sma(close=volume, length=config.vol_sma_length)
    return micro_sma, macro_sma, atr, rsi, rovl
