from pathlib import Path
import pandas as pd

from .config import Config
from .indicators import calculate_technical_indicators
from .loaders import read_parquet_tail

def batch_analyze_stocks(
    data_dir: str,
    config: Config,
) -> pd.DataFrame:
    """Scans a directory of Parquet files to compute the latest technical indicators.

    Args:
        data_dir: Directory path containing the stock Parquet files.
        config: Configuration instance defining indicator metrics.

    Returns:
        A summary DataFrame containing one row per stock ticker with its
        latest date, close price, and calculated technical indicators.
    """
    data_dir = Path(data_dir)
    if not data_dir.exists():
        print(f'Error: Directory {data_dir} does not exist.')
        return pd.DataFrame()
      
    # Note: Macro Indicators need buffer period for calculations
    required_rows = int(config.macro_sma_length * 1.5)
    data = {
        'Ticker': [], 'Last_Date': [], 'Last_Close': [],
        f'SMA_{config.micro_sma_length}': [], f'SMA_{config.macro_sma_length}': [],
        f'ATR_{config.atr_length}': [], f'RSI_{config.rsi_length}': [],
        f'ROVL_{config.vol_sma_length}': []
    }
    
    for file_path in data_dir.rglob('*.parquet'):       
        try:
            df = read_parquet_tail(str(file_path), required_rows)
            if len(df) < config.macro_sma_length or df.empty:
                continue
           
            ( 
                micro_sma, macro_sma,
                atr, rsi, rovl
            ) = calculate_technical_indicators(df, config)
                
            last_date = df.index[-1]
            last_date = last_date.strftime('%Y-%m-%d') if hasattr(last_date, 'strftime') else str(last_date)
            
            data['Ticker'].append(file_path.stem)
            data['Last_Date'].append(last_date)
            data['Last_Close'].append(df['Close'].iloc[-1])
            data[f'SMA_{config.micro_sma_length}'].append(micro_sma.iloc[-1])
            data[f'SMA_{config.macro_sma_length}'].append(macro_sma.iloc[-1])
            data[f'ATR_{config.atr_length}'].append(atr.iloc[-1])
            data[f'RSI_{config.rsi_length}'].append(rsi.iloc[-1])
            data[f'ROVL_{config.vol_sma_length}'].append(rovl.iloc[-1])
        except Exception as e:
            print(f'Skipping {file_path.name} due to error: {e}')
            
    return pd.DataFrame(data)
