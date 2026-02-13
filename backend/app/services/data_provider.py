from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import akshare as ak
import os
import pandas as pd

os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""


@dataclass
class HistoryResult:
    source: str
    frame: pd.DataFrame


def read_index_list(excel_path: str) -> list[dict[str, str]]:
    path = Path(excel_path)
    if not path.exists():
        return []
    df = pd.read_excel(path)
    if df.empty:
        return []

    codes = df.iloc[:, 0].tolist()
    names = df.iloc[:, 1].tolist() if len(df.columns) > 1 else ["" for _ in codes]
    full_names = df.iloc[:, 2].tolist() if len(df.columns) > 2 else ["" for _ in codes]

    result: list[dict[str, str]] = []
    for code, name, full_name in zip(codes, names, full_names):
        if pd.isna(code):
            continue
        code_s = str(code).strip()
        name_s = str(name).strip() if pd.notna(name) else f"INDEX-{code_s}"
        full_name_s = str(full_name).strip() if pd.notna(full_name) else ""
        result.append({"code": code_s, "name": name_s, "full_name": full_name_s})
    return result


def _standardize_history(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    rename_map = {
        "date": "trade_date",
        "close": "close",
        "high": "high",
        "low": "low",
        "pct_chg": "pct_change",
        "日期": "trade_date",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "涨跌幅": "pct_change",
    }

    normalized = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}).copy()
    if "trade_date" not in normalized.columns or "close" not in normalized.columns:
        return pd.DataFrame()

    normalized["trade_date"] = pd.to_datetime(normalized["trade_date"], errors="coerce")
    normalized["close"] = pd.to_numeric(normalized["close"], errors="coerce")
    normalized["high"] = pd.to_numeric(normalized.get("high", normalized["close"]), errors="coerce")
    normalized["low"] = pd.to_numeric(normalized.get("low", normalized["close"]), errors="coerce")
    normalized["pct_change"] = pd.to_numeric(normalized.get("pct_change"), errors="coerce")

    normalized = normalized.dropna(subset=["trade_date", "close", "high", "low"])
    normalized = normalized.sort_values("trade_date")
    return normalized[["trade_date", "close", "high", "low", "pct_change"]]


def _standardize_history_csindex(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or len(df.columns) < 10:
        return pd.DataFrame()

    date_col = df.columns[0]
    high_col = df.columns[7]
    low_col = df.columns[8]
    close_col = df.columns[9]
    pct_col = df.columns[11] if len(df.columns) > 11 else None

    normalized = pd.DataFrame(
        {
            "trade_date": df[date_col],
            "close": df[close_col],
            "high": df[high_col],
            "low": df[low_col],
            "pct_change": df[pct_col] if pct_col is not None else None,
        }
    )

    normalized["trade_date"] = pd.to_datetime(normalized["trade_date"], errors="coerce")
    normalized["close"] = pd.to_numeric(normalized["close"], errors="coerce")
    normalized["high"] = pd.to_numeric(normalized["high"], errors="coerce")
    normalized["low"] = pd.to_numeric(normalized["low"], errors="coerce")
    normalized["pct_change"] = pd.to_numeric(normalized.get("pct_change"), errors="coerce")

    normalized = normalized.dropna(subset=["trade_date", "close"])
    normalized["high"] = normalized["high"].fillna(normalized["close"])
    normalized["low"] = normalized["low"].fillna(normalized["close"])
    normalized = normalized.dropna(subset=["high", "low"])
    normalized = normalized.sort_values("trade_date")
    return normalized[["trade_date", "close", "high", "low", "pct_change"]]


def fetch_index_history(
    index_code: str,
    history_years: int = 5,
    index_name: str | None = None,
    index_full_name: str | None = None,
) -> HistoryResult | None:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=history_years * 365)

    data_sources: list[tuple[str, Any]] = [
        (
            "ak_index_zh_a_hist",
            lambda: ak.index_zh_a_hist(
                symbol=index_code,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
            ),
        ),
        (
            "ak_stock_zh_index_daily_em_csi",
            lambda: ak.stock_zh_index_daily_em(
                symbol=f"csi{index_code}",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
            ),
        ),
        (
            "ak_stock_zh_index_daily_em_plain",
            lambda: ak.stock_zh_index_daily_em(
                symbol=index_code,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
            ),
        ),
        (
            "ak_stock_zh_index_daily",
            lambda: ak.stock_zh_index_daily(
                symbol=f"{'sz' if str(index_code).startswith('399') else 'sh'}{index_code}"
            ),
        ),
        (
            "ak_stock_zh_index_hist_csindex",
            lambda: ak.stock_zh_index_hist_csindex(symbol=index_code),
        ),
    ]

    code_s = str(index_code)
    if code_s.startswith("399"):
        data_sources = [data_sources[-2], *data_sources[:-2], data_sources[-1]]
    elif code_s.startswith("93"):
        data_sources = [data_sources[-1], *data_sources[:-1]]

    for source_name, source_func in data_sources:
        try:
            raw_df = source_func()
            normalized = _standardize_history_csindex(raw_df) if source_name == "ak_stock_zh_index_hist_csindex" else _standardize_history(raw_df)
            if not normalized.empty:
                return HistoryResult(source=source_name, frame=normalized)
        except Exception:
            continue

    return None


def fetch_index_components(index_code: str, top_n: int = 10) -> list[dict[str, Any]]:
    providers: list[Any] = [
        lambda: ak.index_stock_cons(symbol=index_code),
        lambda: ak.index_stock_cons_sina(symbol=index_code),
    ]
    for provider in providers:
        try:
            df = provider()
            if df is None or df.empty:
                continue
            rows = df.head(top_n).reset_index(drop=True)
            result: list[dict[str, Any]] = []
            for i, row in rows.iterrows():
                stock_code = str(row.iloc[0]).strip() if len(row) > 0 else ""
                stock_name = str(row.iloc[1]).strip() if len(row) > 1 else ""
                weight = None
                if len(row) > 2:
                    try:
                        weight = float(row.iloc[2])
                    except Exception:
                        weight = None
                result.append(
                    {
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "weight": weight,
                        "rank": i + 1,
                    }
                )
            if result:
                return result
        except Exception:
            continue
    return []


def fetch_etf_quote(etf_code: str) -> tuple[float | None, float | None]:
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = ak.fund_etf_hist_em(
            symbol=etf_code,
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust="qfq",
        )
        if df is None or df.empty:
            return None, None

        close_col = "收盘" if "收盘" in df.columns else "close"
        chg_col = "涨跌幅" if "涨跌幅" in df.columns else "pct_chg"
        price = float(pd.to_numeric(df[close_col], errors="coerce").dropna().iloc[-1])
        change_series = pd.to_numeric(df.get(chg_col), errors="coerce").dropna()
        change = float(change_series.iloc[-1]) if not change_series.empty else None
        return price, change
    except Exception:
        return None, None
