#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility entrypoint.

This script keeps the historical command `python index_analyzer_unified.py` working,
but delegates data refresh to the new backend task pipeline.
"""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    project_root = Path(__file__).resolve().parent
    script = project_root / "backend" / "scripts" / "refresh_data.py"
    if not script.exists():
        print(f"Missing script: {script}")
        return 1

    print("Running backend refresh task...")
    result = subprocess.run([sys.executable, str(script)], cwd=str(project_root))
    if result.returncode != 0:
        print("Refresh task failed.")
        return result.returncode

    print("Refresh completed.")
    print("Start backend API:  uvicorn app.main:app --app-dir backend --reload")
    print("Start frontend:     cd frontend && npm install && npm run dev")
    print("Open:               http://127.0.0.1:5173")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
