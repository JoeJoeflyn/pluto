import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "dashboard",
      component: () => import("@/views/Dashboard.vue"),
    },
    {
      path: "/scan",
      name: "scan",
      component: () => import("@/views/Scan.vue"),
    },
    {
      path: "/expenses",
      name: "expenses",
      component: () => import("@/views/ExpensesList.vue"),
    },
    {
      path: "/expenses/:id",
      name: "expenses-detail",
      component: () => import("@/views/ExpenseDetail.vue"),
    },
    {
      path: "/merchants",
      name: "merchants",
      component: () => import("@/views/Merchants.vue"),
    },
    {
      path: "/stats",
      name: "stats",
      component: () => import("@/views/Stats.vue"),
    },
  ],
});

export default router;
