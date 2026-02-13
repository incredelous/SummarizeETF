from __future__ import annotations

from datetime import date, datetime, timedelta
from threading import Lock
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import load_app_config
from app.core.database import SessionLocal
from app.models import Index, IndexMetric, RefreshTask
from app.services.analytics import calculate_percentile
from app.services.data_provider import fetch_index_history, read_index_list

_TASK_PROGRESS_LOCK = Lock()
_TASK_PROGRESS: dict[str, dict[str, object]] = {}


def create_refresh_task(db: Session) -> RefreshTask:
    task = RefreshTask(
        task_id=uuid4().hex,
        status="running",
        started_at=datetime.utcnow(),
        finished_at=None,
        message="Task started",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def _upsert_index(db: Session, code: str, name: str, full_name: str | None) -> Index:
    index = db.get(Index, code)
    if index is None:
        index = Index(code=code, name=name, full_name=full_name, market="CN")
        db.add(index)
    else:
        index.name = name
        index.full_name = full_name
    db.flush()
    return index


def _has_metric_for_date(db: Session, code: str, as_of_date: date) -> bool:
    stmt = (
        select(IndexMetric.id)
        .where(IndexMetric.index_code == code, IndexMetric.as_of_date == as_of_date)
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none() is not None


def _normalize_force_codes(force_codes: list[str] | None) -> set[str]:
    if not force_codes:
        return set()
    return {str(code).strip() for code in force_codes if str(code).strip()}


def _set_task_progress(task_id: str, **kwargs):
    with _TASK_PROGRESS_LOCK:
        current = _TASK_PROGRESS.get(task_id, {}).copy()
        current.update(kwargs)
        total = int(current.get("total_count", 0) or 0)
        processed = int(current.get("processed_count", 0) or 0)
        current["progress_percent"] = 100.0 if total <= 0 else round((processed / total) * 100, 2)
        _TASK_PROGRESS[task_id] = current


def get_task_progress(task_id: str) -> dict[str, object] | None:
    with _TASK_PROGRESS_LOCK:
        progress = _TASK_PROGRESS.get(task_id)
        return progress.copy() if progress else None


def run_refresh(
    task_id: str,
    progress=None,
    log=None,
    max_retries: int = 3,
    force_all: bool = False,
    force_codes: list[str] | None = None,
):
    config = load_app_config()
    force_code_set = _normalize_force_codes(force_codes)
    db = SessionLocal()
    try:
        index_list = read_index_list(config.excel_path)
        if not index_list:
            raise RuntimeError(f"No index list found at {config.excel_path}")

        def emit(message: str):
            if log:
                log(message)

        if force_code_set:
            source_codes = {item["code"] for item in index_list}
            missing_codes = sorted(force_code_set - source_codes)
            if missing_codes:
                emit(f"force list not found in index source, ignored: {','.join(missing_codes)}")
            index_list = [item for item in index_list if item["code"] in force_code_set]
            if not index_list:
                raise RuntimeError("force refresh codes are all missing from index source")

        total = len(index_list)
        today = datetime.utcnow().date()
        success_count = 0
        skipped_count = 0
        failed_count = 0
        processed_count = 0
        _set_task_progress(
            task_id,
            status="running",
            total_count=total,
            processed_count=0,
            success_count=0,
            skipped_count=0,
            failed_count=0,
            current_index_code=None,
            current_index_name=None,
        )

        for i, item in enumerate(index_list, start=1):
            code = item["code"]
            name = item["name"]
            full_name = item.get("full_name") or None
            if progress:
                progress(i, total, code, name)
            _set_task_progress(task_id, current_index_code=code, current_index_name=name)

            if not force_all and not force_code_set and _has_metric_for_date(db, code, today):
                skipped_count += 1
                processed_count += 1
                emit(f"skip already refreshed today: {code} {name}")
                _set_task_progress(
                    task_id,
                    processed_count=processed_count,
                    success_count=success_count,
                    skipped_count=skipped_count,
                    failed_count=failed_count,
                    current_index_code=code,
                    current_index_name=name,
                )
                continue

            history_result = None
            for attempt in range(1, max_retries + 1):
                history_result = fetch_index_history(
                    code,
                    history_years=config.history_years,
                    index_name=name,
                    index_full_name=full_name,
                )
                if history_result is not None and not history_result.frame.empty:
                    if attempt > 1:
                        emit(f"history fetch succeeded after retry {attempt}/{max_retries}: {code}")
                    break
                emit(f"history fetch retry {attempt}/{max_retries}: {code} {name}")
            if history_result is None or history_result.frame.empty:
                _upsert_index(db, code=code, name=name, full_name=full_name)
                db.execute(delete(IndexMetric).where(IndexMetric.index_code == code))
                db.commit()
                emit(f"history fetch failed after retries, set empty metric: {code} {name}")
                failed_count += 1
                processed_count += 1
                _set_task_progress(
                    task_id,
                    processed_count=processed_count,
                    success_count=success_count,
                    skipped_count=skipped_count,
                    failed_count=failed_count,
                    current_index_code=code,
                    current_index_name=name,
                )
                continue

            _upsert_index(db, code=code, name=name, full_name=full_name)

            db.execute(delete(IndexMetric).where(IndexMetric.index_code == code))

            df = history_result.frame
            closes = [float(v) for v in df["close"].tolist()]
            current_price = closes[-1]
            percentile_since_inception = calculate_percentile(current_price, closes)

            one_month_ago = today - timedelta(days=30)
            df_1m = df[df["trade_date"] >= datetime.combine(one_month_ago, datetime.min.time())]
            if df_1m.empty:
                df_1m = df
            percentile_1m = calculate_percentile(current_price, [float(v) for v in df_1m["close"].tolist()])

            three_year_ago = today - timedelta(days=365 * 3)
            df_3y = df[df["trade_date"] >= datetime.combine(three_year_ago, datetime.min.time())]
            if df_3y.empty:
                df_3y = df
            percentile_3y = calculate_percentile(current_price, [float(v) for v in df_3y["close"].tolist()])

            db.add(
                IndexMetric(
                    index_code=code,
                    as_of_date=today,
                    current_price=current_price,
                    percentile_1m=percentile_1m,
                    percentile_3y=percentile_3y,
                    percentile_since_inception=percentile_since_inception,
                    high_3y=float(df_3y["close"].max()),
                    low_3y=float(df_3y["close"].min()),
                    avg_3y=float(df_3y["close"].mean()),
                )
            )

            db.commit()
            success_count += 1
            processed_count += 1
            _set_task_progress(
                task_id,
                processed_count=processed_count,
                success_count=success_count,
                skipped_count=skipped_count,
                failed_count=failed_count,
                current_index_code=code,
                current_index_name=name,
            )

        task = db.get(RefreshTask, task_id)
        if task:
            task.status = "completed"
            task.finished_at = datetime.utcnow()
            task.message = (
                f"Refresh completed: success={success_count}, "
                f"skipped={skipped_count}, failed={failed_count}, total={total}"
            )
            db.commit()
            _set_task_progress(task_id, status="completed")

    except Exception as exc:
        task = db.get(RefreshTask, task_id)
        if task:
            task.status = "failed"
            task.finished_at = datetime.utcnow()
            task.message = str(exc)
            db.commit()
        _set_task_progress(task_id, status="failed")
    finally:
        db.close()


def create_and_run_refresh(
    progress=None,
    log=None,
    force_all: bool = False,
    force_codes: list[str] | None = None,
) -> RefreshTask:
    db = SessionLocal()
    try:
        task = create_refresh_task(db)
    finally:
        db.close()
    run_refresh(
        task.task_id,
        progress=progress,
        log=log,
        force_all=force_all,
        force_codes=force_codes,
    )
    db2 = SessionLocal()
    try:
        latest = db2.get(RefreshTask, task.task_id)
        if latest is None:
            raise RuntimeError("refresh task unexpectedly missing")
        return latest
    finally:
        db2.close()


def get_task(task_id: str) -> RefreshTask | None:
    db = SessionLocal()
    try:
        return db.get(RefreshTask, task_id)
    finally:
        db.close()
