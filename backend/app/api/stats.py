from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import load_app_config
from app.core.database import get_db
from app.models import Index, IndexMetric
from app.schemas import DistributionBucket, DistributionResponse, HeatmapCell, HeatmapResponse
from app.services.analytics import calculate_percentile, get_temperature_color

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(db: Session = Depends(get_db)):
    config = load_app_config()
    rows = db.execute(select(Index, IndexMetric).join(IndexMetric, IndexMetric.index_code == Index.code)).all()
    cells: list[HeatmapCell] = []
    metrics = ["percentile", "distance_to_high_3y", "distance_to_low_3y"]
    for idx, metric in rows:
        latest_close = metric.current_price
        if latest_close is None or metric.high_3y <= 0:
            continue
        distance_to_high = max(0.0, (1 - latest_close / metric.high_3y) * 100)
        distance_to_low = max(0.0, (latest_close / max(metric.low_3y, 1e-6) - 1) * 100)
        derived = {
            "percentile": float(metric.percentile_since_inception or 0.0),
            "distance_to_high_3y": float(min(distance_to_high, 100)),
            "distance_to_low_3y": float(min(distance_to_low, 100)),
        }
        for metric_name, value in derived.items():
            percentile = calculate_percentile(value, list(derived.values()))
            cells.append(
                HeatmapCell(
                    index_code=idx.code,
                    index_name=idx.name,
                    metric=metric_name,
                    value=round(value, 2),
                    percentile=round(percentile, 2),
                    color=get_temperature_color(
                        percentile,
                        colors=config.temperature_colors,
                        low=config.percentile_low,
                        high=config.percentile_high,
                    ),
                )
            )
    return HeatmapResponse(metrics=metrics, cells=cells)


@router.get("/distribution", response_model=DistributionResponse)
def get_distribution(db: Session = Depends(get_db)):
    values = db.execute(select(IndexMetric.percentile_since_inception)).scalars().all()
    values = [v for v in values if v is not None]
    buckets = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 101)]
    result: list[DistributionBucket] = []
    for low, high in buckets:
        count = sum(1 for v in values if low <= v < high)
        label = f"{low}-{high - 1}"
        result.append(DistributionBucket(bucket=label, count=count))
    return DistributionResponse(buckets=result)
