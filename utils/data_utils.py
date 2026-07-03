import os
import sys
import time
from datetime import datetime
from typing import List
import pandas as pd
import yfinance as yf

def fetch_data(
    tickers: List[str],
    start: datetime,
    end: datetime,
    format_to_save: str = 'parquet'
) -> None:
    """
    Download historical market data from yfinance and save to a local cache directory.

    Handles single and multi-ticker multi-index outputs automatically, safely manages 
    local directory paths, handles dependency checks, and protects execution loops from 
    network API dropouts.

    Args:
        tickers (List[str]): List of asset symbols to pull (e.g., ['RELIANCE.NS', 'AAPL']).
        start (datetime): Ingestion start timestamp window.
        end (datetime): Ingestion boundary end timestamp window.
        format_to_save (str, optional): Data serialization format ('parquet' or 'csv'). 
                                        Defaults to 'parquet'.
    """
    # --- Initialization Checks ---
    format_to_save = format_to_save.lower().strip()
    if format_to_save not in ['parquet', 'csv']:
        raise ValueError("Unsupported format! Format must be 'parquet' or 'csv'.")
    
    if format_to_save == 'parquet':
        try:
            import pyarrow
        except ImportError:
            raise ImportError(
                "Parquet formatting requires 'pyarrow'."
                "Run: pip install pyarrow"
            )
     
    output_dir = 'stocks_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # --- Download Stock Data ---
    for ticker in tickers:
        try:
            target_path = os.path.join(output_dir, f'{ticker}.{format_to_save}')
            existing_df = None
            actual_start = start
            
            
            print(f'Requesting data for: {ticker}...')
            df = yf.download(tickers=ticker, start=start, end=end, progress=False)
            if df is None or df.empty:
                print(f' Warning: No market data returned for {ticker}. Skipping.')
                continue
            
            # FLATTEN Multi index columns if present in downloaded data
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            
            # Normalize Column Names and sort to work with other libraries
            df.columns = [col.capitalize() for col in df.columns]
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.reindex(columns=required_cols)
            
            # Save the file 
            
            if format_to_save == 'parquet':
                df.to_parquet(target_path)
            else:
                df.to_csv(target_path)
            print(f"✅ Successfully cached: {target_path}")
            
            # Aviod IP ban
            time.sleep(3)            
        except Exception as e:
            # Shield loop iteration so a single broken symbol doesn't crash the entire download job
            print(f"❌ Failed processing sequence for ticker {ticker}. Reason: {str(e)}", file=sys.stderr)
            continue
