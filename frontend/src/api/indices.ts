import client from "./client";

export type IndexSummary = {
  code: string;
  name: string;
  full_name: string | null;
  csindex_url: string;
  current_price: number | null;
  percentile_1m: number | null;
  percentile_3y: number | null;
  percentile_since_inception: number | null;
  updated_at: string;
};

export type IndexDetail = {
  summary: IndexSummary;
  high_3y: number | null;
  low_3y: number | null;
  avg_3y: number | null;
};

export async function fetchIndices(params: {
  q?: string;
  page: number;
  page_size: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}) {
  const { data } = await client.get("/api/v1/indices", { params });
  return data as { items: IndexSummary[]; total: number; page: number; page_size: number };
}

export async function fetchIndexDetail(code: string) {
  const { data } = await client.get(`/api/v1/indices/${code}`);
  return data as IndexDetail;
}

export async function fetchHeatmap() {
  const { data } = await client.get("/api/v1/stats/heatmap");
  return data as {
    metrics: string[];
    cells: Array<{
      index_code: string;
      index_name: string;
      metric: string;
      value: number;
      percentile: number;
      color: string;
    }>;
  };
}

export async function fetchDistribution() {
  const { data } = await client.get("/api/v1/stats/distribution");
  return data as { buckets: Array<{ bucket: string; count: number }> };
}

export async function triggerRefresh() {
  const { data } = await client.post("/api/v1/tasks/refresh");
  return data as { task_id: string; status: string };
}
