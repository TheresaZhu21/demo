from dash import Input, Output, State, callback_context, html
from ..layouts.event_pricing_layout import event_pricing_layout
from ..layouts.hedging_layout import hedging_layout
from ..layouts.event_pricing_layout import event_pricing_layout
from ..layouts.hedging_layout import hedging_layout
from ..layouts.pnl_analytics_layout import pnl_analytics_layout


def register_navigation_callbacks(app, positions):
    # Toggle Research collapse
    @app.callback(
        Output("collapse-research", "is_open"),
        [Input("tab-research", "n_clicks")],
        [State("collapse-research", "is_open")]
    )
    def toggle_research(n, is_open):
        return not is_open if n else is_open

    # Toggle Execution collapse
    @app.callback(
        Output("collapse-execution", "is_open"),
        [Input("tab-execution", "n_clicks")],
        [State("collapse-execution", "is_open")]
    )
    def toggle_execution(n, is_open):
        return not is_open if n else is_open

    # Toggle Risk&PnL collapse
    @app.callback(
        Output("collapse-riskpnl", "is_open"),
        [Input("tab-riskpnl", "n_clicks")],
        [State("collapse-riskpnl", "is_open")]
    )
    def toggle_riskpnl(n, is_open):
        return not is_open if n else is_open

    # Render page content
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
    def render_content(screener, backt, ep, hedging, pnl):
        ctx = callback_context
        if not ctx.triggered:
            return html.Div()
        sub = ctx.triggered[0]['prop_id'].split('.')[0]
        if sub == 'subtab-eventpricing':
            return event_pricing_layout()
        if sub == 'subtab-hedging':
            return hedging_layout(positions)
        if sub == 'subtab-pnlanalytics':
            return pnl_analytics_layout()
        return html.Div(f"{sub} content coming soon.")