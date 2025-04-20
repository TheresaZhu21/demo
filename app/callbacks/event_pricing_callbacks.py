from dash import Input, Output, no_update
import numpy as np
import plotly.graph_objects as go
from ..event_pricing import EventPricing
from ..config import PRIMARY, SECONDARY, BACKGROUND


def register_event_pricing_callbacks(app):
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