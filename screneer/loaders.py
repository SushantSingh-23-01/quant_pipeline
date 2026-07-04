import pandas as pd
import pyarrow.parquet as pq

def read_parquet_tail(
    file_path: str,
    required_rows: int
) -> pd.DataFrame: 
    """Reads metadata of a Parquet file and extracts only the tail rows.
    
    Args:
        file_path: Path to the target Parquet file.
        required_rows: Number of trailing rows needed from the file.
    
    Returns:
        A pandas DataFrame containing the requested trailing rows.
    """
    # Read metada without reading files and get number of rows
    parquet_file = pq.ParquetFile(file_path)
    total_rows = parquet_file.metadata.num_rows
    skip_rows = max(0, total_rows - required_rows)
    
    # Note: This assumes the Parquet file contains a single row group. 
    # Slice and obtain the tail of file.
    df = parquet_file.read_row_group(0).to_pandas()
    df = df.iloc[skip_rows:] if total_rows > required_rows else df
    return df
