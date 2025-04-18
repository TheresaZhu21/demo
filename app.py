"""
app.py for Event Pricing Dashboard
Author: Theresa Zhu
Date: Apr 17, 2025
"""
import dash
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from event_pricing import EventPricing

external_stylesheets = [dbc.themes.FLATLY] # theme
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Color palette
PRIMARY = "#2C3E50"      # Deep blue-grey
SECONDARY = "#18BC9C"    # Teal accent
BACKGROUND = "#F5F7FA"   # Light grey

# App Layout
app.layout = dbc.Container(
    fluid=True,
    style={'backgroundColor': BACKGROUND, 'padding': '2rem'},
    children=[
        # Header
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H1("Event Pricing Dashboard", style={'color': PRIMARY}),
                    html.Small("Author: Theresa Zhu | Date: Apr 17, 2025",
                               style={'color': SECONDARY, 'fontSize': '20px', 'display': 'block', 'marginTop': '0.5rem'})
                ], style={'textAlign': 'center'})
            )
        , className='mb-5'),

        # Main content
        dbc.Row([
            # Left panel: inputs
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Market Inputs", style={'borderBottom': f'2px solid {SECONDARY}'}),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Label("Initial Underlying Price:"),
                            dcc.Input(id='input-s0', type='number', value=100.0, step=0.1, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Annual Volatility:"),
                            dcc.Input(id='input-ann-vol', type='number', value=0.30, step=0.01, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Interest Rate:"),
                            dcc.Input(id='input-r', type='number', value=0.0, step=0.001, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Dividend Yield:"),
                            dcc.Input(id='input-q', type='number', value=0.0, step=0.001, className='form-control')
                        ], className='mb-3'),
                        html.Hr(),
                        dbc.Row([
                            dbc.Label("Normal Trading Days:"),
                            dcc.Input(id='input-normal-days', type='number', value=7, step=1, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Non-Trading Days:"),
                            dcc.Input(id='input-non-tdays', type='number', value=2, step=1, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Event Days:"),
                            dcc.Input(id='input-event-days', type='number', value=1, step=1, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Event Variance Multiplier:"),
                            dcc.Input(id='input-event-multiplier', type='number', value=2.0, step=0.1, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Probability Up:"),
                            dcc.Input(id='input-prob-up', type='number', value=0.9, min=0, max=1, step=0.01, className='form-control')
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Label("Target Delta:"),
                            dcc.Input(id='input-target-delta', type='number', value=0.25, min=0, max=1, step=0.01, className='form-control')
                        ], className='mb-3'),
                        dbc.Button("Compute", id='compute-btn', color='primary', className='mt-3 w-100')
                    ])
                ], style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'height': '80vh', 'overflowY': 'auto'}),
                width=2
            ),

            # Right panel: outputs
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Effective Annualized Volatility", style={'borderBottom': f'2px solid {SECONDARY}'}),
                    dbc.CardBody(html.H2(id='output-vol', style={'color': PRIMARY}))
                ], className='mb-4', style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),

                dbc.Card([
                    dbc.CardHeader("Pricing Summary", style={'borderBottom': f'2px solid {SECONDARY}'}),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='output-table',
                            columns=[],
                            data=[],
                            style_table={'overflowX': 'auto'},
                            style_header={'backgroundColor': SECONDARY, 'color': 'white', 'fontWeight': 'bold'},
                            style_cell={'textAlign': 'center', 'padding': '0.5rem'},
                            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': BACKGROUND}],
                        ),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col(dcc.Graph(id='output-iv-chart'), width=6),
                            dbc.Col(dcc.Graph(id='output-chart'), width=6)
                        ], className='mt-4'),
                        dbc.Row([
                            dbc.Col(dcc.Graph(id='price-comp-chart', figure={}), width=6),
                            dbc.Col(dcc.Graph(id='straddle-payoff-chart', figure={}), width=6)
                        ], className='mt-4')
                    ])
                ], style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'height': '72.25vh', 'overflowY': 'auto'})
            ], width=10)
        ])
    ]
)

@app.callback(
    [
        Output('output-vol', 'children'),
        Output('output-table', 'data'),
        Output('output-table', 'columns'),
        Output('output-iv-chart', 'figure'),
        Output('output-chart', 'figure'),
        Output('price-comp-chart', 'figure'),
        Output('straddle-payoff-chart', 'figure')
    ],
    [
        Input('compute-btn', 'n_clicks'),
        Input('input-s0', 'value'),
        Input('input-ann-vol', 'value'),
        Input('input-r', 'value'),
        Input('input-q', 'value'),
        Input('input-normal-days', 'value'),
        Input('input-non-tdays', 'value'),
        Input('input-event-days', 'value'),
        Input('input-event-multiplier', 'value'),
        Input('input-prob-up', 'value'),
        Input('input-target-delta', 'value')
    ]
)
def update_dashboard(n_clicks, s0, ann_vol, r, q,
                     normal_days, non_tdays, event_days,
                     event_multiplier, prob_up, target_delta):
    if not n_clicks:
        return [dash.no_update]*7

    # Compute
    ep = EventPricing(
        S0=float(s0), ann_vol=float(ann_vol), r=float(r), q=float(q),
        normal_days=int(normal_days), non_tdays=int(non_tdays),
        event_days=int(event_days), event_multiplier=float(event_multiplier),
        prob_up=float(prob_up), target_delta=float(target_delta)
    )

    # Vol output
    vol_text = f"{ep.eff_vol:.2%}"

    # Summary table
    df_sum = ep.summary()
    df_sum.columns = ["Scenario", "Forward Price", "Straddle Price",
                      "Put Strike", "Put Price", "Call Strike", "Call Price"]
    df_sum = df_sum.applymap(lambda x: f"{x:.4f}" if isinstance(x, (float, int)) else x)
    table_data = df_sum.to_dict('records')
    table_cols = [{'name': c, 'id': c} for c in df_sum.columns]

    # IV shift
    df_iv = ep.iv_shift()
    fig_iv = go.Figure()
    fig_iv.add_trace(go.Bar(x=df_iv['Option'], y=df_iv['IV Pre (%)'], name='IV Pre', marker_color=SECONDARY))
    fig_iv.add_trace(go.Bar(x=df_iv['Option'], y=df_iv['IV Post (%)'], name='IV Post', marker_color=PRIMARY))
    fig_iv.update_layout(barmode='group', title='Implied Volatility Shift', template='plotly_white')

    # Premium change
    df_prem = ep.premium_pct_change()
    fig_prem = go.Figure(go.Bar(x=df_prem['Option'], y=df_prem['PctChange'], marker_color=SECONDARY))
    fig_prem.update_layout(title='Premium % Change (Post vs. Pre)', template='plotly_white')

    # New Chart: Forward vs Straddle Price
    fig_price_comp = go.Figure()
    fig_price_comp.add_trace(go.Bar(x=df_sum['Scenario'], y=[float(x) for x in df_sum['Forward Price']], name='Forward Price', marker_color=PRIMARY))
    fig_price_comp.add_trace(go.Bar(x=df_sum['Scenario'], y=[float(x) for x in df_sum['Straddle Price']], name='Straddle Price', marker_color=SECONDARY))
    fig_price_comp.update_layout(barmode='group', title='Forward vs Straddle Price', template='plotly_white')

    # New Chart: Straddle Payoff Diagram
    S_range = np.linspace(float(s0)*0.5, float(s0)*1.5, 100)
    payoff = np.abs(S_range - float(s0))
    fig_payoff = go.Figure(go.Scatter(x=S_range, y=payoff, mode='lines', line={'color': SECONDARY}))
    fig_payoff.update_layout(title='Straddle Payoff Diagram', xaxis_title='Underlying Price', yaxis_title='Payoff', template='plotly_white')

    return vol_text, table_data, table_cols, fig_iv, fig_prem, fig_price_comp, fig_payoff

# if __name__ == '__main__':
#     app.run(debug=True)

# expose Flask server for Gunicorn
server = app.server

if __name__=='__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port, debug=True)
