# Demo Research and Trade Dashboard

**Author:** Theresa Zhu  
**Date:** April 17, 2025

An extensible, modular Plotly Dash application for:

- **Event Pricing**: compute pre‑ and post‑announcement option prices, implied volatility shifts, and payoff diagrams
- **Hedging Orders**: generate and export delta‑hedging trade orders
- **PnL Analytics**: placeholder for future risk and analytics tools

---

## 🚀 Quickstart

1. **Clone the repository**  
   ```bash
   git clone git@github.com:TheresaZhu21/demo.git
   cd demo
   ```

2. **Create a virtual environment & install dependencies**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .\.venv\Scripts\activate   # Windows

   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Generate sample data**  
   Serialize the fake hedging positions into a Parquet file:
   ```bash
   python data/generate_positions.py
   ```

4. **Run the app**  
   ```bash
   python -m app.run
   ```
   Open your browser at `http://localhost:8050`.

---

## 📁 Project Structure

```
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── positions.parquet       # Generated sample hedging data
│   └── generate_positions.py   # Script to create the Parquet file
├── app/
│   ├── __init__.py
│   ├── config.py               # Shared color & style constants
│   ├── run.py                  # App entrypoint & callback registration
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_loader.py      # load_positions()
│   ├── layouts/
│   │   ├── __init__.py
│   │   ├── event_pricing_layout.py
│   │   ├── hedging_layout.py
│   │   └── pnl_analytics_layout.py
│   ├── callbacks/
│   │   ├── __init__.py
│   │   ├── event_pricing_callbacks.py
│   │   ├── hedging_callbacks.py
│   │   └── navigation_callbacks.py
│   └── event_pricing/
│       ├── __init__.py
│       ├── black_scholes.py
│       └── event_pricing.py
└── tests/
    └── test_event_pricing.py    # Unit tests
```

---

## 🛠️ Development

- **Layouts**: add or modify UI in `app/layouts/*.py`
- **Callbacks**: register Dash callbacks in `app/callbacks/*.py`
- **Core Logic**: extend pricing or analytics classes under `app/event_pricing/`
- **Config**: adjust shared constants in `app/config.py`
- **Data**: manage input datasets in `data/`, load via `app/utils/data_loader.py`

To run tests:
```bash
pytest
```

---

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

