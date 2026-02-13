# 指数分析工具 - 集成版使用指南

## 功能特点

### 1. 统一HTML文件
所有分析报告和温度图集成在一个HTML文件中，无需打开多个文件。

### 2. 表格总览页面
- 显示所有指数的基本信息
- 支持搜索（按代码或名称）
- 分页显示（每页10条）
- 点击任意行查看详情

### 3. 详细分析页面
- 完整的指数分析报告
- 交互式温度计图表
- 十大权重股列表
- 近三年走势数据
- 相关产品信息链接

### 4. 导航功能
- 点击表格行跳转到详情
- "返回列表"按钮回到总览
- 页码导航浏览所有指数

## 使用方法

### 快速开始
```bash
python index_analyzer_unified.py
```

### 配置选项

#### 处理数量
在 `main()` 函数中修改：
```python
# 处理前10个指数
analyzer.process_all_indices(limit=10)

# 处理所有指数
analyzer.process_all_indices(limit=None)
```

#### 自定义路径
```python
analyzer = IndexAnalyzer(
    excel_path='data/指数列表.xlsx',
    output_dir='my_output'
)
```

## 输出文件

### 主文件
- `index_analysis_summary.html` - 包含所有指数的统一报告

### 文件大小
- 10个指数: ~263KB
- 100个指数: ~2-3MB（预估）
- 1000个指数: ~20-30MB（预估）

## 页面功能说明

### 总览页面
| 功能 | 说明 |
|------|------|
| 搜索框 | 输入代码或名称实时过滤 |
| 表格 | 展示指数基本信息 |
| 分页 | 每页10条，支持翻页 |
| 温度状态 | 彩色标签显示（低温/中温/高温）|

### 详情页面
| 功能 | 说明 |
|------|------|
| 温度计 | 交互式Plotly图表 |
| 统计卡片 | 显示最新价、最高、最低、平均 |
| 权重股表 | 十大权重股列表 |
| 走势表 | 近三年历史数据 |
| 返回按钮 | 回到总览页面 |

## 温度说明

| 百分位范围 | 状态 | 颜色 | 说明 |
|-----------|------|------|------|
| 0-30% | 低温 | 绿色 | 处于历史低位 |
| 30-70% | 中温 | 黄色 | 处于历史中位 |
| 70-100% | 高温 | 红色 | 处于历史高位 |

## 数据更新

### 更新数据
重新运行脚本即可更新：
```bash
python index_analyzer_unified.py
```

### 数据延迟
- 历史数据：可能有1-2天延迟
- 百分位计算：基于近三年历史数据
- 成份股：最新调整后的成份

## 浏览器兼容性

| 浏览器 | 版本要求 | 状态 |
|--------|---------|------|
| Chrome | 60+ | ✓ 完全支持 |
| Firefox | 60+ | ✓ 完全支持 |
| Safari | 12+ | ✓ 完全支持 |
| Edge | 79+ | ✓ 完全支持 |
| IE | 不支持 | ✗ 不支持 |

## 性能建议

### 大量指数（>100）
1. 增加分页大小
2. 考虑分批处理
3. 使用SSD存储

### 优化建议
```python
# 修改分页大小（在HTML模板中）
const rowsPerPage = 20;  # 默认10，可以改为20或更多
```

## 自定义样式

### 修改颜色
在HTML模板中找到CSS变量：
```css
/* 修改主题色 */
--primary-color: #667eea;
--secondary-color: #764ba2;
```

### 修改布局
调整网格布局：
```css
.stats-grid {{
    grid-template-columns: repeat(2, 1fr);  /* 改为2列 */
}}
```

## 常见问题

### Q: 文件太大？
A: 
1. 减少处理的指数数量
2. 删除历史数据（修改脚本）
3. 压缩HTML文件

### Q: 图表不显示？
A: 
1. 检查网络连接（需要加载Plotly CDN）
2. 使用现代浏览器
3. 查看浏览器控制台错误

### Q: 搜索不工作？
A: 
1. 确保JavaScript已启用
2. 检查浏览器控制台错误
3. 尝试刷新页面

### Q: 点击表格无反应？
A: 
1. 检查是否点击了可点击区域
2. 查看浏览器控制台错误
3. 确认详情页面已生成

## 技术实现

### 关键技术
- **数据获取**：多数据源备用（AKShare）
- **图表生成**：Plotly.js（通过CDN）
- **分页功能**：JavaScript实现
- **搜索功能**：实时过滤
- **响应式设计**：CSS Grid和Flexbox

### 文件结构
```
index_analysis_summary.html
├── CSS样式
│   ├── 主题样式
│   ├── 表格样式
│   ├── 卡片样式
│   └── 响应式样式
├── HTML结构
│   ├── 总览视图
│   ├── 详情视图
│   └── 导航控制
└── JavaScript
    ├── 数据存储
    ├── 分页逻辑
    ├── 搜索功能
    └── 页面切换
```

## 高级功能

### 自定义分页
修改 `rowsPerPage` 变量：
```javascript
const rowsPerPage = 15;  // 每页15条
```

### 导出功能
添加导出按钮：
```javascript
function exportData() {{
    const csv = indices.map(idx => 
        `${{idx.code}},${{idx.name}},${{idx.current_price}}`
    ).join('\\n');
    download(csv, 'indices.csv', 'text/csv');
}}
```

### 数据过滤
按温度状态过滤：
```javascript
function filterByTemperature(status) {{
    filteredIndices = indices.filter(idx => 
        idx.temperature_status === status
    );
    renderTable();
}}
```

## 项目结构

```
SummarizeETF/
├── data/
│   └── 指数列表.xlsx
├── output/
│   └── index_analysis_summary.html
├── index_analyzer_unified.py  # 主脚本
├── index_analyzer_fixed.py    # 修复版（分文件）
├── requirements.txt
└── UNIFIED_GUIDE.md           # 本文件
```

## 对比版本

| 功能 | 集成版 | 分文件版 |
|------|--------|---------|
| 文件数量 | 1个HTML | 多个HTML |
| 页面切换 | 即时切换 | 需要打开新页面 |
| 搜索功能 | 有 | 无 |
| 分页功能 | 有 | 无 |
| 文件大小 | 较大 | 较小 |
| 使用体验 | 更好 | 一般 |

## 总结

集成版的优势：
✓ 所有数据集中在一个文件
✓ 快速切换查看不同指数
✓ 搜索和分页功能
✓ 更好的用户体验
✓ 更易于分享

适合场景：
- 需要查看多个指数
- 需要对比不同指数
- 需要快速查找特定指数
- 需要分享给他人
