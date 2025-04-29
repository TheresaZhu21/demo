from dash import Dash, html
import dash_bootstrap_components as dbc
from .callbacks.event_pricing_callbacks import register_event_pricing_callbacks
from .callbacks.hedging_callbacks import register_hedging_callbacks
from .callbacks.navigation_callbacks import register_navigation_callbacks
from .config import PRIMARY, SECONDARY, BACKGROUND
from .utils.data_loader import load_positions
from .utils.log_config import setup_logging


setup_logging()

def generate_layout():
    header = html.Div([
        html.H1("Demo Research and Trade Dashboard", style={'color': PRIMARY, 'textAlign': 'center'}),
        html.Small("Author: Theresa Zhu | Date: Apr 17, 2025", style={'color': SECONDARY, 'fontSize': '18px', 'display': 'block', 'textAlign': 'center'})
    ], className='mt-4', style={'backgroundColor': BACKGROUND, 'borderBottom': f'2px solid {SECONDARY}', 'padding': '1rem 0', 'borderRadius': '0.5rem'})

    sidebar = html.Div([
        # Research Tools
        dbc.NavLink("Research Tools", href="#", id="tab-research", active="exact",
                    style={'color': SECONDARY, 'fontSize': '1.25rem', 'fontWeight': 'bold', 'marginBottom': '0.5rem'}),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavLink("Event Pricing", href="#", id="subtab-eventpricing", style={'color': PRIMARY, 'fontSize': '1.1rem', 'marginLeft': '1rem'}),
                dbc.NavLink("Stock Screener", href="#", id="subtab-screener", style={'color': PRIMARY, 'fontSize': '1.1rem', 'marginLeft': '1rem'}),
                dbc.NavLink("Backtester", href="#", id="subtab-backtester", style={'color': PRIMARY, 'fontSize': '1.1rem', 'marginLeft': '1rem'}),
            ], vertical=True, pills=True),
            id="collapse-research", is_open=False
        ),
        # Execution Tools
        dbc.NavLink("Execution Tools", href="#", id="tab-execution", active="exact",
                    style={'color': SECONDARY, 'fontSize': '1.25rem', 'fontWeight': 'bold', 'marginTop': '1rem'}),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavLink("Hedging", href="#", id="subtab-hedging", style={'color': PRIMARY, 'fontSize': '1.1rem', 'marginLeft': '1rem'})
            ], vertical=True, pills=True),
            id="collapse-execution", is_open=False
        ),
        # Risk & PnL Tools
        dbc.NavLink("Risk & PnL Tools", href="#", id="tab-riskpnl", active="exact",
                    style={'color': SECONDARY, 'fontSize': '1.25rem', 'fontWeight': 'bold', 'marginTop': '1rem'}),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavLink("PnL Analytics", href="#", id="subtab-pnlanalytics", style={'color': PRIMARY, 'fontSize': '1.1rem', 'marginLeft': '1rem'})
            ], vertical=True, pills=True),
            id="collapse-riskpnl", is_open=False
        ),
        # Market Data Tools
        dbc.NavLink("Market Data Tools", href="#", id="tab-marketdata", active="exact",
                    style={'color': SECONDARY, 'fontSize': '1.25rem', 'fontWeight': 'bold', 'marginTop': '1rem'}),
    ], style={'position': 'fixed', 'top': '151px', 'left': 0, 'bottom': 0, 'width': '18rem', 'padding': '2rem', 'backgroundColor': BACKGROUND})

    content = html.Div(id='page-content', style={'marginLeft': '20rem', 'padding': '2rem'})
    return html.Div([header, sidebar, content])

def create_app():
    external_stylesheets = [dbc.themes.FLATLY]  # theme
    app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
    server = app.server  # expose for deployment

    positions = load_positions()

    app.layout = generate_layout()
    register_event_pricing_callbacks(app)
    register_hedging_callbacks(app, positions)
    register_navigation_callbacks(app, positions)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
