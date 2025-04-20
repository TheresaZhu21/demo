import pandas as pd
import os

def load_positions() -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'positions.parquet')
    return pd.read_parquet(path)