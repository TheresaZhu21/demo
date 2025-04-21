import pandas as pd
import numpy as np
import os


def get_positions_path():
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'positions.parquet')

def generate_positions(n: int = 30):
    """
    Overwrites positions.parquet with defined number of sampled records,
    recalculates greeks & targets to be delta-neutral.
    """
    path = get_positions_path()

    # Load & sample
    df = pd.read_parquet(path)
    replace = len(df) < n
    sampled = df.sample(n=n, replace=replace).reset_index(drop=True)

    # Assign unique symbols & random Book/Market
    sampled['Symbol'] = [f"Symbol{i+1}" for i in range(n)]
    books = ['Book1', 'Book2', 'Book3']
    markets = ['US', 'EU', 'HK', 'JP', 'AU', 'IN']
    sampled['Book'] = np.random.choice(books, size=n)
    sampled['Market'] = np.random.choice(markets, size=n)

    # Generate randome Spot and Gamma$ with thresholds
    sampled['Spot'] = np.random.uniform(1, 200, size=n).round(2)
    min_delta = 500_000
    sampled['Delta$'] = np.random.randint(min_delta, size=n)

    # Parse Spot % Move as decimal
    sampled['Spot Pct Move'] = (sampled['Spot % Move'].str.rstrip('%').astype(float) / 100)

    # Recompute Delta$
    sampled['Gamma$'] = ((sampled['Delta$'] * sampled['Spot Pct Move']).round().astype(int))
    sampled['Managed Delta$'] = sampled['Delta$']
    
    # Always target flat
    sampled['Target Delta$'] = 0.0
    sampled['Target Exec Delta$'] = - sampled['Managed Delta$']
    sampled['Target Exec Shrs'] = (np.round(sampled['Target Exec Delta$'] / sampled['Spot']).astype(int))

    # Reorder the columns
    cols = ['Market', 'Book', 'Symbol', 'Spot', 'Spot % Move', 
            'Delta$', 'Skew Delta$', 'Gamma$', 'Restriction', 'Max Long', 
            'Managed Delta$', 'Max Sell', 'Max Buy', 'Target Delta$', 'Target Exec Delta$', 
            'Target Exec Shrs', 'Inventory', 'Restriction Pct', 'Limit Reached']
    sampled = sampled[cols]

    # Write back to parquet
    print(sampled)
    sampled.to_parquet(path, index=False)
    print(f"Wrote {n} records to: {path}")


if __name__ == '__main__':
    generate_positions()
