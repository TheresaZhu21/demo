import numpy as np
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
    
    @staticmethod
    def find_straddle_ivol(straddle_price: float, S: float, K: float, T: float, r: float, q: float) -> float:
        """Invert BS price to find implied volatility for straddle via Brent root-find."""
        f = lambda vol: (BlackScholes.calc_price(S, K, T, r, q, vol, call=True)
                         + BlackScholes.calc_price(S, K, T, r, q, vol, call=False)
                         - straddle_price)
        return brentq(f, 1e-6, 5.0)