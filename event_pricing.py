import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm
from scipy.optimize import brentq


class BlackScholes:
    """
    Black-Scholes pricing and greeks for European options.
    """
    def __init__(self, S: float, K: float, T: float, r: float = 0.0, q: float = 0.0):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.q = q
    
    @staticmethod
    def calc_price(S: float, K: float, T: float, r: float, q: float,
                   sigma: float, call: bool = True) -> float:
        """Calculate Black-Scholes European option price."""
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if call:
            return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    
    def price(self, sigma: float, call: bool = True) -> float:
        """Instance wrapper around calc_price."""
        return BlackScholes.calc_price(self.S, self.K, self.T,
                                       self.r, self.q, sigma, call)
    
    def _d1(self, sigma: float) -> float:
        return (np.log(self.S / self.K) + (self.r - self.q + 0.5 * sigma**2) * self.T) / (sigma * np.sqrt(self.T))
        
    def delta(self, sigma: float, call: bool = True) -> float:
        """Delta for given volatility."""
        d1 = self._d1(sigma)
        return (np.exp(-self.q * self.T) * norm.cdf(d1)) if call else (-np.exp(-self.q * self.T) * norm.cdf(-d1))
    
    @staticmethod
    def find_strike(S: float, T: float, r: float, q: float,
                    sigma: float, target_delta: float, call: bool = True,
                    bracket: tuple = (1e-6, None)) -> float:
        """Find the strike where option delta equals target delta."""
        a, b = bracket
        b = b or S * 10
        f = lambda K: BlackScholes(S, K, T, r, q).delta(sigma, call) - target_delta
        return brentq(f, a, b)
    
    @staticmethod
    def find_ivol(price: float, S: float, K: float, T: float,
                  r: float, q: float, call: bool = True) -> float:
        """Invert BS price to find implied volatility via Brent root-find."""
        f = lambda vol: BlackScholes.calc_price(S, K, T, r, q, vol, call) - price
        return brentq(f, 1e-6, 5.0)
    

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
        self.S0 = S0                                                # baseline price
        self.ann_vol = ann_vol                                      # annualzied base volatility
        self.r = r                                                  # interest rate
        self.q = q                                                  # dividend yield
        self.normal_days = normal_days                              # normal volality days
        self.non_tdays = non_tdays                                  # zero vol days (non trading days)
        self.event_days = event_days                                # jump day
        self.event_multiplier = event_multiplier                    # event variance multiplier
        self.prob_up = prob_up                                      # event upside probability
        self.target_delta = target_delta                            # target delta for strike finding
        self.T = (normal_days + non_tdays + event_days) / 252.0     # year fraction
        self._compute_effective_vol()

    def _compute_effective_vol(self):
        """Effective annualized volatility."""
        daily_var = self.ann_vol**2 / 252.0
        event_var = daily_var * self.event_multiplier
        period_var = (self.normal_days * daily_var + 
                      self.non_tdays * 0.0 +
                      self.event_days * event_var)
        self.eff_vol = np.sqrt(period_var / self.T)

    def forward_price(self) -> float:
        """Pre-announcement forward price."""
        return self.S0 * np.exp((self.r - self.q) * self.T)
    
    def jump_factors(self) -> tuple:
        """Compute up/down jump factors."""
        T_event = self.event_days / 252.0
        vol_event = self.ann_vol * np.sqrt(self.event_multiplier)
        up = np.exp(vol_event * np.sqrt(T_event))
        down = np.exp(-vol_event * np.sqrt(T_event))
        return up, down
    
    def drifted_forward(self) -> float:
        """Post-announcement forward price under jump probabilities."""
        up, down = self.jump_factors()
        prob_down = 1 - self.prob_up
        return self.S0 * (self.prob_up * up + prob_down * down)
    
    def price_scenario(self, S: float) -> dict:
        """
        Price ATM straddle and 25-delta wings at spot S.
        Returns a dictionary with forward, straddle, put strike, put price, call strike, call price.
        """
        bs = BlackScholes(S, S, self.T, self.r, self.q)
        fwd = S * np.exp((self.r - self.q) * self.T)

        atm_call = bs.price(self.eff_vol, call=True)
        atm_put = bs.price(self.eff_vol, call=False)
        straddle = atm_call + atm_put

        Kp = BlackScholes.find_strike(S, self.T, self.r, self.q, self.eff_vol, -self.target_delta, call=False)
        Kc = BlackScholes.find_strike(S, self.T, self.r, self.q, self.eff_vol, self.target_delta, call=True)
        p = BlackScholes(S, Kp, self.T, self.r, self.q).price(self.eff_vol, call=False)
        c = BlackScholes(S, Kc, self.T, self.r, self.q).price(self.eff_vol, call=True)

        return {
            'forward': fwd,
            'straddle': straddle,
            'put_strike': Kp,
            'put_price': p,
            'call_strike': Kc,
            'call_price': c
        }
    
    def summary(self) -> pd.DataFrame:
        """Return DataFrame comparing pre vs post scenario."""
        pre = self.price_scenario(self.S0)
        post = self.price_scenario(self.drifted_forward())
        return pd.DataFrame([
            {'Scenario': 'Pre', **pre},
            {'Scenario': 'Post', **post}
        ])

    def iv_shift(self) -> pd.DataFrame:
        """
        Returns a DataFrame with index Option and columns ['Pre','Post'] giving
        the implied vols (%), *inverted* from the prices (including ATM straddle).
        """
        # get pre and post scenario data
        pre = self.price_scenario(self.S0)
        post = self.price_scenario(self.drifted_forward())
        # define options list
        options = [
            ("ATM Straddle", self.S0, self.S0, pre['straddle'], post['straddle'], True),
            ("25Δ Put",       self.S0, pre['put_strike'],  pre['put_price'],  post['put_price'],  False),
            ("25Δ Call",      self.S0, pre['call_strike'], pre['call_price'], post['call_price'], True),
        ]
        rows = []
        for name, S, K, p_pre, p_post, is_call in options:
            iv_pre  = BlackScholes.find_ivol(p_pre,  S, K, self.T, self.r, self.q, call=is_call) * 100
            iv_post = BlackScholes.find_ivol(p_post, S, K, self.T, self.r, self.q, call=is_call) * 100
            pct      = (iv_post - iv_pre) / iv_pre * 100
            rows.append({
                'Option':     name,
                'IV Pre (%)': iv_pre,
                'IV Post (%)': iv_post,
                '% Change':   pct
            })
        return pd.DataFrame(rows)
    
    def premium_pct_change(self):
        """
        Returns a DataFrame with columns ['Option','Pre','Post','PctChange'] for
        ATM Straddle, 25Δ Put, 25Δ Call.
        """
        df = self.summary().set_index('Scenario')
        pre, post = df.loc['Pre'], df.loc['Post']
        out = []
        for name, col in [('ATM Straddle','straddle'),
                          ('25Δ Put','put_price'),
                          ('25Δ Call','call_price')]:
            pct = (post[col] - pre[col]) / pre[col] * 100
            out.append({
                'Option': name,
                'Pre': pre[col],
                'Post': post[col],
                'PctChange': pct
            })
        return pd.DataFrame(out)


if __name__ == '__main__':
    ep = EventPricing()
    print(f"Effective annualzied volatility: {ep.eff_vol: .6%}")
    print(ep.summary())