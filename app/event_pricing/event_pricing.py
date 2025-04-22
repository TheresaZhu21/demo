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
        for name, S, K_pre, K_post, price_pre, price_post, is_call in [
            ("ATM Straddle", self.S0, self.S0, self.S0, pre['straddle'], post['straddle'], True),
            (f"{label} Put", self.S0, pre['put_strike'], post['put_strike'], pre['put_price'], post['put_price'], False),
            (f"{label} Call", self.S0, pre['call_strike'], post['call_strike'], pre['call_price'], post['call_price'], True)
        ]:
            iv_pre = BlackScholes.find_ivol(price_pre, S, K_pre, self.T, self.r, self.q, call=is_call) * 100
            iv_post = BlackScholes.find_ivol(price_post, S, K_post, self.T, self.r, self.q, call=is_call) * 100
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
    
    def skew(self):
        moneyness = np.linspace(0.75, 1.25, 50) # strikes from 75% to 125% of spot
        strikes = moneyness * self.S0
        u, d = self.jump_factors()
        ivs_pre, ivs_post = [], []

        for K in strikes:
            # pre: flat BS
            price_pre = BlackScholes.calc_price(self.S0, K, self.T, self.r, self.q, self.eff_vol, call=True)
            try:
                iv_pre = BlackScholes.find_ivol(price_pre, self.S0, K, self.T, self.r, self.q, call=True) * 100
            except Exception:
                iv_pre = np.nan
            ivs_pre.append(iv_pre)

            # post: 
            S = self.drifted_forward() # drifted forward
            # is_call = (K >= S)
            is_call = True
            price_post = BlackScholes(S, K, self.T, self.r, self.q).price(self.eff_vol, call=is_call)
            try:
                iv_post = BlackScholes.find_ivol(price_post, self.S0, K, self.T, self.r, self.q, call=is_call) * 100
            except Exception:
                iv_post = np.nan
            ivs_post.append(iv_post)
        return (moneyness, ivs_pre, ivs_post)
    
    def pdf(self):
        moneyness, ivs_pre, ivs_post = self.skew()
        strikes = np.array(moneyness) * self.S0
        F = self.forward_price()
        pdf_implied, pdf_lognormal = [], []
        for K, iv_post_pct in zip(strikes, ivs_post):
            # Implied risk-neutral density via lognormal at moneyness
            sigma_imp = iv_post_pct / 100.0
            mu_imp = np.log(F) - 0.5 * sigma_imp**2 * self.T
            pdf_implied.append(
                1 / (K * sigma_imp * np.sqrt(2 * np.pi * self.T)) *
                np.exp(- (np.log(K) - mu_imp)**2 / (2 * sigma_imp**2 * self.T))
            )

            # Baseline lognormal from effective volatility
            sigma_ln = self.eff_vol
            mu_ln = np.log(F) - 0.5 * sigma_ln**2 * self.T
            pdf_lognormal.append(
                1 / (K * sigma_ln * np.sqrt(2 * np.pi * self.T)) *
                np.exp(- (np.log(K) - mu_ln)**2 / (2 * sigma_ln**2 * self.T))
            )
        return (strikes, pdf_implied, pdf_lognormal)