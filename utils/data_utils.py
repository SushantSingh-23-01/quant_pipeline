import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import pandas as pd
import yfinance as yf

class MarketDataCache:
    """Manages downloading, incrementally updating, and caching market data."""
    
    def __init__(self, output_dir: str = 'stocks_data', format_to_save: str = 'parquet'):
        self.output_dir = output_dir
        self.format_to_save = format_to_save.lower().strip()
        
        self._validate_config()
        os.makedirs(self.output_dir, exist_ok=True)

    def _validate_config(self) -> None:
        """Ensure the chosen format is valid and dependencies are met."""
        if self.format_to_save not in ['parquet', 'csv']:
            raise ValueError("Unsupported format! Choose 'parquet' or 'csv'.")
        
        if self.format_to_save == 'parquet':
            try:
                import pyarrow 
            except ImportError:
                raise ImportError("Parquet formatting requires 'pyarrow'. Run: pip install pyarrow")

    def _get_target_path(self, ticker: str) -> str:
        return os.path.join(self.output_dir, f'{ticker}.{self.format_to_save}')

    def _load_existing_data(self, path: str) -> Optional[pd.DataFrame]:
        """Safely load cached file if it exists."""
        if not os.path.exists(path):
            return None
            
        if self.format_to_save == 'parquet':
            return pd.read_parquet(path)
        return pd.read_csv(path, index_col=0, parse_dates=True)

    def _clean_yf_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flatten multi-indices and structure columns uniformally."""
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        
        df.columns = [str(col).capitalize() for col in df.columns]
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        return df.reindex(columns=required_cols)

    def _determine_date_range(self, existing_df: Optional[pd.DataFrame], default_start: datetime, end: datetime) -> Tuple[datetime, bool]:
        """Calculate the next logical start date. Returns (start_date, should_skip)."""
        if existing_df is None or existing_df.empty:
            return default_start, False
            
        last_date = existing_df.index.max()
        actual_start = last_date + timedelta(days=1)
        
        # If our next required date is already matching or past the requested end window, skip
        return actual_start, (actual_start >= end)

    def update_ticker(self, ticker: str, default_start: datetime, end: datetime) -> None:
        """Handles the end-to-end pipeline for a single asset."""
        try:
            target_path = self._get_target_path(ticker)
            existing_df = self._load_existing_data(target_path)
            
            actual_start, should_skip = self._determine_date_range(existing_df, default_start, end)
            if should_skip:
                print(f"😎 {ticker} is already up to date. Skipping download.")
                return

            print(f"Requesting data for: {ticker} from {actual_start.strftime('%Y-%m-%d')}...")
            new_df = yf.download(tickers=ticker, start=actual_start, end=end, progress=False)
            
            if new_df is None or new_df.empty:
                print(f' ⚠️ No new market data returned for {ticker}.')
                return
            
            new_df = self._clean_yf_dataframe(new_df)
            
            # Merge logic
            if existing_df is not None and not existing_df.empty:
                combined_df = pd.concat([existing_df, new_df])
                # Prevent from writing duplicates if a script is run twice on the same day.
                combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
                combined_df.sort_index(inplace=True)
            else:
                combined_df = new_df
            
            # Save logic
            if self.format_to_save == 'parquet':
                combined_df.to_parquet(target_path)
            else:
                combined_df.to_csv(target_path)
                
            print(f"✅ Successfully updated cache: {target_path}")
            time.sleep(2)
                  
        except Exception as e:
            print(f"❌ Failed processing sequence for ticker {ticker}. Reason: {str(e)}", file=sys.stderr)

    def update_all(self, tickers: List[str], default_start: datetime, end: datetime) -> None:
        """Loop through a collection of assets."""
        for ticker in tickers:
            self.update_ticker(ticker, default_start, end)
