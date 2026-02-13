<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchIndices, type IndexSummary } from "../api/indices";

const router = useRouter();

const loading = ref(false);
const allRows = ref<IndexSummary[]>([]);

const topN = ref(20);
const query = ref("");
const sortOrder = ref<"asc" | "desc">("desc");
const page = ref(1);
const pageSize = ref(20);

function percentileColor(percentile: number | null): string {
  if (percentile == null) return "#9ca3af";
  if (percentile < 30) return "#16a34a";
  if (percentile <= 70) return "#f59e0b";
  return "#dc2626";
}

function comparePercentile(a: IndexSummary, b: IndexSummary, order: "asc" | "desc"): number {
  const av = a.percentile_since_inception ?? Number.POSITIVE_INFINITY;
  const bv = b.percentile_since_inception ?? Number.POSITIVE_INFINITY;
  return order === "asc" ? av - bv : bv - av;
}

async function loadAll() {
  loading.value = true;
  try {
    const first = await fetchIndices({ page: 1, page_size: 200, sort_by: "code", sort_order: "asc" });
    const total = first.total;
    const pages = Math.max(1, Math.ceil(total / 200));
    const rows: IndexSummary[] = [...first.items];

    for (let p = 2; p <= pages; p += 1) {
      const data = await fetchIndices({ page: p, page_size: 200, sort_by: "code", sort_order: "asc" });
      rows.push(...data.items);
    }

    allRows.value = rows;
    page.value = 1;
  } finally {
    loading.value = false;
  }
}

const rankingBaseRows = computed(() => allRows.value.filter((r) => r.percentile_since_inception != null));

const hottestRows = computed(() => {
  return [...rankingBaseRows.value].sort((a, b) => comparePercentile(a, b, "desc")).slice(0, topN.value);
});

const coldestRows = computed(() => {
  return [...rankingBaseRows.value].sort((a, b) => comparePercentile(a, b, "asc")).slice(0, topN.value);
});

const filteredRows = computed(() => {
  const keyword = query.value.trim().toLowerCase();
  return allRows.value.filter((row) => {
    const qHit =
      !keyword ||
      row.code.toLowerCase().includes(keyword) ||
      row.name.toLowerCase().includes(keyword) ||
      (row.full_name || "").toLowerCase().includes(keyword);
    return qHit;
  });
});

const sortedRows = computed(() => {
  const rows = [...filteredRows.value];
  rows.sort((a, b) => comparePercentile(a, b, sortOrder.value));
  return rows;
});

const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  return sortedRows.value.slice(start, start + pageSize.value);
});

onMounted(loadAll);
</script>

<template>
  <el-card>
    <template #header>
      <div class="top-header">
        <div>
          <div class="title">Top / Bottom Percentile Ranking</div>
          <div class="sub">Readable ranking view for high-volume index universe</div>
        </div>
        <div class="actions">
          <el-input-number v-model="topN" :min="5" :max="100" :step="5" controls-position="right" />
          <el-button :loading="loading" @click="loadAll">Reload</el-button>
        </div>
      </div>
    </template>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card shadow="never">
          <template #header>Hottest Top {{ topN }}</template>
          <el-table :data="hottestRows" size="small" height="380">
            <el-table-column prop="code" label="Code" width="100" />
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="percentile_since_inception" label="Percentile" width="120" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="never">
          <template #header>Coldest Top {{ topN }}</template>
          <el-table :data="coldestRows" size="small" height="380">
            <el-table-column prop="code" label="Code" width="100" />
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="percentile_since_inception" label="Percentile" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </el-card>

  <el-card style="margin-top: 16px">
    <template #header>
      <div class="table-header">
        <div class="title">Filterable Index Table</div>
        <div class="filters">
          <el-input v-model="query" placeholder="Search code/name" style="width: 220px" />
          <el-select v-model="sortOrder" style="width: 140px">
            <el-option label="Percentile Desc" value="desc" />
            <el-option label="Percentile Asc" value="asc" />
          </el-select>
        </div>
      </div>
    </template>

    <el-table :data="pagedRows" v-loading="loading">
      <el-table-column prop="code" label="Code" width="110" />
      <el-table-column prop="name" label="Name" min-width="180" />
      <el-table-column prop="full_name" label="Full Name" min-width="220" />
      <el-table-column prop="current_price" label="Current Price" width="130" />
      <el-table-column label="Percentile" width="220">
        <template #default="{ row }">
          <div class="percentile-cell">
            <el-progress
              :percentage="Math.max(0, Math.min(100, Number(row.percentile_since_inception ?? 0)))"
              :color="percentileColor(row.percentile_since_inception)"
              :stroke-width="14"
              :show-text="false"
            />
            <span class="percentile-text">
              {{ row.percentile_since_inception == null ? "-" : `${row.percentile_since_inception}%` }}
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Action" width="110">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/indices/${row.code}`)">Detail</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        layout="total, prev, pager, next, sizes"
        :total="sortedRows.length"
      />
    </div>
  </el-card>
</template>

<style scoped>
.top-header,
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.title {
  font-size: 16px;
  font-weight: 700;
}
.sub {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}
.actions,
.filters {
  display: flex;
  align-items: center;
  gap: 10px;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.percentile-cell {
  display: grid;
  grid-template-columns: 1fr 56px;
  align-items: center;
  gap: 8px;
}
.percentile-text {
  font-size: 12px;
  color: #374151;
  text-align: right;
}
@media (max-width: 900px) {
  .top-header,
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .actions,
  .filters {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
