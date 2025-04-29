# Demo Research and Trade Dashboard

**Author:** Theresa Zhu  
**Date:** April 17, 2025

An extensible, modular demo Plotly Dash application for reserch and trading, featuring:

- **Event Pricing**: compute pre‑ and post‑announcement option prices, implied volatility shifts, skew, PDF, etc.
- **Hedging Orders**: generate and export delta‑hedging trade orders.
- **PnL Analytics**: monitor and evaluate historical PnL trends and correlations.

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

4. **Run the app (local)**  
   ```bash
   python -m app.run
   ```
   Open your browser at `http://localhost:8050`.

5. **Run the app (online)**  
   Open your browser at `https://demo-vehj.onrender.com/`.

6. **Run Tests**  
   To run unit tests:
   ```bash
   pytest tests/
   ```
   Make sure you have `pytest` installed (`pip install pytest`).

---

## 📁 Project Structure

```
├── .gitignore
├── README.md
├── requirements.txt
├── data/                              # Data files and generators
│   ├── positions.parquet              # Sample hedging dataset
│   ├── generate_pnl.py                # Script to simulate random PnL data
│   └── generate_positions.py          # Script to simulate random positions
├── app/                               # Main application package
│   ├── __init__.py
│   ├── config.py                      # Centralized configuration (colors, settings)
│   ├── run.py                         # App entrypoint (initialize Dash app & register callbacks)
│   ├── utils/                         # Utility functions
│   │   ├── __init__.py
│   │   └── data_loader.py             # load_positions(), load_pnl_data(), etc.
│   ├── layouts/                       # Dash layouts
│   │   ├── __init__.py
│   │   ├── event_pricing_layout.py
│   │   ├── hedging_layout.py
│   │   └── pnl_analytics_layout.py
│   ├── callbacks/                     # Dash callbacks (business logic connecting UI & core)
│   │   ├── __init__.py
│   │   ├── event_pricing_callbacks.py
│   │   ├── hedging_callbacks.py
│   │   └── navigation_callbacks.py
│   └── event_pricing/                 # Core app logic and services: event pricing
│       ├── __init__.py
│       ├── black_scholes.py           # Black-Scholes formulas
│       └── event_pricing.py           # Event pricing engine
└── tests/                             # Unit and integration tests
    ├── test_event_pricing.py          # Unit tests for event pricing core logic
    └── test_positions_parquet.py      # Unit tests for position generator
```

---

## 🛠️ Development

- **Layouts**: add or modify UI in `app/layouts/*.py`
- **Callbacks**: register Dash callbacks in `app/callbacks/*.py`
- **Core Logic**: extend pricing or analytics classes under `app/event_pricing/`
- **Config**: adjust shared constants in `app/config.py`
- **Data**: manage input datasets in `data/`, load via `app/utils/data_loader.py`

---

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

