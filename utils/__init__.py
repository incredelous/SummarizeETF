"""
A股板块分析器工具包
"""

from .data_fetcher import DataFetcher, calculate_percentile, get_color_by_percentile
from .percentile_analyzer import PercentileAnalyzer
from .html_generator import HTMLGenerator

__all__ = [
    'DataFetcher',
    'calculate_percentile',
    'get_color_by_percentile',
    'PercentileAnalyzer',
    'HTMLGenerator'
]
