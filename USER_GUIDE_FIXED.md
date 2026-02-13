# 指数分析工具 - 修复版使用指南

## 修复内容

### 问题
原始脚本遇到代理连接错误，无法获取数据。

### 解决方案

#### 1. 禁用代理
在脚本启动时禁用所有代理设置：
```python
os.environ['NO_PROXY'] = '*'
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
```

#### 2. 多数据源备用
实现了三个备用数据源：
- AKShare index_zh_a_hist（主要）
- AKShare stock_zh_index_daily_em（备用1）
- AKShare stock_zh_index_daily_sina（备用2）

#### 3. 智能重试
- 失败自动重试（最多3次）
- 自动切换到下一个数据源
- 连接超时处理

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行脚本
```bash
# 处理前5个指数（测试）
python index_analyzer_fixed.py

# 修改脚本中的limit参数处理更多指数
# limit=None 处理所有指数
```

### 3. 查看结果
在浏览器中打开 `output/` 目录中的HTML文件

## 文件说明

```
output/
├── 000300_沪深300_report.html          # 沪深300报告
├── 000300_沪深300_temperature.html     # 沪深300温度计
├── 000510_中证A500_report.html
├── 000510_中证A500_temperature.html
├── 000802_500沪市_report.html
├── 000802_500沪市_temperature.html
├── 000814_细分医药_report.html
├── 000814_细分医药_temperature.html
├── 000819_有色金属_report.html
└── 000819_有色金属_temperature.html
```

## 功能说明

### 百分位计算
根据近三年历史数据计算当前价格位置：
- **低温 (0-30%)**：绿色
- **中温 (30-70%)**：黄色
- **高温 (70-100%)**：红色

### 报告内容
- 指数基本信息
- 当前百分位温度显示
- 近三年统计（最高、最低、平均）
- 十大权重股列表
- 相关产品信息链接
- 近三年走势数据

## 自定义配置

### 修改处理数量
在 `main()` 函数中：
```python
# 处理前10个指数
analyzer.process_all_indices(limit=10)

# 处理所有指数
analyzer.process_all_indices(limit=None)
```

### 修改输出目录
```python
analyzer = IndexAnalyzer(
    excel_path='data/指数列表.xlsx',
    output_dir='my_reports'  # 自定义目录
)
```

## 网络要求

### 需要访问的网站
- www.csindex.com.cn
- quote.eastmoney.com
- finance.sina.com.cn

### 网络环境
- 不能使用代理
- 需要稳定的网络连接
- 建议使用国内网络

## 常见问题

### Q: 仍然获取数据失败？
A: 
1. 检查网络连接
2. 尝试使用不同的网络（如手机热点）
3. 检查是否被防火墙阻止

### Q: 数据不准确？
A: 
- 数据可能有1-2天延迟
- 历史数据可能不完整
- 建议核对多个数据源

### Q: HTML页面无法打开？
A: 
1. 检查文件是否完整生成
2. 使用现代浏览器（Chrome、Firefox等）
3. 检查文件编码

## 性能优化

### 提高处理速度
1. 减少处理数量
2. 增加数据源之间的延迟时间
3. 使用多线程处理（需要修改代码）

### 降低网络请求
1. 实现数据缓存
2. 减少重试次数
3. 使用本地数据备份

## 扩展功能

可以添加的功能：
1. 数据自动更新
2. 邮件/消息通知
3. 更多可视化图表
4. 数据导出（Excel、CSV）
5. 自定义报告模板

## 技术支持

如遇问题：
1. 查看控制台输出的详细错误信息
2. 检查FIX_DOCUMENTATION.md了解修复详情
3. 确认网络连接正常
4. 验证依赖包版本
