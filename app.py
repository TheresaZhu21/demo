"""
app.py for Demo Research and Trade Dashboard
Author: Theresa Zhu
Date: Apr 17, 2025
"""
import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from event_pricing import EventPricing

external_stylesheets = [dbc.themes.FLATLY]  # theme
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server  # expose for deployment

# Color palette
PRIMARY = "#2C3E50"      # Deep blue-grey
SECONDARY = "#18BC9C"    # Teal accent
BACKGROUND = "#F5F7FA"   # Light grey

# Fake hedge df
_HEDGE_DF = pd.DataFrame({
    'Symbol':           ['Symbol1',  'Symbol2',   'Symbol3'],
    'Spot':              [100.23,     150.45,      200.67],
    'Spot % Move':       ['+1.2%',    '-0.5%',     '+0.8%'],
    'Delta':             [10000,      -5000,       7500],
    'Skew Delta':        [850,        -220,        600],
    'Gamma':             [45,         30,          75],
    'Restriction':       ['None',     'MaxSell',   'None'],
    'Max Long':          [120,        80,          100],
    'Managed Delta':     [10850,      -4780,       8100],
    'Max Sell':          [5000,       3000,        4000],
    'Max Buy':           [6000,       3500,        4500],
    'Target Delta':      [11000,      -5500,       8200],
    'Target Exec Delta': [10500,      -5300,       7900],
    'Target Exec Shrs':  [105,        -53,         79],
    'Permitted Pct':     ['100%',     '90%',        '95%'],
    'Limit Reached':     [False,      True,        False]
})
_HEDGE_COLUMNS = [{'name': c, 'id': c} for c in _HEDGE_DF.columns]

# Event Pricing layout
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

# Execution hedging layout placeholder
def hedging_layout():
    df = _HEDGE_DF
    columns = _HEDGE_COLUMNS
    return html.Div([
        html.H4("Hedging Orders", style={'textAlign': 'left', 'marginBottom': '1rem', 'color': PRIMARY}),

        # Row 1: market & style
        dbc.Row([
            # Market selector
            dbc.Col(
                [
                    html.Div("Market:", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        options=[{'label': m,'value': m} for m in ['US', 'EU', 'HK', 'AU', 'IN', 'JP']],
                        value='US',
                        placeholder='Select Market'
                    ),
                ], width=1
            ),
            # Style selector
            dbc.Col(
                [
                    html.Div("Style:", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        options=[{'label': s,'value': s} for s in ['Limit on Close', 'Inline', 'VWAP']],
                        value='Limit on Close',
                        placeholder='Select Hedge Style'
                    ),
                ], width=2
            ),
        ], className='mb-4', align='center'),

        # Row 2: cutoff date & time
        dbc.Row([
            dbc.Col([
                html.Div("Cutoff Date:", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                dcc.DatePickerSingle(id='hedge-date', date=pd.to_datetime('today'), style={'width': '100%'}),
            ], width=1),
            dbc.Col([
                html.Div("Cutoff Time:", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                dbc.Input(id='hedge-time', type='time', value='16:00', style={'width': '100%'}),
            ], width=2)
        ], className='mb-4', align='center'),

        # Row 3: Trader books
        dbc.Row([
            dbc.Col([
                html.Div("Hedge Trader Books:", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    options=[
                        {'label':'Book1','value':'B1'},
                        {'label':'Book2','value':'B2'},
                        {'label':'Book3','value':'B3'},
                    ],
                    placeholder='Book1',
                    multi=True,
                )
            ], width=3),
        ], className='mb-4', align='center'),

        # Row 4: auto-check restrictions
        dbc.Row([
            dbc.Col(dbc.Switch(id='auto-check-switch', label='Auto check trade restrictions', value=True, input_class_name='bg-info', style={'marginBottom': '0.5rem'}), width='auto'),
        ], className='mb-2', align='center'),

        # Row 5: generate & cancel button
        dbc.Row([
            dbc.Col(dbc.Button('Generate', id='generate-btn', color='success'), width='auto'),
            dbc.Col(dbc.Button('Clear', id='clear-btn', color='danger'), width='auto'),
        ], className='mb-4', align='center'),

        # Hedging orders table
        html.Div(
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardHeader("Risks", style={'borderBottom': f'2px solid {SECONDARY}'}),
                        dbc.CardBody(
                            dash_table.DataTable(
                                id='hedge-table',
                                columns=columns,
                                data=df.to_dict('records'),
                                page_size=10,
                                style_table={'overflowX': 'auto'},
                                style_header={'backgroundColor': PRIMARY, 'color': 'white', 'fontWeight': 'bold'},
                                style_cell={'textAlign': 'center', 'padding': '0.5rem'},
                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': BACKGROUND}]
                            )
                        )
                    ], 
                    className='h-100',
                    style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'height': '100%'}
                ),
                dbc.Row([
                    dbc.Col(dbc.Button("Copy Orders", id='copy-orders-btn', color='warning'), width='auto'),
                    dbc.Col(dbc.Button("Download Orders", id='download-orders-btn', color='info'), width='auto'),
                ], className='mt-4', align='center'),
                dcc.Download(id='download-orders'),
            ], width=9),
            id='hedge-table-container',
            style={'display': 'none'}
        )
    ])


# Risk & PnL subtools placeholder
def pnl_analytics_layout():
    return html.Div([
        html.H4("PnL Analytics", style={'textAlign': 'left'}),
        html.Div("PnL Analytics content coming soon.")
    ])

# Main layout with header and sidebar
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

app.layout = generate_layout()

# Toggle collapses
@app.callback(
    Output("collapse-research", "is_open"),
    [Input("tab-research", "n_clicks")],
    [State("collapse-research", "is_open")]
)
def toggle_research(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-execution", "is_open"),
    [Input("tab-execution", "n_clicks")],
    [State("collapse-execution", "is_open")]
)
def toggle_execution(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-riskpnl", "is_open"),
    [Input("tab-riskpnl", "n_clicks")],
    [State("collapse-riskpnl", "is_open")]
)
def toggle_riskpnl(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

# Render content based on current subtab
@app.callback(
    Output('page-content', 'children'),
    [
        Input('subtab-screener', 'n_clicks'),
        Input('subtab-backtester', 'n_clicks'),
        Input('subtab-eventpricing', 'n_clicks'),
        Input('subtab-hedging', 'n_clicks'),
        Input('subtab-pnlanalytics', 'n_clicks')
    ]
)
def render_content(screener, backt, ep, hedging, pnlanalytics):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div()
    sub = ctx.triggered[0]['prop_id'].split('.')[0]
    if sub == 'subtab-eventpricing':
        return event_pricing_layout()
    elif sub == 'subtab-hedging':
        return hedging_layout()
    elif sub == 'subtab-pnlanalytics':
        return pnl_analytics_layout()
    return html.Div(f"{sub} content coming soon.")

# Callback for Event Pricing charts
@app.callback(
    [Output('output-vol', 'children'), Output('output-table', 'data'), Output('output-table', 'columns'),
     Output('output-iv-chart', 'figure'), Output('output-chart', 'figure'),
     Output('price-comp-chart', 'figure'), Output('straddle-payoff-chart', 'figure')],
    [Input('compute-btn', 'n_clicks'), Input('input-s0', 'value'), Input('input-ann-vol', 'value'),
     Input('input-r', 'value'), Input('input-q', 'value'), Input('input-normal-days', 'value'),
     Input('input-non-tdays', 'value'), Input('input-event-days', 'value'),
     Input('input-event-multiplier', 'value'), Input('input-prob-up', 'value'),
     Input('input-target-delta', 'value')]
)
def update_event_pricing(n_clicks, s0, ann_vol, r, q,
                         normal_days, non_tdays, event_days,
                         event_multiplier, prob_up, target_delta):
    if not n_clicks:
        return [no_update]*7
    ep = EventPricing(
        S0=float(s0), ann_vol=float(ann_vol) / 100, r=float(r) / 100, q=float(q) / 100,
        normal_days=int(normal_days), non_tdays=int(non_tdays),
        event_days=int(event_days), event_multiplier=float(event_multiplier),
        prob_up=float(prob_up) / 100, target_delta=float(target_delta) / 100
    )
    vol_text = f"{ep.eff_vol:.2%}"
    df_sum = ep.summary()
    df_sum.columns = ["Scenario", "Forward Price", "Straddle Price", f"{target_delta}Δ Put Strike", f"{target_delta}Δ Put Price", f"{target_delta}Δ Call Strike", f"{target_delta}Δ Call Price"]
    df_sum = df_sum.applymap(lambda x: f"{x:.4f}" if isinstance(x,(float,int)) else x)
    data = df_sum.to_dict('records')
    cols = [{'name': c,'id': c} for c in df_sum.columns]
    df_iv = ep.iv_shift()
    fig_iv = go.Figure()
    fig_iv.add_trace(go.Bar(x=df_iv['Option'], y=df_iv['IV Pre (%)'], name='IV Pre', marker_color=SECONDARY))
    fig_iv.add_trace(go.Bar(x=df_iv['Option'], y=df_iv['IV Post (%)'], name='IV Post', marker_color=PRIMARY))
    fig_iv.update_layout(barmode='group', title='Implied Volatility Shift', template='plotly_white')
    df_prem = ep.premium_pct_change()
    fig_prem = go.Figure(go.Bar(x=df_prem['Option'], y=df_prem['PctChange'], marker_color=SECONDARY))
    fig_prem.update_layout(title='Premium % Change (Post vs. Pre)', template='plotly_white')
    fig_price_comp = go.Figure()
    fig_price_comp.add_trace(go.Bar(x=df_sum['Scenario'], y=[float(x) for x in df_sum['Forward Price']], name='Forward Price', marker_color=PRIMARY))
    fig_price_comp.add_trace(go.Bar(x=df_sum['Scenario'], y=[float(x) for x in df_sum['Straddle Price']], name='Straddle Price', marker_color=SECONDARY))
    fig_price_comp.update_layout(barmode='group', title='Forward vs Straddle Price', template='plotly_white')
    S_range = np.linspace(float(s0)*0.5, float(s0)*1.5,100)
    payoff = np.abs(S_range - float(s0))
    fig_payoff = go.Figure(go.Scatter(x=S_range,y=payoff,mode='lines',line={'color':SECONDARY}))
    fig_payoff.update_layout(title='Straddle Payoff Diagram', xaxis_title='Underlying Price', yaxis_title='Payoff', template='plotly_white')
    return vol_text, data, cols, fig_iv, fig_prem, fig_price_comp, fig_payoff

# Callback for Hedge Table
@app.callback(
    [
        Output('hedge-table-container', 'style'),
        Output('hedge-table', 'data'),
    ],
    [
        Input('generate-btn', 'n_clicks'),
        Input('clear-btn', 'n_clicks'),
    ]
)
def generate_or_clear_hedge_table(generate_clicks, clear_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'none'}, [] # initial state: hidden, no data
    
    clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if clicked_id == 'generate-btn':
        return {'display': 'block'}, _HEDGE_DF.to_dict('records')
    else:
        return {'display': 'none'}, []

# Clientcallback to do the actual copying for hedge table
app.clientside_callback(
    """
    function(n_clicks) {
      if (!n_clicks) {
        return '';
      }
      // find the <table> inside the DataTable component
      const tbl = document.querySelector('#hedge-table table');
      if (!tbl) {
        return '';
      }
      // select its text
      const range = document.createRange();
      range.selectNode(tbl);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      // copy to clipboard
      document.execCommand('copy');
      sel.removeAllRanges();
      return '';
    }
    """,
    Output('copy-orders-btn', 'n_clicks'),  # dummy output
    Input('copy-orders-btn', 'n_clicks')
)

# Callback to download the orders
@app.callback(
    Output('download-orders', 'data'),
    Input('download-orders-btn', 'n_clicks'),
    prevent_initial_call=True
)
def download_orders(n_clicks):
    # when clicked, package the master df as CSV
    return dcc.send_data_frame(_HEDGE_DF.to_csv, "hedge_orders.csv", index=False)



if __name__ == '__main__':
    app.run(debug=True)



# if __name__=='__main__':
#     import os
#     port = int(os.environ.get('PORT', 8050))
#     app.run_server(host='0.0.0.0', port=port, debug=True)
