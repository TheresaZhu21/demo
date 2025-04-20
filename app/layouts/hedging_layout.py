import pandas as pd
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from config import PRIMARY, SECONDARY, BACKGROUND


def hedging_layout(positions):
    columns = [{'name': c, 'id': c} for c in positions.columns]
    return html.Div([
        html.H4("Hedging Orders", style={'textAlign': 'left', 'marginBottom': '1rem', 'color': PRIMARY}),

        # Row 1: market & style
        dbc.Row([
            # Market selector
            dbc.Col(
                [
                    html.Div("Market:", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='mkt-dropdown',
                        options=[{'label': m,'value': m} for m in ['US', 'EU', 'HK', 'AU', 'IN', 'JP']],
                        # value='US',
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
                html.Div("Cutoff Time (Local Timezone):", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                dbc.Input(id='hedge-time', type='time', value='16:00', style={'width': '100%'}),
            ], width=2)
        ], className='mb-4', align='center'),

        # Row 3: Trader books
        dbc.Row([
            dbc.Col([
                html.Div("Hedge Trader Books:", style={'marginBottom': '0.25rem', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='book-dropdown',
                    options=[
                        {'label':'Book1','value':'B1'},
                        {'label':'Book2','value':'B2'},
                        {'label':'Book3','value':'B3'},
                    ],
                    placeholder='Select books',
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
                                data=positions.to_dict('records'),
                                page_size=15,
                                style_table={'overflowX': 'auto', 'width': '100%'},
                                style_header={'backgroundColor': PRIMARY, 'color': 'white', 'fontWeight': 'bold'},
                                style_cell={'textAlign': 'center', 'padding': '0.5rem'},
                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': BACKGROUND}]
                            )
                        )
                    ], 
                    className='h-100',
                    style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'height': '100%', 'width': '100%'}
                ),
                dbc.Row([
                    dbc.Col(dbc.Button("Copy Orders", id='copy-orders-btn', color='warning'), width='auto'),
                    dbc.Col(dbc.Button("Download Orders", id='download-orders-btn', color='info'), width='auto'),
                ], className='mt-4', align='center'),
                dcc.Download(id='download-orders'),
            ], width=11),
            id='hedge-table-container',
            style={'display': 'none', 'width': '100%', 'overflowX': 'auto'}
        )
    ])
