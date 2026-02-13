<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchIndices, triggerRefresh, type IndexSummary } from "../api/indices";

const router = useRouter();
const rows = ref<IndexSummary[]>([]);
const loading = ref(false);
const refreshing = ref(false);
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);
const q = ref("");
const sortBy = ref("code");
const sortOrder = ref<"asc" | "desc">("asc");

async function load() {
  loading.value = true;
  try {
    const data = await fetchIndices({
      q: q.value || undefined,
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    });
    rows.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

function handleSort({ prop, order }: { prop: string; order: "ascending" | "descending" | null }) {
  if (!prop) return;
  sortBy.value = prop;
  sortOrder.value = order === "descending" ? "desc" : "asc";
  load();
}

async function refreshNow() {
  refreshing.value = true;
  try {
    await triggerRefresh();
  } finally {
    refreshing.value = false;
  }
}

onMounted(load);
</script>

<template>
  <el-card>
    <template #header>
      <div class="toolbar">
        <div class="left">
          <el-input v-model="q" placeholder="搜索代码或名称" style="width: 220px" @keyup.enter="load" />
          <el-button @click="load">查询</el-button>
        </div>
        <el-button type="primary" :loading="refreshing" @click="refreshNow">刷新</el-button>
      </div>
    </template>

    <el-table :data="rows" v-loading="loading" @sort-change="handleSort">
      <el-table-column prop="code" label="代码" sortable="custom" />
      <el-table-column prop="name" label="简称" sortable="custom" />
      <el-table-column prop="full_name" label="全称" />
      <el-table-column prop="current_price" label="最新点位" sortable="custom" />
      <el-table-column prop="percentile_1m" label="近一月百分位" sortable="custom" />
      <el-table-column prop="percentile_3y" label="近三年百分位" sortable="custom" />
      <el-table-column prop="percentile_since_inception" label="成立以来百分位" sortable="custom" />
      <el-table-column prop="updated_at" label="更新时间" sortable="custom" />
      <el-table-column label="外部链接" width="120">
        <template #default="{ row }">
          <el-link type="primary" :href="row.csindex_url" target="_blank" rel="noopener noreferrer">
            中证详情
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="细节" width="120">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/indices/${row.code}`)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        layout="total, prev, pager, next, sizes"
        :total="total"
        @current-change="load"
        @size-change="load"
      />
    </div>
  </el-card>
</template>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.left {
  display: flex;
  gap: 12px;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>

