import pandas as pd
import numpy as np
import os


def get_positions_path():
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'positions.parquet')

def generate_positions(n: int = 30):
    """
    Overwrites positions.parquet with defined number of sampled records,
    """
    path = get_positions_path()

    # Load existing positions to infer schema (must have at least one record)
    df = pd.read_parquet(path)

    replace = len(df) < n
    sampled = df.sample(n=n, replace=replace).reset_index(drop=True)

    # Assign unique symbols
    sampled['Symbol'] = [f"Symbol{i+1}" for i in range(n)]

    # Assign random Book and Market to each row
    books = ['Book1', 'Book2', 'Book3']
    markets = ['US', 'EU', 'HK', 'JP', 'AU', 'IN']
    sampled['Book'] = np.random.choice(books, size=n)
    sampled['Market'] = np.random.choice(markets, size=n)

    # Reorder the columns by putting Symbol, Book, and Market first
    cols = sampled.columns.tolist()
    for col in ['Symbol', 'Book', 'Market']:
        cols.insert(0, cols.pop(cols.index(col)))
    sampled = sampled[cols]

    # Write back to parquet (overwrites existing file)
    sampled.to_parquet(path, index=False)
    print(f"Wrote {n} records to: {path}")


if __name__ == '__main__':
    generate_positions()




# path = os.path.join(os.path.dirname(__file__), 'positions.parquet')

# df = pd.DataFrame({
#     'Symbol':           ['Symbol1', 'Symbol2', 'Symbol3'],
#     'Spot':              [100.23, 150.45, 200.67],
#     'Spot % Move':       ['+1.2%', '-0.5%', '+0.8%'],
#     'Delta':             [10000, -5000, 7500],
#     'Skew Delta':        [850, -220, 600],
#     'Gamma':             [45, 30, 75],
#     'Restriction':       ['None', 'MaxSell', 'None'],
#     'Max Long':          [120, 80, 100],
#     'Managed Delta':     [10000, -5000, 7500],
#     'Max Sell':          [5000, 3000, 4000],
#     'Max Buy':           [6000, 3500, 4500],
#     'Target Delta':      [11000, -5500, 8200],
#     'Target Exec Delta': [10500, -5300, 7900],
#     'Target Exec Shrs':  [105, -53, 79],
#     'Inventory':         [200, -20, 100],
#     'Restriction Pct':   ['100%', '90%', '95%'],
#     'Limit Reached':     [False, True, False]
# })

# df.to_parquet(path, index=False)
# print(f"Wrote {n} records to: {path}")
