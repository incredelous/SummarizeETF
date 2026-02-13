import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import numpy as np
from jinja2 import Template
import plotly.graph_objects as go
import os
import time

class IndexAnalyzer:
    def __init__(self, excel_path='data/指数列表.xlsx', output_dir='output'):
        self.excel_path = excel_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def read_index_codes(self):
        df = pd.read_excel(self.excel_path)
        index_codes = df.iloc[:, 0].tolist()
        index_names = df.iloc[:, 1].tolist()
        return list(zip(index_codes, index_names))
    
    def get_index_history(self, index_code):
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*3)
            
            hist_df = ak.index_zh_a_hist(
                symbol=index_code,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d")
            )
            return hist_df
        except Exception as e:
            print(f"获取指数 {index_code} 历史数据失败: {e}")
            return None
    
    def get_index_components(self, index_code):
        try:
            components_df = ak.index_stock_cons(symbol=index_code)
            return components_df
        except Exception as e:
            print(f"获取指数 {index_code} 成份股失败: {e}")
            return None
    
    def calculate_percentile(self, current_value, history_values):
        sorted_values = np.sort(history_values)
        rank = np.searchsorted(sorted_values, current_value)
        percentile = (rank / len(sorted_values)) * 100
        return percentile
    
    def get_temperature_color(self, percentile):
        if percentile < 30:
            return '#4CAF50'
        elif percentile < 70:
            return '#FFC107'
        else:
            return '#F44336'
    
    def create_temperature_gauge(self, percentile, index_name):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = percentile,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{index_name} 温度计"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self.get_temperature_color(percentile)},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "lightgray"},
                    {'range': [70, 100], 'color': "lightgray"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            title=f"{index_name} 当前百分位: {percentile:.1f}%",
            annotations=[{
                'text': '低温 | 中温 | 高温',
                'x': 0.5,
                'y': 0.1,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 12}
            }]
        )
        
        html_path = os.path.join(self.output_dir, f"{index_name}_temperature.html")
        fig.write_html(html_path)
        return html_path
    
    def generate_html_report(self, index_data):
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ index_name }} 指数分析报告</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        h2 {
            color: #666;
            margin-top: 30px;
        }
        .info-section {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .temperature-display {
            text-align: center;
            padding: 20px;
            background: linear-gradient(to right, #4CAF50, #FFC107, #F44336);
            border-radius: 10px;
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }
        .stat-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ index_name }} ({{ index_code }}) 指数分析报告</h1>
        
        <div class="temperature-display" style="background-color: {{ temperature_color }}">
            当前百分位: {{ percentile }}%
        </div>
        
        <div class="stat-grid">
            <div class="stat-card">
                <h3>最新收盘价</h3>
                <div class="value">{{ current_price }}</div>
            </div>
            <div class="stat-card">
                <h3>近三年最高</h3>
                <div class="value">{{ three_year_high }}</div>
            </div>
            <div class="stat-card">
                <h3>近三年最低</h3>
                <div class="value">{{ three_year_low }}</div>
            </div>
            <div class="stat-card">
                <h3>近三年平均</h3>
                <div class="value">{{ three_year_avg }}</div>
            </div>
        </div>
        
        <h2>十大权重股</h2>
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>股票代码</th>
                    <th>股票名称</th>
                </tr>
            </thead>
            <tbody>
                {% for stock in top_stocks %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ stock[0] }}</td>
                    <td>{{ stock[1] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h2>相关产品信息</h2>
        <div class="info-section">
            <p>该指数的相关ETF产品可以通过中证指数官网查询。</p>
            <p>详情请访问: <a href="https://www.csindex.com.cn/#/indices/family/detail?indexCode={{ index_code }}" target="_blank">中证指数官网</a></p>
        </div>
        
        <h2>近三年指数走势</h2>
        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>收盘价</th>
                    <th>涨跌幅(%)</th>
                </tr>
            </thead>
            <tbody>
                {% for row in recent_data %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[2] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <script>
        // 嵌入温度计图表
        var iframe = document.createElement('iframe');
        iframe.src = '{{ temperature_chart }}';
        iframe.style.width = '100%';
        iframe.style.height = '450px';
        iframe.style.border = 'none';
        
        var chartContainer = document.createElement('div');
        chartContainer.style.margin = '30px 0';
        chartContainer.appendChild(iframe);
        document.querySelector('.container').insertBefore(chartContainer, document.querySelectorAll('h2')[0]);
    </script>
</body>
</html>
        """
        
        return template_str
    
    def process_index(self, index_code, index_name):
        print(f"正在处理指数: {index_name} ({index_code})")
        
        history_df = self.get_index_history(index_code)
        if history_df is None or history_df.empty:
            print(f"无法获取指数 {index_code} 的历史数据")
            return None
        
        components_df = self.get_index_components(index_code)
        
        current_price = float(history_df.iloc[-1]['收盘'])
        three_year_high = float(history_df['收盘'].max())
        three_year_low = float(history_df['收盘'].min())
        three_year_avg = float(history_df['收盘'].mean())
        
        percentile = self.calculate_percentile(current_price, history_df['收盘'].values)
        temperature_color = self.get_temperature_color(percentile)
        
        temp_chart_path = self.create_temperature_gauge(percentile, f"{index_name}_{index_code}")
        temp_chart_name = os.path.basename(temp_chart_path)
        
        top_stocks = []
        if components_df is not None and not components_df.empty:
            top_stocks = [(row[0], row[1]) for _, row in components_df.head(10).iterrows()]
        
        recent_data = history_df.tail(10)[['日期', '收盘', '涨跌幅']].values.tolist()
        
        template = Template(self.generate_html_report({}))
        html_content = template.render(
            index_name=index_name,
            index_code=index_code,
            percentile=f"{percentile:.1f}",
            temperature_color=temperature_color,
            current_price=f"{current_price:.2f}",
            three_year_high=f"{three_year_high:.2f}",
            three_year_low=f"{three_year_low:.2f}",
            three_year_avg=f"{three_year_avg:.2f}",
            top_stocks=top_stocks,
            temperature_chart=temp_chart_name,
            recent_data=[[str(row[0]), f"{row[1]:.2f}", f"{row[2]:.2f}" if pd.notna(row[2]) else "N/A"] for row in recent_data]
        )
        
        output_path = os.path.join(self.output_dir, f"{index_code}_{index_name}_report.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已生成报告: {output_path}")
        return output_path
    
    def process_all_indices(self, limit=None):
        index_codes = self.read_index_codes()
        
        if limit:
            index_codes = index_codes[:limit]
        
        for index_code, index_name in index_codes:
            try:
                self.process_index(index_code, index_name)
                time.sleep(1)
            except Exception as e:
                print(f"处理指数 {index_name} ({index_code}) 时出错: {e}")
                continue

def main():
    analyzer = IndexAnalyzer()
    
    print("开始处理指数数据...")
    analyzer.process_all_indices(limit=5)
    
    print("处理完成！")
    print(f"报告已保存在 {analyzer.output_dir} 目录中")

if __name__ == "__main__":
    main()
