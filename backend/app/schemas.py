from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class IndexSummary(BaseModel):
    code: str
    name: str
    full_name: str | None
    csindex_url: str
    current_price: float | None
    percentile_1m: float | None
    percentile_3y: float | None
    percentile_since_inception: float | None
    updated_at: datetime


class IndexListResponse(BaseModel):
    items: list[IndexSummary]
    total: int
    page: int
    page_size: int


class IndexDetail(BaseModel):
    summary: IndexSummary
    high_3y: float | None
    low_3y: float | None
    avg_3y: float | None


class HeatmapCell(BaseModel):
    index_code: str
    index_name: str
    metric: str
    value: float
    percentile: float
    color: str


class HeatmapResponse(BaseModel):
    metrics: list[str]
    cells: list[HeatmapCell]


class DistributionBucket(BaseModel):
    bucket: str
    count: int


class DistributionResponse(BaseModel):
    buckets: list[DistributionBucket]


class RefreshTaskResponse(BaseModel):
    task_id: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    message: str | None
