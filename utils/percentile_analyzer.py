"""
百分位分析模块
提供百分位计算和温度图生成功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class PercentileAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.low_threshold = config.get('percentile', {}).get('low', 30)
        self.high_threshold = config.get('percentile', {}).get('high', 70)
        self.colors = config.get('colors', {})

    def calculate_percentile(self, current_value: float, historical_values: List[float]) -> float:
        if not historical_values or len(historical_values) < 2:
            return 50.0

        historical = np.array(historical_values)
        below_count = np.sum(historical < current_value)
        percentile = (below_count / len(historical)) * 100

        return min(100, max(0, percentile))

    def get_percentile_category(self, percentile: float) -> str:
        if percentile < self.low_threshold:
            return 'low'
        elif percentile >= self.high_threshold:
            return 'high'
        else:
            return 'normal'

    def get_color_by_percentile(self, percentile: float) -> str:
        category = self.get_percentile_category(percentile)

        if category == 'low':
            return self.colors.get('low', '#4CAF50')
        elif category == 'high':
            return self.colors.get('high', '#F44336')
        else:
            return self.colors.get('medium', '#FFC107')

    def analyze_sector(self, sector_data: Dict) -> Dict:
        try:
            data = sector_data.get('data', pd.DataFrame())

            if data.empty or 'close' not in data.columns:
                return {
                    'name': sector_data.get('name'),
                    'percentile': 50.0,
                    'category': 'normal',
                    'color': self.colors.get('medium', '#FFC107'),
                    'status': '数据不足'
                }

            current_price = data['close'].iloc[-1]
            historical_prices = data['close'].tolist()

            percentile = self.calculate_percentile(current_price, historical_prices)
            category = self.get_percentile_category(percentile)
            color = self.get_color_by_percentile(percentile)

            stats = {
                'current_price': current_price,
                'high': data['high'].max() if 'high' in data.columns else current_price,
                'low': data['low'].min() if 'low' in data.columns else current_price,
                'mean': data['close'].mean(),
                'std': data['close'].std()
            }

            return {
                'name': sector_data.get('name'),
                'code': sector_data.get('code'),
                'percentile': round(percentile, 2),
                'category': category,
                'color': color,
                'stats': stats,
                'status': '正常'
            }

        except Exception as e:
            logger.error(f"分析板块 {sector_data.get('name')} 时出错: {e}")
            return {
                'name': sector_data.get('name'),
                'percentile': 50.0,
                'category': 'normal',
                'color': self.colors.get('medium', '#FFC107'),
                'status': f'错误: {str(e)}'
            }

    def generate_temperature_data(self, sector_data_list: List[Dict]) -> List[Dict]:
        temperature_data = []
        for sector_data in sector_data_list:
            analysis = self.analyze_sector(sector_data)
            temperature_data.append(analysis)
        return temperature_data

    def get_summary_statistics(self, sector_data_list: List[Dict]) -> Dict:
        temperature_data = self.generate_temperature_data(sector_data_list)

        total = len(temperature_data)
        low_count = sum(1 for d in temperature_data if d['category'] == 'low')
        normal_count = sum(1 for d in temperature_data if d['category'] == 'normal')
        high_count = sum(1 for d in temperature_data if d['category'] == 'high')

        avg_percentile = np.mean([d['percentile'] for d in temperature_data])

        return {
            'total_sectors': total,
            'low_valuation': low_count,
            'normal_valuation': normal_count,
            'high_valuation': high_count,
            'average_percentile': round(avg_percentile, 2),
            'low_percentage': round(low_count / total * 100, 2) if total > 0 else 0,
            'normal_percentage': round(normal_count / total * 100, 2) if total > 0 else 0,
            'high_percentage': round(high_count / total * 100, 2) if total > 0 else 0
        }
