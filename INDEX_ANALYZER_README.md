# 指数分析工具

这个工具用于分析中国股市指数，生成包含指数信息、权重股、相关产品和温度图的 HTML 报告。

## 功能特性

1. **自动读取指数列表**：从 Excel 文件中读取指数代码和名称
2. **获取指数历史数据**：获取近三年的指数历史数据
3. **计算百分位**：根据历史数据计算当前指数的百分位位置
4. **获取成份股信息**：获取指数的前十大权重股
5. **生成温度图**：使用 Plotly 生成交互式温度计图表
6. **生成 HTML 报告**：生成美观的 HTML 报告页面

## 依赖项

```bash
pip install pandas akshare numpy jinja2 plotly openpyxl
```

或使用项目的 requirements.txt：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```bash
python index_analyzer.py
```

这将处理 `data/指数列表.xlsx` 中的所有指数，并将生成的 HTML 报告保存到 `output/` 目录。

### 限制处理数量

如果你只想测试前几个指数，可以修改脚本中的 `limit` 参数：

```python
# 只处理前 5 个指数
analyzer.process_all_indices(limit=5)
```

### 作为模块使用

```python
from index_analyzer import IndexAnalyzer

# 创建分析器
analyzer = IndexAnalyzer(
    excel_path='data/指数列表.xlsx',
    output_dir='output'
)

# 处理单个指数
analyzer.process_index('000300', '沪深300')

# 处理所有指数
analyzer.process_all_indices()
```

## 输出文件

脚本会生成以下类型的文件：

1. **HTML 报告**：`{指数代码}_{指数名称}_report.html`
   - 包含指数基本信息
   - 十大权重股列表
   - 近三年指数走势数据
   - 当前百分位温度显示

2. **温度计图表**：`{指数名称}_{指数代码}_temperature.html`
   - 交互式 Plotly 温度计图表
   - 显示当前百分位位置

## 数据说明

### 数据来源

- **指数历史数据**：使用 AKShare 从东方财富获取
- **指数成份股**：使用 AKShare 获取
- **相关产品**：提供中证指数官网链接供查询

### 百分位计算

百分位是根据近三年所有交易日的收盘价计算得出：

- **低温 (0-30%)**：绿色，表示当前价格处于历史较低水平
- **中温 (30-70%)**：黄色，表示当前价格处于历史中等水平
- **高温 (70-100%)**：红色，表示当前价格处于历史较高水平

## 注意事项

1. **网络问题**：如果遇到网络连接问题，请检查：
   - 网络连接是否正常
   - 是否需要配置代理
   - 数据源网站是否可访问

2. **数据延迟**：指数数据可能有一天的延迟

3. **指数代码格式**：确保 Excel 文件中的指数代码格式正确（如 "000300"）

4. **依赖库更新**：定期更新 AKShare 以获取最新数据接口

## 故障排除

### 网络连接错误

如果遇到 "Unable to connect to proxy" 或类似的网络错误：

```python
# 可以尝试禁用代理
import os
os.environ['NO_PROXY'] = '*'

# 或者设置正确的代理
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'
```

### 数据获取失败

如果某些指数数据获取失败，可能原因：
- 指数代码不正确
- 该指数已停牌或退市
- 数据源暂无该指数数据

### 编码问题

Excel 文件如果遇到乱码，尝试用以下方式保存：
- 使用 UTF-8 编码
- 确保使用 Excel 2007+ 格式 (.xlsx)

## 项目结构

```
SummarizeETF/
├── data/
│   └── 指数列表.xlsx          # 指数数据源
├── output/                     # 输出目录
│   ├── 000300_沪深300_report.html
│   ├── 沪深300_000300_temperature.html
│   └── ...
├── index_analyzer.py           # 主脚本
├── requirements.txt           # 依赖列表
└── README.md                  # 本文件
```

## 扩展功能

你可以根据需要扩展脚本：

### 添加更多指标

```python
def calculate_custom_indicator(self, history_df):
    # 计算自定义指标
    pass
```

### 自定义 HTML 模板

修改 `generate_html_report` 方法中的模板字符串来自定义报告样式。

### 添加更多数据源

可以在 `get_index_history` 方法中添加备用数据源。

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，欢迎提出 Issue。
