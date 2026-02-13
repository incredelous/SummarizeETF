# 快速开始

## 1. 安装依赖
```bash
pip install -r requirements.txt
```

## 2. 准备数据
确保 `data/指数列表.xlsx` 文件存在，包含指数代码和名称

## 3. 运行脚本
```bash
# 推荐使用集成版（单HTML文件+分页+搜索）
python index_analyzer_unified.py
```

## 4. 查看结果
打开生成的文件：
```
output/index_analysis_summary.html
```

## 功能特点

✅ **统一HTML文件** - 所有指数在一个文件中
✅ **表格分页** - 每页10条，支持翻页
✅ **实时搜索** - 按代码或名称过滤
✅ **点击详情** - 点击表格行查看完整报告
✅ **温度计** - 交互式Plotly图表
✅ **网络优化** - 多数据源自动切换

## 脚本版本对比

| 版本 | 文件 | 输出 | 特点 |
|------|------|------|------|
| 集成版 | index_analyzer_unified.py | 1个HTML文件 | 推荐！分页+搜索 |
| 修复版 | index_analyzer_fixed.py | 多个HTML文件 | 网络问题已修复 |
| 原始版 | index_analyzer.py | 多个HTML文件 | 基础功能 |

## 配置选项

### 修改处理数量
编辑 `index_analyzer_unified.py`：
```python
# 处理前10个指数
analyzer.process_all_indices(limit=10)

# 处理所有指数
analyzer.process_all_indices(limit=None)
```

### 自定义输出目录
```python
analyzer = IndexAnalyzer(
    excel_path='data/指数列表.xlsx',
    output_dir='my_output'
)
```

## 温度说明

| 百分位 | 状态 | 颜色 | 含义 |
|--------|------|------|------|
| 0-30% | 低温 | 绿色 | 历史低位 |
| 30-70% | 中温 | 黄色 | 历史中位 |
| 70-100% | 高温 | 红色 | 历史高位 |

## 页面操作

### 总览页面
- 搜索：输入代码或名称实时过滤
- 翻页：点击"上一页"/"下一页"
- 查看详情：点击任意表格行

### 详情页面
- 返回列表：点击"← 返回列表"
- 查看图表：温度计自动显示
- 浏览数据：滚动查看所有信息

## 文档

| 文档 | 内容 |
|------|------|
| PROJECT_SUMMARY.md | 完整项目总结 |
| UNIFIED_GUIDE.md | 集成版详细指南 |
| FIX_DOCUMENTATION.md | 网络问题修复说明 |

## 常见问题

**Q: 网络连接失败？**
A: 脚本已自动修复网络问题，如仍有问题请检查网络连接

**Q: 文件太大？**
A: 减少 `limit` 参数处理较少的指数

**Q: 搜索不工作？**
A: 确保JavaScript已启用，使用现代浏览器

**Q: 图表不显示？**
A: 需要网络连接加载Plotly CDN

## 系统要求

- Python 3.7+
- 现代浏览器（Chrome 60+, Firefox 60+, Safari 12+）
- 稳定的网络连接
- 不能使用代理

## 项目结构

```
SummarizeETF/
├── data/
│   └── 指数列表.xlsx
├── output/
│   └── index_analysis_summary.html
├── index_analyzer_unified.py  ← 使用这个
├── requirements.txt
└── README_START.md  ← 本文件
```

## 下一步

1. ✅ 运行脚本生成报告
2. ✅ 在浏览器中打开HTML文件
3. ✅ 使用搜索和分页功能
4. ✅ 点击查看指数详情
5. ✅ 查看温度计和统计数据

---

**推荐使用**: `index_analyzer_unified.py`
