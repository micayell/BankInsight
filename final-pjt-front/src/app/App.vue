<template>
  <div class="app-wrapper">
    <header class="app-header sticky-top bg-white">
      <nav class="navbar navbar-expand-lg navbar-light">
        <div class="container-fluid px-4 px-lg-5">
          <RouterLink to="/" class="navbar-brand py-2">
            <img :src="appLogo" alt="BankInsight Logo" class="app-logo-image" />
          </RouterLink>
          <button
            class="navbar-toggler border-0 shadow-none"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNavDropdown"
            aria-controls="navbarNavDropdown"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNavDropdown">
            <ul class="navbar-nav ms-auto mb-2 mb-lg-0 gap-2">
              <li class="nav-item">
                <RouterLink
                  to="/financial-products"
                  class="nav-link fs-6"
                  active-class="active"
                  >금융상품</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/spot" class="nav-link fs-6" active-class="active"
                  >환율상품</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/search" class="nav-link fs-6" active-class="active"
                  >종목검색</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/map" class="nav-link fs-6" active-class="active"
                  >영업점찾기</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/article" class="nav-link fs-6" active-class="active"
                  >게시판</RouterLink
                >
              </li>
              <template v-if="userStore.isLogin">
                <li class="nav-item">
                  <RouterLink
                    :to="`/profile/${userStore.userInfo?.username}`"
                    class="nav-link fs-6"
                    active-class="active"
                    >마이프로필</RouterLink
                  >
                </li>
                <li class="nav-item">
                  <a href="#" class="nav-link fs-6" @click.prevent="handleLogout"
                    >로그아웃</a
                  >
                </li>
              </template>
              <template v-if="!userStore.isLogin">
                <li class="nav-item">
                  <RouterLink
                    to="/registration"
                    class="nav-link fs-6"
                    active-class="active"
                    >회원가입</RouterLink
                  >
                </li>
                <li class="nav-item">
                  <RouterLink to="/login" class="nav-link fs-6" active-class="active"
                    >로그인</RouterLink
                  >
                </li>
              </template>
            </ul>
          </div>
        </div>
      </nav>
    </header>

    <main class="main-page-content flex-grow-1">
      <RouterView />
    </main>

    <footer class="app-footer text-secondary py-5">
      <div class="container-fluid text-center">
        <p class="mb-0 text-muted fw-medium font-monospace">
          &copy; {{ new Date().getFullYear() }} BankInsight. All rights reserved.
        </p>
      </div>
    </footer>

    <Transition name="bounce">
      <div v-show="expand" ref="chatbotWindowRef" class="chatbot-window shadow-lg border-0 rounded-4">
        <ChatbotComponent />
      </div>
    </Transition>

    <div @click="toggleChatbot" ref="chatbotFabRef" class="chatbot-fab-button rounded-circle">
      <img :src="chatbotIcon" alt="Chatbot Icon" class="chatbot-fab-icon" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { RouterView, RouterLink, useRouter } from "vue-router";
import { useUserStore } from "@/features/accounts/store/userStore.js";
import ChatbotComponent from "@/features/chatbot/components/Chatbot.vue";
import swal from "sweetalert";

const appLogo = "/logo.png";
const chatbotIcon = "/chatbot3.png";

const userStore = useUserStore();
const router = useRouter();
const expand = ref(false);

const chatbotWindowRef = ref(null);
const chatbotFabRef = ref(null);

const toggleChatbot = () => {
  expand.value = !expand.value;
};

// 챗봇 바깥 클릭 시 닫기
const closeChatbotOnOutsideClick = (event) => {
  if (
    expand.value &&
    chatbotWindowRef.value &&
    !chatbotWindowRef.value.contains(event.target) &&
    chatbotFabRef.value &&
    !chatbotFabRef.value.contains(event.target)
  ) {
    expand.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', closeChatbotOnOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener('click', closeChatbotOnOutsideClick);
});

const handleLogout = () => {
  swal({
    title: "로그아웃",
    text: "정말로 로그아웃 하시겠습니까?",
    icon: "warning",
    buttons: ["취소", "확인"],
    dangerMode: true,
  }).then((willLogout) => {
    if (willLogout) {
      userStore.logoutUser();
    }
  });
};
</script>

<style>
/* CSS RESET AND TOSS DESIGN SYSTEM STYLES */
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css");

:root {
  --toss-blue: #3182f6;
  --toss-blue-hover: #1b64da;
  --toss-bg: #f9fafb;
  --toss-card-bg: #ffffff;
  --toss-text-dark: #191f28;
  --toss-text-medium: #4e5968;
  --toss-text-light: #8b95a1;
  --toss-border: #f2f4f6;
  --toss-border-dark: #e5e8eb;
  --toss-radius: 16px;
  --toss-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  --toss-shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.08);
}

body {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: var(--toss-text-dark);
  background-color: var(--toss-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Button Globally Override to Toss Style */
.btn-primary {
  background-color: var(--toss-blue) !important;
  border-color: var(--toss-blue) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  padding: 0.6rem 1.2rem !important;
}

.btn-primary:hover, .btn-primary:active {
  background-color: var(--toss-blue-hover) !important;
  border-color: var(--toss-blue-hover) !important;
}

/* Cards Globally Override to Toss Style */
.card {
  background-color: var(--toss-card-bg);
  border-radius: var(--toss-radius) !important;
  border: 1px solid var(--toss-border) !important;
  box-shadow: var(--toss-shadow) !important;
}
</style>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  box-shadow: 0 1px 0 0 rgba(0, 0, 0, 0.04);
}

.app-logo-image {
  height: 28px;
  width: auto;
  object-fit: contain;
}

.navbar-nav .nav-link {
  font-weight: 500;
  color: var(--toss-text-medium);
  border-radius: 8px;
  padding: 0.5rem 1rem !important;
  transition: all 0.2s;
}

.navbar-nav .nav-link:hover {
  background-color: #f2f4f6;
  color: var(--toss-text-dark);
}

.navbar-nav .nav-link.active {
  color: var(--toss-blue);
  font-weight: 600;
}

.app-footer {
  background-color: var(--toss-bg);
  border-top: 1px solid var(--toss-border-dark);
}

/* Chatbot Styles */
.chatbot-window {
  position: fixed;
  bottom: 130px;
  right: 30px;
  z-index: 1050;
  background-color: #ffffff;
  width: 400px;
  max-width: 90vw;
  height: 600px;
  max-height: 70vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chatbot-fab-button {
  position: fixed;
  bottom: 40px;
  right: 30px;
  z-index: 1050;
  width: 65px;
  height: 65px;
  cursor: pointer;
  transition: transform 0.3s ease;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
}
.chatbot-fab-button:hover {
  transform: scale(1.05) translateY(-2px);
}
.chatbot-fab-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.bounce-enter-active {
  animation: bounce-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.bounce-leave-active {
  animation: bounce-in 0.25s cubic-bezier(0.6, -0.28, 0.735, 0.045) reverse;
}
@keyframes bounce-in {
  0% {
    transform: scale(0.8) translateY(20px);
    opacity: 0;
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}
</style>
