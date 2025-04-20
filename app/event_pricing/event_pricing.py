import numpy as np
import pandas as pd
from .black_scholes import BlackScholes

class EventPricing:
    """
    Compute option prices before and after a discrete event.
    """
    def __init__(self, 
                 S0: float = 100.0, 
                 ann_vol: float = 0.30, 
                 r: float = 0.0, 
                 q: float = 0.0,
                 normal_days: int = 7,
                 non_tdays: int = 2,
                 event_days: int = 1,
                 event_multiplier: float = 2.0,
                 prob_up: float = 0.9,
                 target_delta: float = 0.25):
        self.S0 = S0
        self.ann_vol = ann_vol
        self.r = r
        self.q = q
        self.normal_days = normal_days
        self.non_tdays = non_tdays
        self.event_days = event_days
        self.event_multiplier = event_multiplier
        self.prob_up = prob_up
        self.target_delta = target_delta
        self.T = (normal_days + non_tdays + event_days) / 252.0
        self._compute_effective_vol()

    def _compute_effective_vol(self):
        daily_var = self.ann_vol**2 / 252.0
        event_var = daily_var * self.event_multiplier
        period_var = (self.normal_days * daily_var +
                      self.non_tdays * 0.0 +
                      self.event_days * event_var)
        self.eff_vol = np.sqrt(period_var / self.T)

    def forward_price(self) -> float:
        return self.S0 * np.exp((self.r - self.q) * self.T)
    
    def jump_factors(self) -> tuple:
        T_event = self.event_days / 252.0
        vol_event = self.ann_vol * np.sqrt(self.event_multiplier)
        return np.exp(vol_event * np.sqrt(T_event)), np.exp(-vol_event * np.sqrt(T_event))
    
    def drifted_forward(self) -> float:
        up, down = self.jump_factors()
        return self.S0 * (self.prob_up * up + (1 - self.prob_up) * down)

    def price_scenario(self, S: float) -> dict:
        bs = BlackScholes(S, S, self.T, self.r, self.q)
        fwd = self.forward_price() if S == self.S0 else S * np.exp((self.r - self.q) * self.T)
        atm_call = bs.price(self.eff_vol, call=True)
        atm_put = bs.price(self.eff_vol, call=False)
        straddle = atm_call + atm_put
        Kp = BlackScholes.find_strike(S, self.T, self.r, self.q, self.eff_vol, -self.target_delta, call=False)
        Kc = BlackScholes.find_strike(S, self.T, self.r, self.q, self.eff_vol, self.target_delta, call=True)
        p = BlackScholes(S, Kp, self.T, self.r, self.q).price(self.eff_vol, call=False)
        c = BlackScholes(S, Kc, self.T, self.r, self.q).price(self.eff_vol, call=True)
        return {'forward': fwd, 'straddle': straddle,
                'put_strike': Kp, 'put_price': p,
                'call_strike': Kc, 'call_price': c}

    def summary(self) -> pd.DataFrame:
        pre = self.price_scenario(self.S0)
        post = self.price_scenario(self.drifted_forward())
        return pd.DataFrame([{'Scenario': 'Pre', **pre}, {'Scenario': 'Post', **post}])

    def iv_shift(self) -> pd.DataFrame:
        delta_pct = int(self.target_delta * 100)
        label = f"{delta_pct}Δ"
        pre = self.price_scenario(self.S0)
        post = self.price_scenario(self.drifted_forward())
        rows = []
        for name, S, K, p_pre, p_post, is_call in [
            ("ATM Straddle", self.S0, self.S0, pre['straddle'], post['straddle'], True),
            (f"{label} Put", self.S0, pre['put_strike'], pre['put_price'], post['put_price'], False),
            (f"{label} Call", self.S0, pre['call_strike'], pre['call_price'], post['call_price'], True)
        ]:
            iv_pre = BlackScholes.find_ivol(p_pre, S, K, self.T, self.r, self.q, call=is_call) * 100
            iv_post = BlackScholes.find_ivol(p_post, S, K, self.T, self.r, self.q, call=is_call) * 100
            pct = (iv_post - iv_pre) / iv_pre * 100
            rows.append({'Option': name, 'IV Pre (%)': iv_pre, 'IV Post (%)': iv_post, '% Change': pct})
        return pd.DataFrame(rows)

    def premium_pct_change(self) -> pd.DataFrame:
        delta_pct = int(self.target_delta * 100)
        label = f"{delta_pct}Δ"
        df = self.summary().set_index('Scenario')
        pre, post = df.loc['Pre'], df.loc['Post']
        out = []
        for name, col in [("ATM Straddle", 'straddle'), (f"{label} Put", 'put_price'), (f"{label} Call", 'call_price')]:
            pct = (post[col] - pre[col]) / pre[col] * 100
            out.append({'Option': name, 'Pre': pre[col], 'Post': post[col], 'PctChange': pct})
        return pd.DataFrame(out)