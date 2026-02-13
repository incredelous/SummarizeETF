from __future__ import annotations

from sqlalchemy.engine import Engine


def ensure_runtime_schema(engine: Engine):
    with engine.begin() as conn:
        index_cols = conn.exec_driver_sql("PRAGMA table_info(indices)").fetchall()
        index_names = {row[1] for row in index_cols}
        if "full_name" not in index_names:
            conn.exec_driver_sql("ALTER TABLE indices ADD COLUMN full_name VARCHAR(256)")

        metric_cols = conn.exec_driver_sql("PRAGMA table_info(index_metrics)").fetchall()
        metric_names = {row[1] for row in metric_cols}
        if metric_cols and "current_price" not in metric_names:
            conn.exec_driver_sql("ALTER TABLE index_metrics ADD COLUMN current_price FLOAT")
        if metric_cols and "percentile_1m" not in metric_names:
            conn.exec_driver_sql("ALTER TABLE index_metrics ADD COLUMN percentile_1m FLOAT")
        if metric_cols and "percentile_3y" not in metric_names:
            conn.exec_driver_sql("ALTER TABLE index_metrics ADD COLUMN percentile_3y FLOAT")
        if metric_cols and "percentile_since_inception" not in metric_names:
            conn.exec_driver_sql("ALTER TABLE index_metrics ADD COLUMN percentile_since_inception FLOAT")
        if metric_cols and "percentile" in metric_names:
            conn.exec_driver_sql(
                "UPDATE index_metrics SET percentile_since_inception = percentile "
                "WHERE percentile_since_inception IS NULL"
            )

        # Try to remove deprecated columns on modern SQLite; if unsupported, keep compatibility.
        metric_cols = conn.exec_driver_sql("PRAGMA table_info(index_metrics)").fetchall()
        metric_names = {row[1] for row in metric_cols}
        if "temperature_status" in metric_names:
            try:
                conn.exec_driver_sql("ALTER TABLE index_metrics DROP COLUMN temperature_status")
            except Exception:
                pass
        if "percentile" in metric_names:
            try:
                conn.exec_driver_sql("ALTER TABLE index_metrics DROP COLUMN percentile")
            except Exception:
                pass

        # Deprecated tables were used only for detail history/components/ETF content.
        conn.exec_driver_sql("DROP TABLE IF EXISTS index_snapshots")
        conn.exec_driver_sql("DROP TABLE IF EXISTS index_components")
        conn.exec_driver_sql("DROP TABLE IF EXISTS related_etfs")
