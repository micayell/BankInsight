// 파일 위치: front/final_pjt/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/userStore";

import IndexView from "@/views/IndexView.vue";
import LoginView from "@/views/LoginView.vue";
import RegistrationView from "@/views/RegistrationView.vue";
import MapView from "@/views/MapView.vue";
import ArticleListView from "@/views/ArticleListView.vue";
import ArticleCreateView from "@/views/ArticleCreateView.vue";
import SearchView from "@/views/SearchView.vue";
import SpotView from "@/views/SpotView.vue";
import FinancialProductsView from "@/views/FinancialProductsView.vue";
import DepositDetailView from "@/views/DepositDetailView.vue";
import SavingDetailView from "@/views/SavingDetailView.vue";
import ProfileView from "@/views/ProfileView.vue";
import ArticleDetailView from "@/views/ArticleDetailView.vue";
import ArticleUpdateView from "@/views/ArticleUpdateView.vue";
import ProfileUpdateView from "@/views/ProfileUpdateView.vue";
import VideoDetailView from "@/views/VideoDetailView.vue";

const routes = [
  { path: "/", name: "home", component: IndexView },

  { path: "/login", name: "login", component: LoginView },
  { path: "/registration", name: "registration", component: RegistrationView },

  /* ---------- 프로필 ---------- */
  {
    path: "/profile",
    name: "profile-redirect", 
    redirect: () => {
      const userStore = useUserStore(); 
      if (userStore.isLogin && userStore.userInfo && typeof userStore.userInfo.username === 'string' && userStore.userInfo.username.trim() !== '') {
        return { name: 'profile', params: { username: userStore.userInfo.username } };
      }
      // 유효하지 않으면 로그인 페이지로 강제 이동
      return { name: 'login' };
    },
    meta: { requiresAuth: true },
  },
  // /profile/:username
  {
    path: "/profile/:username",
    name: "profile",
    component: ProfileView,
    props: true,
    meta: { requiresAuth: true },
  },
  // /profile/:username/edit
  {
    path: "/profile/:username/edit",
    name: "profile-edit",
    component: ProfileUpdateView,
    props: true,
    meta: { requiresAuth: true },
  },

  /* ---------- 기타 페이지 ---------- */
  { path: "/map", name: "map", component: MapView },

  {
    path: "/articlecreate",
    name: "articlecreate",
    component: ArticleCreateView,
  },
  { path: "/article", name: "article", component: ArticleListView },
  {
    path: "/article/:id",
    name: "article-detail",
    component: ArticleDetailView,
    props: true,
  },
  {
    path: "/articles/:id/edit",
    name: "articleupdate",
    component: ArticleUpdateView,
    props: true,
  },

  { path: "/search", name: "search", component: SearchView },
  { path: "/videos/:videoId", name: "video-detail", component: VideoDetailView },

  { path: "/spot", name: "spot", component: SpotView },

  {
    path: "/financial-products",
    name: "financial-products",
    component: FinancialProductsView,
  },
  {
    path: "/financial-products/deposits/:code",
    name: "deposit-detail",
    component: DepositDetailView,
    props: true,
  },
  {
    path: "/financial-products/savings/:code",
    name: "saving-detail",
    component: SavingDetailView,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

/* ---------- 전역 네비게이션 가드 ---------- */
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore();
  if (to.meta.requiresAuth && !userStore.isLogin) next("/login");
  else next();
});

export default router;
