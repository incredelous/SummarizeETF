from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from app.core.database import Base, engine
from app.core.schema import ensure_runtime_schema
from app.tasks.update_indices import create_and_run_refresh


def setup_logger() -> logging.Logger:
    log_dir = ROOT / "backend" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"refresh_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger("refresh")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info("log_file=%s", log_path)
    return logger


def ensure_schema(logger: logging.Logger):
    ensure_runtime_schema(engine)
    logger.info("schema checked")


def main():
    parser = argparse.ArgumentParser(description="Refresh index data into SQLite")
    parser.add_argument(
        "--force",
        nargs="*",
        metavar="INDEX_CODE",
        help=(
            "Force refresh mode. Use `--force` to refresh all indices, "
            "or `--force 000300 000905` to refresh only specific index codes."
        ),
    )
    args = parser.parse_args()

    logger = setup_logger()
    force_raw = args.force
    force_all = force_raw is not None and len(force_raw) == 0
    force_codes = [code.strip() for code in (force_raw or []) if code and code.strip()] or None

    logger.info("refresh start")
    logger.info("force_all=%s force_codes=%s", force_all, force_codes)
    Base.metadata.create_all(bind=engine)
    ensure_schema(logger)

    def progress(current: int, total: int, code: str, name: str):
        logger.info("(%s/%s) %s %s", current, total, code, name)

    task = create_and_run_refresh(
        progress=progress,
        log=logger.info,
        force_all=force_all,
        force_codes=force_codes,
    )
    logger.info("refresh finished")
    logger.info("task_id=%s", task.task_id)
    logger.info("status=%s", task.status)
    if task.message:
        logger.info("message=%s", task.message)


if __name__ == "__main__":
    main()
