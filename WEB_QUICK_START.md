# SummarizeETF Web 快速启动

## 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

## 2. 初始化并刷新数据（兼容旧命令）

```bash
python index_analyzer_unified.py
```

或直接运行：

```bash
python backend/scripts/refresh_data.py
```

## 3. 启动后端 API

```bash
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

## 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 5. 打开页面

- 前端: `http://127.0.0.1:5173`
- 后端健康检查: `http://127.0.0.1:8000/health`

## 页面说明

- `/` 指数表格：搜索、排序、分页、温度筛选、手动刷新
- `/indices/:code` 指数详情：1月/3年/成立以来曲线 + Top10 成分股 + 相关 ETF
- `/stats` 统计页：百分位热力图 + 分布柱状图

