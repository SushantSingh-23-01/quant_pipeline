from dataclasses import dataclass

@dataclass
class Config:
    """Configuration parameters for technical analysis indicators."""
    micro_sma_length: int = 20
    macro_sma_length: int = 200
    atr_length: int = 14
    rsi_length: int = 14
    vol_sma_length: int = 20
