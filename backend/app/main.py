from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.indices import router as indices_router
from app.api.stats import router as stats_router
from app.api.tasks import router as tasks_router
from app.core.database import Base, engine
from app.core.schema import ensure_runtime_schema
from app.scheduler import start_scheduler, stop_scheduler

app = FastAPI(title="SummarizeETF API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema(engine)
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(indices_router)
app.include_router(stats_router)
app.include_router(tasks_router)
