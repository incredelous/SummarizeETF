from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Index, IndexMetric
from app.schemas import IndexDetail, IndexListResponse, IndexSummary

router = APIRouter(prefix="/api/v1", tags=["indices"])


@router.get("/indices", response_model=IndexListResponse)
def list_indices(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="code"),
    sort_order: str = Query(default="asc"),
    db: Session = Depends(get_db),
):
    stmt = select(Index, IndexMetric).join(IndexMetric, IndexMetric.index_code == Index.code, isouter=True)
    if q:
        keyword = f"%{q.strip()}%"
        stmt = stmt.where(or_(Index.code.like(keyword), Index.name.like(keyword)))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    sort_col_map = {
        "code": Index.code,
        "name": Index.name,
        "percentile_1m": IndexMetric.percentile_1m,
        "percentile_3y": IndexMetric.percentile_3y,
        "percentile_since_inception": IndexMetric.percentile_since_inception,
        "percentile": IndexMetric.percentile_since_inception,
        "updated_at": Index.updated_at,
    }
    sort_col = sort_col_map.get(sort_by, Index.code)
    if sort_order.lower() == "desc":
        stmt = stmt.order_by(desc(sort_col))
    else:
        stmt = stmt.order_by(sort_col)

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(stmt).all()
    items: list[IndexSummary] = []
    for idx, metric in rows:
        csindex_url = f"https://www.csindex.com.cn/#/indices/family/detail?indexCode={idx.code}"
        items.append(
            IndexSummary(
                code=idx.code,
                name=idx.name,
                full_name=idx.full_name,
                csindex_url=csindex_url,
                current_price=metric.current_price if metric else None,
                percentile_1m=metric.percentile_1m if metric else None,
                percentile_3y=metric.percentile_3y if metric else None,
                percentile_since_inception=metric.percentile_since_inception if metric else None,
                updated_at=idx.updated_at,
            )
        )
    return IndexListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/indices/{index_code}", response_model=IndexDetail)
def get_index_detail(index_code: str, db: Session = Depends(get_db)):
    idx = db.get(Index, index_code)
    if idx is None:
        raise HTTPException(status_code=404, detail="Index not found")
    metric = db.execute(select(IndexMetric).where(IndexMetric.index_code == index_code)).scalar_one_or_none()

    csindex_url = f"https://www.csindex.com.cn/#/indices/family/detail?indexCode={idx.code}"
    summary = IndexSummary(
        code=idx.code,
        name=idx.name,
        full_name=idx.full_name,
        csindex_url=csindex_url,
        current_price=metric.current_price if metric else None,
        percentile_1m=metric.percentile_1m if metric else None,
        percentile_3y=metric.percentile_3y if metric else None,
        percentile_since_inception=metric.percentile_since_inception if metric else None,
        updated_at=idx.updated_at,
    )
    return IndexDetail(
        summary=summary,
        high_3y=metric.high_3y if metric else None,
        low_3y=metric.low_3y if metric else None,
        avg_3y=metric.avg_3y if metric else None,
    )
