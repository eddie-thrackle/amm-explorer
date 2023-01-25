from typing import List, Tuple
import dataclasses
# The Pool class depends on Sympy.
# Familiarize [here](https://docs.sympy.org/) before editing this code.
from sympy import Symbol, integrate, Piecewise
from sympy.core.expr import Expr
from sympy.plotting.plot import plot
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
custom_params = {"axes.spines.right": False, "axes.spines.top": False, "figure.facecolor": "#A09ABC", "axes.facecolor": "#D5CFE1"}
sns.set_theme(style="ticks", rc=custom_params)

ASSET_HANDLES = ['x', 'y']
SYMBOL_LOOKUP = {
    asset_str: Symbol(asset_str, real=True, positive=True)
    for asset_str in ASSET_HANDLES
}
N_PTS_PER_CURVE = 100

@dataclasses.dataclass
class CurveSegment:
    expression: Expr
    domain_width: int

class Pool:
    
    def __init__(self, initial_tbc_segments : List[CurveSegment] = None) -> None:
        "After constructor, the TBC and AMM visualization's call stack must be ready."
        self.tbc_segments = initial_tbc_segments
        self.global_domain = (0, sum([
            segment.domain_width for segment in self.tbc_segments]))
        # self.exchange_history = {'sell_symbol': [], 'sell_amount': [], 'buy_symbol': [], 'buy_amount': []}

    def extend_tbc(self, segment : CurveSegment) -> None:
        self.tbc_segments.append(segment)
        self.global_domain[1] += segment.domain_width

    @property
    def amm_curve(self, symbol : str = 'x') -> List[CurveSegment]:
        symbol = SYMBOL_LOOKUP[symbol]
        pieces = []
        latest_domain_tick = 0
        for segment in self.tbc_segments:
            pieces.append((
                segment.expression, 
                (symbol > latest_domain_tick) & (symbol <= latest_domain_tick + segment.domain_width)
            ))
            latest_domain_tick += segment.domain_width
        integrated_tbc_segments = integrate(Piecewise(*pieces))
        amm_segments = integrated_tbc_segments.subs(symbol, self.global_domain[1] - symbol)
        return Piecewise(*pieces), integrated_tbc_segments, amm_segments

    def plot(self, symbol : str = 'x') -> Tuple[plt.Figure, plt.Axes]:
        symbol = SYMBOL_LOOKUP[symbol]
        pieces, integrated_tbc_segments, amm_segments = self.amm_curve
        domain_grid = np.linspace(*self.global_domain, N_PTS_PER_CURVE)
        tbc = []; tbc_int = []; amm = []
        for _grid_pt in domain_grid:
            tbc.append(pieces.subs(symbol, _grid_pt))
            tbc_int.append(integrated_tbc_segments.subs(symbol, _grid_pt))
            amm.append(amm_segments.subs(symbol, _grid_pt))
        fig, ax = plt.subplots(1,1, figsize=(8,6))
        ax.plot(domain_grid, tbc, label='TBC')
        ax.plot(domain_grid, tbc_int, label='TBC integrated')
        ax.plot(domain_grid, amm, label='AMM')
        ax.set_xlabel(list(SYMBOL_LOOKUP.keys())[0])
        ax.set_ylabel(list(SYMBOL_LOOKUP.keys())[1])
        ax.legend()
        return fig, ax
     
### Usage ### 
"""
x = SYMBOL_LOOKUP['x']
f0 = 2
f1 = 2*x - 2
initial_tbc_segments = [CurveSegment(f0, 2), CurveSegment(f1, 1)]
pool = Pool(initial_tbc_segments)
tbc_segments, integrated_tbc_segments, amm_segments = pool.amm_curve
fig, ax = pool.plot()
"""