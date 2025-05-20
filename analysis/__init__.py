"""
Analyse-Modul für den Crypto Trading Bot V2.

Dieses Modul enthält Funktionen zur Analyse und Visualisierung
von Backtest-Ergebnissen.
"""

from .data_loader import load_backtest_results
from .visualizations import (
    create_equity_curve_plot,
    create_drawdown_plot,
    create_monthly_breakdown_plot,
    create_trade_analysis_plots
)
from .statistics import (
    calculate_drawdown_statistics,
    calculate_monthly_returns,
    calculate_trade_statistics,
    create_performance_metrics
)
from .reporting import (
    save_reports,
    print_summary
)

__all__ = [
    'load_backtest_results',
    'create_equity_curve_plot',
    'create_drawdown_plot',
    'create_monthly_breakdown_plot',
    'create_trade_analysis_plots',
    'calculate_drawdown_statistics',
    'calculate_monthly_returns',
    'calculate_trade_statistics',
    'create_performance_metrics',
    'save_reports',
    'print_summary'
]
