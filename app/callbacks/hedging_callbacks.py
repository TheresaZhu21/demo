import pandas as pd
from dash import dcc, Input, Output, State, callback_context


def register_hedging_callbacks(app, positions: pd.DataFrame):
    # Callback for Hedge Table
    @app.callback(
        [
            Output('hedge-table-container', 'style'),
            Output('hedge-table', 'data'),
            Output('mkt-dropdown', 'value'),
            Output('book-dropdown', 'value'),
        ],
        [
            Input('generate-btn', 'n_clicks'),
            Input('clear-btn', 'n_clicks'),
            Input('mkt-dropdown', 'value'),
            Input('book-dropdown', 'value'),
        ]
    )
    def update_hedge_table(generate_clicks, clear_clicks, selected_market, selected_books):
        ctx = callback_context
        default_market = None
        default_books = []

        if not ctx.triggered:
            return {'display': 'none'}, [], default_market, default_books # initial state: hidden, no data
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Clear button: hide table and reset dropdowns
        if triggered_id == 'clear-btn':
            return {'display': 'none'}, [], default_market, default_books
        
        if triggered_id in ('generate-btn', 'mkt-dropdown', 'book-dropdown'):
            df = positions.copy()
            # Filter by market
            if selected_market:
                df = df[df['Market'] == selected_market]
            # Fitler by books (multi-select)
            if selected_books:
                books = (selected_books if isinstance(selected_books, (list, tuple)) else [selected_books])
                df = df[df['Book'].isin(books)]
            # If no rows after filtering, hide table but keep dropdown selections
            if df.empty:
                return {'display': 'none'}, [], selected_market, selected_books
            # Otherwise, show fitlered rows and preserve selections
            return {'display': 'block'}, df.to_dict('records'), selected_market, selected_books
        
        # Fallback: hide and reset
        return {'display': 'none'}, [], default_market, default_books

    # Clientcallback to do the actual copying for hedge table
    app.clientside_callback(
        """
        function(n_clicks) {
            if (!n_clicks) {return '';}
            // find the <table> inside the DataTable component
            const tbl = document.querySelector('#hedge-table table');
            if (!tbl) {return '';}
            // select its text
            const range = document.createRange();
            range.selectNode(tbl);
            const sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
            // copy to clipboard
            document.execCommand('copy'); sel.removeAllRanges();
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
        State('mkt-dropdown', 'value'), 
        State('book-dropdown', 'value'),
        prevent_initial_call=True
    )
    def download_orders(n_clicks, selected_market, selected_books):
        # when clicked, package the master df as CSV
        df = positions.copy()
        if selected_market:
            df = df[df['Market'] == selected_market]
        if selected_books:
            books = (selected_books if isinstance(selected_books, (list, tuple)) else [selected_books])
            df = df[df['Book'].isin(books)]
        return dcc.send_data_frame(df.to_csv, "hedge_orders.csv", index=False)