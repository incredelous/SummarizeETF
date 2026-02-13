import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import numpy as np
from jinja2 import Template
import plotly.graph_objects as go
import os
import time
import warnings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

warnings.filterwarnings('ignore')

# 禁用代理
os.environ['NO_PROXY'] = '*'
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

class CSIndexAPI:
    """中证指数官网API封装类"""
    
    def __init__(self):
        self.base_url = "https://www.csindex.com.cn"
        self.session = self._create_session()
    
    def _create_session(self):
        """创建带有重试机制的会话"""
        session = requests.Session()
        
        # 重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 禁用SSL验证
        session.verify = False
        
        return session
    
    def get_index_history(self, index_code):
        """获取指数历史数据 - 使用AKShare备用方案"""
        try:
            print(f"  正在获取指数 {index_code} 的历史数据...")
            
            # 尝试使用不同的数据源
            data_sources = [
                self._get_from_akshare,
                self._get_from_eastmoney,
                self._get_from_sina
            ]
            
            for data_source in data_sources:
                try:
                    df = data_source(index_code)
                    if df is not None and not df.empty:
                        print(f"  成功获取 {len(df)} 条历史数据")
                        return df
                except Exception as e:
                    print(f"  数据源失败: {e}")
                    continue
            
            print(f"  所有数据源都失败了")
            return None
            
        except Exception as e:
            print(f"  获取历史数据异常: {e}")
            return None
    
    def _get_from_akshare(self, index_code):
        """从AKShare获取数据"""
        print("  尝试 AKShare 数据源...")
        
        # 方法1: index_zh_a_hist
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*3)
            
            df = ak.index_zh_a_hist(
                symbol=index_code,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d")
            )
            
            if df is not None and not df.empty:
                df = df.sort_values('日期')
                return df
        except Exception as e:
            print(f"  index_zh_a_hist 失败: {e}")
        
        # 方法2: stock_zh_index_daily_em
        try:
            df = ak.stock_zh_index_daily_em(
                symbol=f"csi{index_code}",
                start_date="20200201",
                end_date="20250101"
            )
            
            if df is not None and not df.empty:
                df = df.sort_values('date')
                # 重命名列以匹配预期格式
                if 'date' in df.columns:
                    df = df.rename(columns={'date': '日期'})
                if 'close' in df.columns:
                    df = df.rename(columns={'close': '收盘'})
                
                # 只保留近三年的数据
                recent_date = datetime.now() - timedelta(days=365*3)
                df['日期'] = pd.to_datetime(df['日期'])
                df = df[df['日期'] >= recent_date]
                
                return df
        except Exception as e:
            print(f"  stock_zh_index_daily_em 失败: {e}")
        
        return None
    
    def _get_from_eastmoney(self, index_code):
        """从东方财富获取数据"""
        print("  尝试东方财富数据源...")
        try:
            df = ak.stock_zh_index_daily_em(
                symbol=f"000{index_code}",
                start_date="20200201",
                end_date="20250101"
            )
            
            if df is not None and not df.empty:
                df = df.sort_values('date')
                # 重命名列
                df = df.rename(columns={
                    'date': '日期',
                    'close': '收盘',
                    'high': '最高',
                    'low': '最低',
                    'open': '开盘'
                })
                
                # 只保留近三年的数据
                recent_date = datetime.now() - timedelta(days=365*3)
                df['日期'] = pd.to_datetime(df['日期'])
                df = df[df['日期'] >= recent_date]
                
                return df
        except Exception as e:
            print(f"  东方财富数据源失败: {e}")
        
        return None
    
    def _get_from_sina(self, index_code):
        """从新浪获取数据"""
        print("  尝试新浪数据源...")
        try:
            # 中证指数在新浪上的格式是 sh000xxx
            symbol = f"sh{index_code}"
            df = ak.stock_zh_index_daily(symbol=symbol)
            
            if df is not None and not df.empty:
                df = df.sort_values('date')
                # 重命名列
                df = df.rename(columns={
                    'date': '日期',
                    'close': '收盘',
                    'high': '最高',
                    'low': '最低',
                    'open': '开盘'
                })
                
                return df
        except Exception as e:
            print(f"  新浪数据源失败: {e}")
        
        return None
    
    def get_index_components(self, index_code):
        """获取指数成份股"""
        try:
            print(f"  正在获取指数 {index_code} 的成份股...")
            
            # 方法1: index_stock_cons
            try:
                df = ak.index_stock_cons(symbol=index_code)
                if df is not None and not df.empty:
                    print(f"  成功获取 {len(df)} 只成份股")
                    return df
            except Exception as e:
                print(f"  index_stock_cons 失败: {e}")
            
            # 方法2: index_stock_cons_sina
            try:
                df = ak.index_stock_cons_sina(symbol=index_code)
                if df is not None and not df.empty:
                    print(f"  成功获取 {len(df)} 只成份股 (sina)")
                    return df
            except Exception as e:
                print(f"  index_stock_cons_sina 失败: {e}")
            
            print(f"  无法获取成份股数据")
            return None
            
        except Exception as e:
            print(f"  获取成份股异常: {e}")
            return None
    
    def test_connection(self):
        """测试连接"""
        test_urls = [
            "https://www.baidu.com",
            "https://www.csindex.com.cn",
            "https://quote.eastmoney.com"
        ]
        
        print("测试网络连接...")
        for url in test_urls:
            try:
                response = self.session.get(url, timeout=10)
                print(f"  {url}: {response.status_code}")
            except Exception as e:
                print(f"  {url}: 失败 - {e}")


class IndexAnalyzer:
    def __init__(self, excel_path='data/指数列表.xlsx', output_dir='output'):
        self.excel_path = excel_path
        self.output_dir = output_dir
        self.api = CSIndexAPI()
        os.makedirs(output_dir, exist_ok=True)
    
    def read_index_codes(self):
        """读取 Excel 文件中的指数代码和名称"""
        try:
            df = pd.read_excel(self.excel_path)
            if df.empty:
                print("Excel 文件为空")
                return []
            
            index_codes = df.iloc[:, 0].tolist()
            index_names = df.iloc[:, 1].tolist() if len(df.columns) > 1 else [f"指数{code}" for code in index_codes]
            
            indices = []
            for code, name in zip(index_codes, index_names):
                if pd.notna(code):
                    indices.append((str(code).strip(), str(name).strip() if pd.notna(name) else f"指数{code}"))
            
            return indices
        except FileNotFoundError:
            print(f"找不到文件: {self.excel_path}")
            return []
        except Exception as e:
            print(f"读取 Excel 文件失败: {e}")
            return []
    
    def calculate_percentile(self, current_value, history_values):
        """计算当前值在历史数据中的百分位"""
        sorted_values = np.sort(history_values)
        rank = np.searchsorted(sorted_values, current_value)
        percentile = (rank / len(sorted_values)) * 100
        return percentile
    
    def get_temperature_color(self, percentile):
        """根据百分位返回颜色"""
        if percentile < 30:
            return '#4CAF50'
        elif percentile < 70:
            return '#FFC107'
        else:
            return '#F44336'
    
    def create_temperature_gauge(self, percentile, index_name, index_code):
        """创建温度计图表"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=percentile,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{index_name} 温度计"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': self.get_temperature_color(percentile)},
                'steps': [
                    {'range': [0, 30], 'color': "#d4edda"},
                    {'range': [30, 70], 'color': "#fff3cd"},
                    {'range': [70, 100], 'color': "#f8d7da"},
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
            title=f"{index_name} ({index_code}) 当前百分位: {percentile:.1f}%",
            annotations=[{
                'text': '低温 | 中温 | 高温',
                'x': 0.5,
                'y': 0.1,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 12, 'color': '#666'}
            }]
        )
        
        html_path = os.path.join(self.output_dir, f"{index_code}_{index_name}_temperature.html")
        fig.write_html(html_path)
        return html_path
    
    def generate_html_report(self):
        """生成 HTML 报告模板"""
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ index_name }} 指数分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 28px;
        }
        h2 {
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 22px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        .info-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 5px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #e0e0e0;
            padding: 12px 15px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 14px;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #e9ecef;
        }
        .temperature-display {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #4CAF50, #FFC107, #F44336);
            border-radius: 10px;
            color: white;
            font-size: 36px;
            font-weight: bold;
            margin: 30px 0;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card h3 {
            margin: 0 0 15px 0;
            color: rgba(255,255,255,0.9);
            font-size: 14px;
            font-weight: 500;
        }
        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
            color: white;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .chart-container {
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
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
        
        {% if top_stocks %}
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
        {% else %}
        <div class="info-section">
            <p>暂无成份股数据</p>
        </div>
        {% endif %}
        
        <h2>相关产品信息</h2>
        <div class="info-section">
            <p>该指数的相关ETF产品可以通过以下方式查询：</p>
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li style="margin-bottom: 8px;"><strong>中证指数官网：</strong> <a href="https://www.csindex.com.cn/#/indices/family/detail?indexCode={{ index_code }}" target="_blank">点击访问</a></li>
                <li style="margin-bottom: 8px;"><strong>东方财富：</strong> 在东方财富网搜索指数代码</li>
                <li><strong>各大券商APP：</strong> 搜索指数代码查看相关产品</li>
            </ul>
        </div>
        
        {% if recent_data %}
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
        {% else %}
        <div class="info-section">
            <p>暂无历史数据</p>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>数据生成时间: {{ generate_time }}</p>
            <p>数据来源: AKShare (多数据源)</p>
            <p>注: 数据仅供参考，不构成投资建议</p>
        </div>
    </div>
    
    <script>
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
        """处理单个指数"""
        print(f"正在处理指数: {index_name} ({index_code})")
        
        # 获取历史数据
        history_df = self.api.get_index_history(index_code)
        
        if history_df is None or history_df.empty:
            print(f"无法获取指数 {index_code} 的历史数据")
            return None
        
        # 获取成份股
        components_df = self.api.get_index_components(index_code)
        
        # 计算统计信息
        if '收盘' in history_df.columns:
            current_price = float(history_df.iloc[-1]['收盘'])
            three_year_high = float(history_df['收盘'].max())
            three_year_low = float(history_df['收盘'].min())
            three_year_avg = float(history_df['收盘'].mean())
            
            percentile = self.calculate_percentile(current_price, history_df['收盘'].values)
            temperature_color = self.get_temperature_color(percentile)
        else:
            print(f"历史数据中没有'收盘'列")
            return None
        
        # 创建温度计图表
        temp_chart_path = self.create_temperature_gauge(percentile, index_name, index_code)
        temp_chart_name = os.path.basename(temp_chart_path)
        
        # 获取前十成份股
        top_stocks = []
        if components_df is not None and not components_df.empty:
            components_df = components_df.head(10)
            for idx, row in components_df.iterrows():
                stock_code = str(row[0]) if len(row) > 0 else "N/A"
                stock_name = str(row[1]) if len(row) > 1 else "N/A"
                top_stocks.append((stock_code, stock_name))
        
        # 获取最近的数据
        recent_data = []
        if '日期' in history_df.columns and '收盘' in history_df.columns:
            recent_df = history_df.tail(10)[['日期', '收盘']]
            if '涨跌幅' in history_df.columns:
                recent_df = history_df.tail(10)[['日期', '收盘', '涨跌幅']]
                recent_data = [
                    [str(row[0]), f"{row[1]:.2f}", f"{row[2]:.2f}" if pd.notna(row[2]) else "N/A"]
                    for _, row in recent_df.iterrows()
                ]
            else:
                recent_data = [
                    [str(row[0]), f"{row[1]:.2f}", "N/A"]
                    for _, row in recent_df.iterrows()
                ]
        
        # 生成 HTML 报告
        template = Template(self.generate_html_report())
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
            recent_data=recent_data,
            generate_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        output_path = os.path.join(self.output_dir, f"{index_code}_{index_name}_report.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已生成报告: {output_path}")
        return output_path
    
    def process_all_indices(self, limit=None):
        """处理所有指数"""
        indices = self.read_index_codes()
        
        if not indices:
            print("没有找到有效的指数数据")
            return
        
        print(f"共找到 {len(indices)} 个指数")
        
        if limit:
            indices = indices[:limit]
            print(f"限制处理前 {limit} 个指数")
        
        # 测试网络连接
        self.api.test_connection()
        
        success_count = 0
        fail_count = 0
        
        for index_code, index_name in indices:
            try:
                result = self.process_index(index_code, index_name)
                if result:
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(2)
            except Exception as e:
                print(f"处理指数 {index_name} ({index_code}) 时出错: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
                continue
        
        print(f"\n处理完成！")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"报告已保存在 {self.output_dir} 目录中")

def main():
    print("=" * 60)
    print("指数分析工具 (修复版)")
    print("=" * 60)
    
    analyzer = IndexAnalyzer()
    
    print("\n开始处理指数数据...")
    print("限制处理前 5 个指数进行测试")
    analyzer.process_all_indices(limit=5)
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
