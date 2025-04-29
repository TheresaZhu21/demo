import pandas as pd
import os
import warnings
import logging

logger = logging.getLogger(__name__)

def load_positions() -> pd.DataFrame:
    """
    Load and validate the positions data from a Parquet file.

    Performs sanity checks:
    - File exists
    - Required columns
    - WArns if missing value are present
    - Ensures the DataFrame is not empty

    Returns:
        pd.DataFrame: Validate positions data.
    
    Raises:
        FileNotFoundError: If the file is missing.
        ValueError: If required columns are missing or data is empty.
        RuntimeWarning: If there are missing values.
    """
    logger.info("Loadding positions...")
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'positions.parquet')

    if not os.path.exists(path):
        raise FileNotFoundError(f"Positions file not found: {path}") # TODO: include errors in the logs
    
    df = pd.read_parquet(path)

    # Sanity checks
    required_columns = ['Symbol', 'Delta$', 'Book', 'Market']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}") # TODO: include errors in the logs
        
    if df.isnull().any().any():
        warnings.warn("Positions file contains missing values.", RuntimeWarning) # here soft warnings are more proper
        logger.warning("Missing values detected.") 
    
    # if not df['UnitDelta'].between(-1, 1).all():
    #     raise ValueError("Unit delta should be between -1 and 1.")

    if df.empty():
        raise ValueError("Loaded positions file is empty.") # TODO: include errors in the logs

    return df