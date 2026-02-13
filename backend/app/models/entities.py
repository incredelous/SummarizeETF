from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Index(Base):
    __tablename__ = "indices"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    market: Mapped[str] = mapped_column(String(32), default="CN")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    metric = relationship("IndexMetric", back_populates="index", uselist=False, cascade="all, delete-orphan")


class IndexMetric(Base):
    __tablename__ = "index_metrics"
    __table_args__ = (UniqueConstraint("index_code", name="uq_metric_index"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    index_code: Mapped[str] = mapped_column(ForeignKey("indices.code"), nullable=False, index=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentile_1m: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentile_3y: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentile_since_inception: Mapped[float | None] = mapped_column(Float, nullable=True)
    high_3y: Mapped[float] = mapped_column(Float, nullable=False)
    low_3y: Mapped[float] = mapped_column(Float, nullable=False)
    avg_3y: Mapped[float] = mapped_column(Float, nullable=False)

    index = relationship("Index", back_populates="metric")


class RefreshTask(Base):
    __tablename__ = "refresh_tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
