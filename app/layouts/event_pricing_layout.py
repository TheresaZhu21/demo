from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from config import PRIMARY, SECONDARY, BACKGROUND


def event_pricing_layout():
    return html.Div([
        html.H4("Event Pricing", style={'textAlign': 'left', 'marginTop': '0', 'marginBottom': '1rem', 'color': PRIMARY}),
        dbc.Row([
            # Left pnanel: Market Inputs
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Market Inputs", style={'borderBottom': f'2px solid {SECONDARY}'}),
                    dbc.CardBody([
                        # Input fields
                        dbc.Row([dbc.Label("Initial Underlying Price:"), dcc.Input(id='input-s0', type='number', value=100.0, step=0.1, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Annual Volatility (%):"), dcc.Input(id='input-ann-vol', type='number', value=30.0, step=0.01, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Interest Rate (%):"), dcc.Input(id='input-r', type='number', value=0.0, step=0.01, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Dividend Yield (%):"), dcc.Input(id='input-q', type='number', value=0.0, step=0.01, className='form-control')], className='mb-3'),
                        html.Hr(),
                        dbc.Row([dbc.Label("Normal Trading Days:"), dcc.Input(id='input-normal-days', type='number', value=7, step=1, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Non-Trading Days:"), dcc.Input(id='input-non-tdays', type='number', value=2, step=1, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Event Days:"), dcc.Input(id='input-event-days', type='number', value=1, step=1, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Event Variance Multiplier:"), dcc.Input(id='input-event-multiplier', type='number', value=2.0, step=0.1, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Upside Probability (%):"), dcc.Input(id='input-prob-up', type='number', value=90.0, min=0, max=100, step=0.01, className='form-control')], className='mb-3'),
                        dbc.Row([dbc.Label("Target Delta (%):"), dcc.Input(id='input-target-delta', type='number', value=25.0, min=0, max=100, step=1, className='form-control')], className='mb-3'),
                        dbc.Button("Compute", id='compute-btn', color='primary', className='mt-3 w-100')
                    ])
                ], style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'overflowY': 'auto'}), width=2
            ),
            # Right panel: Effectiv Annualized Volatility, Pricing Summary, and charts
            dbc.Col([
                dbc.Row(
                    [
                        # Effective Annualized Volatility
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader("Effective Annualized Volatility", style={'borderBottom': f'2px solid {SECONDARY}'}),
                                dbc.CardBody(
                                    html.H2(id='output-vol', style={'color': PRIMARY}),
                                    style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '100%',},
                                ),
                            ], style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'height': '100%'}),
                            width=3
                        ),
                        # Pricing Summary table
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader("Pricing Summary", style={'borderBottom': f'2px solid {SECONDARY}'}),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id='output-table', columns=[], data=[],
                                        style_table={'overflowX': 'auto'},
                                        style_header={'backgroundColor': PRIMARY, 'color': 'white', 'fontWeight': 'bold', 'fontSize': '0.85rem'},
                                        style_cell={'textAlign': 'center', 'padding': '0.5rem', 'fontSize': '0.75rem'},
                                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': BACKGROUND}]
                                    )
                                )
                            ], 
                            className='h-100',
                            style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'height': '100%'}),
                            width=9
                        )
                    ], 
                    className='mb-4',
                    style={'display': 'flex', 'alignItems': 'stretch'},
                ),
                # Row 1 of charts
                dbc.Row([
                    dbc.Col(dcc.Graph(id='output-iv-chart', style={'width':'90%','aspectRatio':'3/2'}), width=6),
                    dbc.Col(dcc.Graph(id='output-chart', style={'width':'90%','aspectRatio':'3/2'}), width=6)
                ], className='mb-4'),
                # Row 2 of charts
                dbc.Row([
                    dbc.Col(dcc.Graph(id='price-comp-chart', figure={}, style={'width':'90%','aspectRatio':'3/2'}), width=6),
                    dbc.Col(dcc.Graph(id='straddle-payoff-chart', figure={}, style={'width':'90%','aspectRatio':'3/2'}), width=6)
                ], className='mb-4')
            ], width=10)
        ])
    ])
