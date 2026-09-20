<template>
  <div class="app-wrapper">
    <header class="app-header sticky-top">
      <nav class="navbar navbar-expand-lg navbar-light">
        <div class="container-fluid">
          <RouterLink to="/" class="navbar-brand">
            <img :src="appLogo" alt="BankInsight Logo" class="app-logo-image" />
          </RouterLink>
          <button
            class="navbar-toggler"
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
            <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <RouterLink
                  to="/financial-products"
                  class="nav-link"
                  active-class="active"
                  >예금비교</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/spot" class="nav-link" active-class="active"
                  >현물상품</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/search" class="nav-link" active-class="active"
                  >종목검색</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/map" class="nav-link" active-class="active"
                  >은행지도</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink to="/article" class="nav-link" active-class="active"
                  >게시판</RouterLink
                >
              </li>
              <template v-if="userStore.isLogin">
                <li class="nav-item">
                  <RouterLink
                    :to="`/profile/${userStore.userInfo?.username}`"
                    class="nav-link"
                    >내 프로필</RouterLink
                  >
                </li>
                <li class="nav-item">
                  <RouterLink to="/" class="nav-link" @click.prevent="handleLogout"
                    >로그아웃</RouterLink
                  >
                </li>
                </template>
                <template v-if="!userStore.isLogin">
                <li class="nav-item">
                  <RouterLink
                    to="/registration"
                    class="nav-link"
                    active-class="active"
                    >회원가입</RouterLink
                  >
                </li>
                <li class="nav-item">
                  <RouterLink to="/login" class="nav-link" active-class="active"
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

    <footer class="app-footer bg-dark text-secondary py-4">
      <div class="container-fluid text-center">
        <p class="mb-0">
          &copy; {{ new Date().getFullYear() }} BankInsight. 모든 권리 보유.
        </p>
      </div>
    </footer>

    <Transition name="bounce">
      <div v-show="expand" class="chatbot-window shadow-lg">
        <ChatbotComponent />
      </div>
    </Transition>

    <div @click="toggleChatbot" class="chatbot-fab-button rounded-circle">
      <img :src="chatbotIcon" alt="Chatbot Icon" class="chatbot-fab-icon" />
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { RouterView, RouterLink, useRouter } from "vue-router";
import { useUserStore } from "@/features/accounts/store/userStore.js";
import ChatbotComponent from "@/features/chatbot/components/Chatbot.vue";
import swal from "sweetalert";

const appLogo = "/logo.png";
const chatbotIcon = "/chatbot3.png";

const userStore = useUserStore();
const router = useRouter();
const expand = ref(false);

const toggleChatbot = () => {
  expand.value = !expand.value;
};

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

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-image: url("/app_bg_subtle.png");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.app-header .navbar {
  background-color: #e8e8e8 !important; 
  border-bottom: 1px solid #d8d8d8; 
}

.app-logo-image {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.navbar-nav .nav-link {
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.5rem 0.75rem;
  color: #333;
}

.navbar-nav .nav-link:hover,
.navbar-nav .nav-link.active {
  color: #0056b3;
}

.main-page-content {
}

.app-footer {
  font-size: 0.85rem;
}

.chatbot-window {
  position: fixed;
  bottom: 130px;
  right: 30px;
  z-index: 1050;
  background-color: #ffffff;
  border-radius: 0.5rem;
  width: 400px;
  max-width: 90vw;
  height: 600px;
  max-height: 70vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid #dee2e6;
}

.chatbot-fab-button {
  position: fixed;
  bottom: 40px;
  right: 30px;
  z-index: 1050;
  width: 70px;
  height: 70px;
  cursor: pointer;
  transition: transform 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: center;
  align-items: center;
}
.chatbot-fab-button:hover {
  transform: scale(1.1) translateY(-2px);
}
.chatbot-fab-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.bounce-enter-active {
  animation: bounce-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.bounce-leave-active {
  animation: bounce-in 0.3s cubic-bezier(0.6, -0.28, 0.735, 0.045) reverse;
}
@keyframes bounce-in {
  0% {
    transform: scale(0) translateY(50px);
    opacity: 0;
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}
:root {
  --app-primary-color: #D93600; 
  --app-secondary-color: #007A87; 
  
  --app-text-dark: #212529;    
  --app-text-medium: #495057;  
  --app-text-light: #6c757d;   
  
  --app-background-primary: #FFFFFF; 
  --app-background-secondary: #f4f6f8; 
  
  --app-border-color: #dee2e6;  
  --app-border-radius: 0.25rem; 

  --app-font-sans-serif: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

body {
  font-family: var(--app-font-sans-serif);
  color: var(--app-text-dark);
  background-color: var(--app-background-primary);
  line-height: 1.6;
}


.page-wrapper {
  background-color: var(--app-background-secondary); 
  min-height: calc(100vh - 56px); 
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.content-container {
  width: 100%;
  max-width: 1140px; 
  margin-left: auto;
  margin-right: auto;
  padding-left: 15px;
  padding-right: 15px;
  background-color: var(--app-background-primary); 
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.075); 
  border-radius: var(--app-border-radius);
}

.page-section-header {
  text-align: center;
  padding: 2rem 0 1.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--app-border-color);
}

.page-section-header .title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--app-text-dark);
  margin-bottom: 0.5rem;
}

.page-section-header .subtitle {
  font-size: 1.1rem;
  color: var(--app-text-medium);
}

.btn-custom {
  font-family: var(--app-font-sans-serif);
  border-radius: var(--app-border-radius);
  padding: 0.6rem 1.2rem;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  border: 1px solid transparent;
}

.btn-custom-primary {
  background-color: var(--app-primary-color);
  border-color: var(--app-primary-color);
  color: var(--app-background-primary);
}
.btn-custom-primary:hover {
  background-color: #c03000; 
  border-color: #c03000;
  color: var(--app-background-primary);
}

.btn-custom-secondary {
  background-color: var(--app-secondary-color);
  border-color: var(--app-secondary-color);
  color: var(--app-background-primary);
}
.btn-custom-secondary:hover {
  background-color: #005f69; 
  border-color: #005f69;
  color: var(--app-background-primary);
}

.btn-custom-outline-dark {
  border-color: var(--app-text-dark);
  color: var(--app-text-dark);
}
.btn-custom-outline-dark:hover {
  background-color: var(--app-text-dark);
  color: var(--app-background-primary);
}
</style>