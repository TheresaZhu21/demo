import pandas as pd
import numpy as np
import os


def get_pnl_path():
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'pnl.parquet')

def generate_pnl(n: int = 10000):
    """
    Generate a random PnL DataFrame spanning the past 1000 days.
    """
    # Date range: past 1000 days up to today
    end_date = pd.Timestamp.today().normalize()
    start_date = end_date - pd.Timedelta(days=999)
    dates = pd.date_range(start_date, end_date, freq='D')

    # Fixed metadata
    books = ['Book1', 'Book2', 'Book3']

    # Combinations
    combos = [
        ('Class1', 'STRATEGY1_EU', 'USDCHF Curncy'),
        ('Class1', 'STRATEGY1_EU', 'EURUSD Curncy'),
        ('Class1', 'STRATEGY1_HK', 'GBPUSD Curncy'),
        ('Class1', 'STRATEGY1_HK', 'USDHKD Curncy'),
        ('Class1', 'STRATEGY1_HK', 'USDHKD Curncy'),
        ('Class1', 'STRATEGY1_HK', 'USDHKD Curncy'),
        ('Class1', 'STRATEGY1_HK','USDHKD Curncy'),
        ('Class1', 'STRATEGY1_HK', 'USDHKD Curncy'),
        ('Class1', 'STRATEGY1_HK', 'USDHKD Curncy'),
        ('Class1', 'STRATEGY1_IN', 'USDINR Curncy'),
        ('Class1', 'STRATEGY1_JP', 'USDJPY Curncy'),
        ('Class1', 'STRATEGY1_JP', 'USDJPY Curncy'),
        ('Class1', 'STRATEGY1_JP', 'JT Equity'),
        ('Class1', 'STRATEGY1_JP', 'TPX Index'),
        ('Class1', 'STRATEGY1_US', 'EURUSD Curncy'),
        ('Class2', 'STRATEGY2', 'AUDUSD Curncy'),
        ('Class2', 'STRATEGY2', 'GBPUSD Curncy'),
        ('Class2', 'STRATEGY2', 'KOSPI2 Index'),
        ('Class2', 'STRATEGY2', 'NKY Index'),
        ('Class2', 'STRATEGY2', 'TPX Index'),
        ('Class2', 'STRATEGY2', 'USDCHF Curncy'),
        ('Class2', 'STRATEGY2', 'USDJPY Curncy'),
        ('Class3', 'STRATEGY3', 'AUDUSD Curncy'),
        ('Class3', 'STRATEGY3', 'EURUSD Curncy'),
        ('Class3', 'STRATEGY3', 'GBPUSD Curncy'),
        ('Class3', 'STRATEGY3', 'USDCHF Curncy'),
        ('Class4', 'STRATEGY4', 'USDJPY Curncy'),
        ('Class4', 'STRATEGY4', 'EURUSD Curncy'),
        ('Class5', 'STRATEGY5', 'USDHKD Curncy'),
    ]

    # Randomly sample indices
    combo_idxs = np.random.choice(len(combos), size=n, replace=True)
    date_idxs = np.random.choice(len(dates), size=n, replace=True)

    rows = []
    for combo_i, date_i in zip(combo_idxs, date_idxs):
        cls, strat, und = combos[combo_i]
        date = dates[date_i]
        book = np.random.choice(books)

        daily = np.random.normal(loc=0, scale=200000)
        carry = np.random.normal(loc=0, scale=50000)
        delta = np.random.normal(loc=0, scale=100000)
        trade = np.random.normal(loc=0, scale=30000)
        vega = np.random.normal(loc=0, scale=80000)
        vanna = np.random.normal(loc=0, scale=80000)
        volga = np.random.normal(loc=0, scale=80000)
        unexpl = daily - (carry + delta + trade + vega + vanna + volga)

        rows.append({
            'valuationDateTime': date,
            'book': book,
            'class': cls,
            'strategy': strat,
        })