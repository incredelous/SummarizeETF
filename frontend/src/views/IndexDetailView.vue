<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { fetchIndexDetail, type IndexDetail } from "../api/indices";

const route = useRoute();
const code = route.params.code as string;
const detail = ref<IndexDetail | null>(null);

async function loadDetail() {
  detail.value = await fetchIndexDetail(code);
}

onMounted(loadDetail);
</script>

<template>
  <div class="wrap" v-if="detail">
    <el-card>
      <template #header>
        <div class="title">{{ detail.summary.name }} ({{ detail.summary.code }})</div>
      </template>
      <div class="metrics">
        <el-statistic title="Current Price" :value="detail.summary.current_price || 0" />
        <el-statistic title="3Y High" :value="detail.high_3y || 0" />
        <el-statistic title="3Y Low" :value="detail.low_3y || 0" />
        <el-statistic title="3Y Avg" :value="detail.avg_3y || 0" />
        <el-statistic title="Percentile 1M" :value="detail.summary.percentile_1m || 0" />
        <el-statistic title="Percentile 3Y" :value="detail.summary.percentile_3y || 0" />
        <el-statistic title="Percentile Since Inception" :value="detail.summary.percentile_since_inception || 0" />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.title {
  font-size: 20px;
  font-weight: 700;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
@media (max-width: 900px) {
  .metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
