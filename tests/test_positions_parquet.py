import os
import pandas as pd
import pytest
import importlib


def test_positions_parquet_load():
    root_dir = os.path.dirname(os.path.dirname(__file__))
    positions_path = os.path.join(root_dir, 'data', 'positions.parquet')

    # Verify the file exists
    assert os.path.exists(positions_path), f"File not found: {positions_path}"

    # Ensure a parquet engine is available
    has_pyarrow = importlib.util.find_spec("pyarrow") is not None
    has_fastparquet = importlib.util.find_spec("fastparquet") is not None
    if not (has_pyarrow or has_fastparquet):
        pytest.skip("Neither pyarrow nor fastparquet is installed; skipping parquet load test")
    # pytest.importorskip("pyarrow", reason="pyarrow is required for parquet support")

    # Load data
    positions = pd.read_parquet(positions_path)

    # Basic sanity checks
    assert isinstance(positions, pd.DataFrame), "Loaded object is not a DataFrame"
    assert positions.shape[0] > 0, "DataFrame has no rows"
    assert positions.shape[1] > 0, "DataFrame has no columns"

    # Expose structure for inspection in test output
    print(f"positions.parquet columns: {positions.columns.tolist()}")
    print(f"First 3 rows:\n {positions.head(3).to_dict(orient='records')}")


# In command line, test with: pytest tests/test_positions_parquet.py -s