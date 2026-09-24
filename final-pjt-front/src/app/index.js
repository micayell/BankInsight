// 파일 위치: front/final_pjt/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/features/accounts/store/userStore.js";

import IndexView from "@/features/home/pages/IndexView.vue";
import LoginView from "@/features/accounts/pages/LoginView.vue";
import RegistrationView from "@/features/accounts/pages/RegistrationView.vue";
import ResetPasswordView from "@/features/accounts/pages/ResetPasswordView.vue";
import ResetPasswordConfirmView from "@/features/accounts/pages/ResetPasswordConfirmView.vue";
import MapView from "@/features/map/pages/MapView.vue";
import ArticleListView from "@/features/articles/pages/ArticleListView.vue";
import ArticleCreateView from "@/features/articles/pages/ArticleCreateView.vue";
import SearchView from "@/features/search/pages/SearchView.vue";
import SpotView from "@/features/spot/pages/SpotView.vue";

import MortgageDetailView from '@/features/products/pages/MortgageDetailView.vue';
import JeonseDetailView from '@/features/products/pages/JeonseDetailView.vue';
import FinancialProductsView from "@/features/products/pages/FinancialProductsView.vue";
import DepositDetailView from "@/features/products/pages/DepositDetailView.vue";
import SavingDetailView from "@/features/products/pages/SavingDetailView.vue";
import ProfileView from "@/features/accounts/pages/ProfileView.vue";
import ArticleDetailView from "@/features/articles/pages/ArticleDetailView.vue";
import ArticleUpdateView from "@/features/articles/pages/ArticleUpdateView.vue";
import ProfileUpdateView from "@/features/accounts/pages/ProfileUpdateView.vue";
import VideoDetailView from "@/features/search/pages/VideoDetailView.vue";

const routes = [
  { path: "/", name: "home", component: IndexView },

  { path: "/login", name: "login", component: LoginView },
  { path: "/registration", name: "registration", component: RegistrationView },
  { path: "/reset-password", name: "reset-password", component: ResetPasswordView },
  { path: "/reset-password-confirm/:uid/:token", name: "reset-password-confirm", component: ResetPasswordConfirmView },

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

    {
      path: '/financial-products/mortgages/:code',
      name: 'mortgage-detail',
      component: MortgageDetailView,
      props: true
    },
    {
      path: '/financial-products/jeonses/:code',
      name: 'jeonse-detail',
      component: JeonseDetailView,
      props: true
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