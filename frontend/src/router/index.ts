import { createRouter, createWebHistory } from "vue-router";
import IndexListView from "../views/IndexListView.vue";
import IndexDetailView from "../views/IndexDetailView.vue";
import StatsView from "../views/StatsView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: IndexListView },
    { path: "/indices/:code", component: IndexDetailView },
    { path: "/stats", component: StatsView }
  ]
});

export default router;

