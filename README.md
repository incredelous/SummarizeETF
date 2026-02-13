# SummarizeETF

ETF/指数数据分析项目，包含：
- `backend/`：FastAPI 服务与数据刷新任务
- `frontend/`：Vue 3 + Vite 前端界面
- 根目录脚本：离线分析与报告生成（如 `index_analyzer_v2.py`）

## Project Structure

```text
SummarizeETF/
|- backend/                 # API, services, models, tasks
|- frontend/                # Vue 3 + TypeScript UI
|- data/                    # 本地数据输入（已忽略，不入库）
|- output/                  # 报告输出目录（已忽略，不入库）
|- requirements.txt         # Python 依赖
|- CONTRIBUTING.md          # 团队协作规范
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
cd frontend && npm install
```

### 2. Refresh index/ETF data

```bash
python backend/scripts/refresh_data.py
```

### 3. Start backend API

```bash
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

### 4. Start frontend

```bash
cd frontend
npm run dev
```

默认访问：
- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8000`

## Testing

```bash
pytest backend/tests -q
```

## Build Frontend

```bash
cd frontend
npm run build
npm run preview
```

## Legacy/Offline Scripts

可直接运行以下脚本生成离线分析报告：
- `python index_analyzer_unified.py`
- `python index_analyzer_v2.py`
- `python process_index_data.py`

## Team Collaboration

- 使用 `main` 作为稳定分支
- 功能开发基于特性分支（例如 `feat/stats-endpoint`）
- 提交信息遵循 Conventional Commits（`feat:`, `fix:`, `docs:` 等）
- 通过 Pull Request 合并代码

详见 `CONTRIBUTING.md`。

