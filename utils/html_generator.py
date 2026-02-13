"""
HTML报告生成模块
生成A股板块分析的可视化HTML报告
"""

import os
from datetime import datetime
from typing import Dict, List
from jinja2 import Template
import json


class HTMLGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = config.get('output', {}).get('output_dir', './output')
        self.colors = config.get('colors', {})
        self.percentile_config = config.get('percentile', {})

        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, sector_data: List[Dict], output_filename: str = None) -> str:
        if output_filename is None:
            output_filename = f"a_stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        output_path = os.path.join(self.output_dir, output_filename)
        report_data = self._prepare_report_data(sector_data)
        html_content = self._render_html(report_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _prepare_report_data(self, sector_data: List[Dict]) -> Dict:
        report = {
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sectors': []
        }

        for sector in sector_data:
            sector_info = {
                'name': sector.get('name', '未知板块'),
                'code': sector.get('code', ''),
                'current_price': sector.get('current_price', 0),
                'high': sector.get('high', 0),
                'low': sector.get('low', 0),
                'mean': sector.get('mean', 0),
                'percentile': self._calculate_sector_percentile(sector),
                'etfs': []
            }

            for etf in sector.get('etfs', []):
                etf_info = {
                    'code': etf.get('code', ''),
                    'name': etf.get('name', ''),
                    'price': etf.get('price', 0),
                    'change': etf.get('change', 0),
                    'pe': etf.get('pe'),
                    'pb': etf.get('pb'),
                    'holdings': etf.get('holdings', [])
                }
                sector_info['etfs'].append(etf_info)

            report['sectors'].append(sector_info)

        return report

    def _calculate_sector_percentile(self, sector: Dict) -> float:
        try:
            data = sector.get('data')
            if data is None or (isinstance(data, dict) and not data):
                return 50.0
            
            import pandas as pd
            
            if isinstance(data, pd.DataFrame):
                if 'close' not in data.columns or data.empty:
                    return 50.0
                close_data = data['close'].dropna().tolist()
            elif isinstance(data, dict):
                close_data = data.get('close', [])
            else:
                return 50.0
            
            if not close_data or len(close_data) < 2:
                return 50.0
            
            current = float(close_data[-1])
            below_count = sum(1 for price in close_data if float(price) < current)
            percentile = (below_count / len(close_data)) * 100 if close_data else 50.0
            
            return round(percentile, 2)
        except Exception as e:
            return 50.0

    def _get_color_by_percentile(self, percentile: float) -> str:
        low = self.percentile_config.get('low', 30)
        high = self.percentile_config.get('high', 70)

        if percentile < low:
            return self.colors.get('low', '#4CAF50')
        elif percentile > high:
            return self.colors.get('high', '#F44336')
        else:
            return self.colors.get('medium', '#FFC107')

    def _render_html(self, report_data: Dict) -> str:
        template = self._get_html_template()
        return template.render(
            report=report_data,
            colors=self.colors,
            percentile_config=self.percentile_config,
            get_color_by_percentile=self._get_color_by_percentile,
            format_number=self._format_number
        )

    def _format_number(self, num: float, decimals: int = 2) -> str:
        if num is None:
            return '-'
        return f"{num:.{decimals}f}" if isinstance(num, float) else str(num)

    def _get_html_template(self) -> Template:
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A股板块分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background-color: {{ colors.background }};
            color: {{ colors.text }};
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .legend-color {
            width: 30px;
            height: 30px;
            border-radius: 5px;
        }

        .section {
            margin-bottom: 40px;
        }

        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .sector-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .sector-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .sector-header {
            padding: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        }

        .sector-name {
            font-size: 1.6em;
            font-weight: bold;
        }

        .sector-code {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.9em;
        }

        .sector-stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .stat-box {
            padding: 15px 25px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            text-align: center;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 1.4em;
            font-weight: bold;
        }

        .percentile-indicator {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }

        .percentile-value {
            font-size: 2em;
        }

        .percentile-label {
            font-size: 0.8em;
        }

        .etf-section {
            padding: 25px;
        }

        .etf-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }

        .etf-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }

        .etf-card:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .etf-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .etf-name {
            font-size: 1.3em;
            font-weight: bold;
        }

        .etf-code {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.9em;
        }

        .etf-price-info {
            display: flex;
            gap: 30px;
            margin-bottom: 15px;
        }

        .price-box {
            text-align: center;
        }

        .price-label {
            font-size: 0.85em;
            opacity: 0.7;
            margin-bottom: 3px;
        }

        .price-value {
            font-size: 1.2em;
            font-weight: bold;
        }

        .valuation-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }

        .valuation-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }

        .holdings-section {
            margin-top: 15px;
        }

        .holdings-title {
            font-size: 1em;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .holdings-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }

        .holding-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }

        .holding-name {
            font-size: 0.9em;
            margin-bottom: 3px;
        }

        .holding-code {
            font-size: 0.75em;
            color: rgba(255, 255, 255, 0.6);
        }

        .holding-proportion {
            font-size: 0.85em;
            color: #667eea;
            margin-top: 3px;
        }

        .temperature-bar {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }

        .temperature-bar-title {
            margin-bottom: 10px;
            font-size: 0.9em;
        }

        .temperature-track {
            height: 25px;
            background: linear-gradient(to right,
                {{ colors.low }} 0%,
                {{ colors.low }} 30%,
                {{ colors.medium }} 30%,
                {{ colors.medium }} 70%,
                {{ colors.high }} 70%,
                {{ colors.high }} 100%);
            border-radius: 12px;
            position: relative;
        }

        .temperature-marker {
            position: absolute;
            top: -5px;
            width: 4px;
            height: 35px;
            background: white;
            border-radius: 2px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
        }

        .temperature-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            font-size: 0.8em;
            opacity: 0.7;
        }

        .summary-section {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
            padding: 30px;
            border-radius: 15px;
            margin-top: 40px;
        }

        .summary-title {
            font-size: 1.5em;
            margin-bottom: 20px;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .summary-item {
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }

        .summary-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .summary-label {
            opacity: 0.8;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .sector-card {
            animation: fadeIn 0.5s ease forwards;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 A股板块指数分析报告</h1>
            <div class="subtitle">生成时间: {{ report.generated_time }}</div>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: {{ colors.low }};"></div>
                <span>低估值 (< {{ percentile_config.low }}%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: {{ colors.medium }};"></div>
                <span>正常 ({{ percentile_config.low }}%-{{ percentile_config.high }}%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: {{ colors.high }};"></div>
                <span>高估值 (> {{ percentile_config.high }}%)</span>
            </div>
        </div>

        {% for sector in report.sectors %}
        <div class="sector-card">
            <div class="sector-header">
                <div>
                    <div class="sector-name">{{ sector.name }}</div>
                    <div class="sector-code">{{ sector.code }}</div>
                </div>
                <div class="sector-stats">
                    <div class="stat-box">
                        <div class="stat-label">当前价格</div>
                        <div class="stat-value">{{ format_number(sector.current_price) }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">历史最高</div>
                        <div class="stat-value">{{ format_number(sector.high) }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">历史最低</div>
                        <div class="stat-value">{{ format_number(sector.low) }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">平均价格</div>
                        <div class="stat-value">{{ format_number(sector.mean) }}</div>
                    </div>
                    <div class="percentile-indicator" style="background: {{ get_color_by_percentile(sector.percentile) }};">
                        <div class="percentile-value">{{ "%.1f"|format(sector.percentile) }}%</div>
                        <div class="percentile-label">百分位</div>
                    </div>
                </div>
            </div>

            <div class="temperature-bar">
                <div class="temperature-bar-title">📈 百分位温度图</div>
                <div class="temperature-track">
                    <div class="temperature-marker" style="left: {{ sector.percentile }}%;"></div>
                </div>
                <div class="temperature-labels">
                    <span>0%</span>
                    <span>{{ percentile_config.low }}%</span>
                    <span>{{ percentile_config.high }}%</span>
                    <span>100%</span>
                </div>
            </div>

            {% if sector.etfs %}
            <div class="etf-section">
                <h3 class="etf-title">🏦 相关ETF</h3>
                <div class="etf-grid">
                    {% for etf in sector.etfs %}
                    <div class="etf-card">
                        <div class="etf-header">
                            <div>
                                <div class="etf-name">{{ etf.name }}</div>
                                <div class="etf-code">{{ etf.code }}</div>
                            </div>
                        </div>

                        <div class="etf-price-info">
                            <div class="price-box">
                                <div class="price-label">当前价格</div>
                                <div class="price-value">{{ format_number(etf.price) }}</div>
                            </div>
                            <div class="price-box">
                                <div class="price-label">涨跌幅</div>
                                <div class="price-value" style="color: {% if etf.change >= 0 %}#4CAF50{% else %}#F44336{% endif %};">
                                    {{ format_number(etf.change) }}
                                </div>
                            </div>
                        </div>

                        {% if etf.pe or etf.pb %}
                        <div class="valuation-grid">
                            {% if etf.pe %}
                            <div class="valuation-item">
                                <div class="price-label">PE</div>
                                <div class="price-value">{{ format_number(etf.pe) }}</div>
                            </div>
                            {% endif %}
                            {% if etf.pb %}
                            <div class="valuation-item">
                                <div class="price-label">PB</div>
                                <div class="price-value">{{ format_number(etf.pb) }}</div>
                            </div>
                            {% endif %}
                        </div>
                        {% endif %}

                        {% if etf.holdings %}
                        <div class="holdings-section">
                            <div class="holdings-title">🎯 Top10 持仓股</div>
                            <div class="holdings-list">
                                {% for holding in etf.holdings[:10] %}
                                <div class="holding-item">
                                    <div class="holding-name">{{ holding.name }}</div>
                                    <div class="holding-code">{{ holding.code }}</div>
                                    <div class="holding-proportion">{{ format_number(holding.proportion, 2) }}%</div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""
        return Template(template_str)
