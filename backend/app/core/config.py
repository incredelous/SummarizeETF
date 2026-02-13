from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AppConfig:
    database_url: str
    history_years: int
    percentile_low: float
    percentile_high: float
    temperature_colors: dict[str, str]
    excel_path: str
    scheduler_day_of_week: str
    scheduler_hour: int
    scheduler_minute: int
    api_host: str
    api_port: int


def _default_config(project_root: Path) -> dict[str, Any]:
    return {
        "database": {
            "url": f"sqlite:///{(project_root / 'backend' / 'data' / 'summarize_etf.db').as_posix()}",
        },
        "data": {
            "history_years": 5,
            "excel_path": str(project_root / "data" / "指数列表.xlsx"),
        },
        "percentile": {
            "low": 30,
            "high": 70,
        },
        "colors": {
            "low": "#4CAF50",
            "medium": "#FFC107",
            "high": "#F44336",
        },
        "scheduler": {
            "day_of_week": "sun",
            "hour": 18,
            "minute": 0,
        },
        "api": {
            "host": "127.0.0.1",
            "port": 8000,
        },
    }


def load_raw_config() -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[3]
    config_path = project_root / "config.yaml"
    defaults = _default_config(project_root)

    loaded: dict[str, Any] = {}
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}

    def merged(base: dict[str, Any], custom: dict[str, Any]) -> dict[str, Any]:
        result = dict(base)
        for k, v in custom.items():
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = merged(result[k], v)
            else:
                result[k] = v
        return result

    return merged(defaults, loaded)


def load_app_config() -> AppConfig:
    raw = load_raw_config()
    project_root = Path(__file__).resolve().parents[3]
    raw_db_url = str(raw["database"]["url"])
    raw_db_path = Path(raw_db_url.replace("sqlite:///", ""))
    if not raw_db_path.is_absolute():
        raw_db_path = (project_root / raw_db_path).resolve()
    db_url = f"sqlite:///{raw_db_path.as_posix()}"
    db_path = raw_db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    excel_path = raw["data"]["excel_path"]
    if not Path(excel_path).is_absolute():
        excel_path = str((project_root / excel_path).resolve())

    return AppConfig(
        database_url=db_url,
        history_years=int(raw["data"]["history_years"]),
        percentile_low=float(raw["percentile"]["low"]),
        percentile_high=float(raw["percentile"]["high"]),
        temperature_colors=raw["colors"],
        excel_path=excel_path,
        scheduler_day_of_week=str(raw["scheduler"]["day_of_week"]),
        scheduler_hour=int(raw["scheduler"]["hour"]),
        scheduler_minute=int(raw["scheduler"]["minute"]),
        api_host=str(raw["api"]["host"]),
        api_port=int(raw["api"]["port"]),
    )
