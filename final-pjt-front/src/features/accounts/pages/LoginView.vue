<template>
  <div class="login-wrapper">
    <div class="login-card p-4 shadow-sm">
      <div class="text-center mb-4">
        <h1 class="app-logo">BankInsight</h1>
      </div>

      <form @submit.prevent="logIn">
        <div class="mb-3 input-group">
          <span class="input-group-text">
            <i class="bi bi-person-fill"></i>
          </span>
          <input
            type="text"
            class="form-control"
            v-model.trim="username"
            placeholder="아이디를 입력해주세요"
            required
          />
        </div>
        
        <div class="mb-3 input-group">
          <span class="input-group-text">
            <i class="bi bi-lock-fill"></i>
          </span>
          <input
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            v-model="password"
            placeholder="비밀번호를 입력해주세요"
            required
          />
          <span class="input-group-text password-toggle" @click="showPassword = !showPassword">
            <i :class="showPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill'"></i>
          </span>
        </div>
        <button type="submit" class="btn btn-danger w-100 mb-2">
          로그인
        </button>
        <button type="button" class="btn btn-outline-secondary w-100" @click="goToRegister">
          계정 만들기
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/features/accounts/store/userStore.js'
import swal from 'sweetalert'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)

const logIn = async () => {
  try {
    await userStore.loginUser({ username: username.value, password: password.value })
  } catch {
  }
}

const goToRegister = () => {
  router.push({ name: 'registration' })
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 16px;
}

.login-card {
  width: 100%;
  max-width: 360px;
  background: #fff;
  border-radius: 8px;
}

.app-logo {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.input-group-text {
  background: #fff;
  border: 1px solid #ddd;
  border-right: 0;
}
.form-control {
  border-left: 0;
  height: 48px;
}
.password-toggle {
  cursor: pointer;
  border: 1px solid #ddd;
  border-left: 0;
  background: #fff;
}

.form-control::placeholder {
  color: #888 !important;
  opacity: 1;
}

.form-control:focus {
  border-color: #E60012;
  box-shadow: none;
  outline: none;
}

.login-card .text-decoration-none {
  color: #666;
}
.login-card .text-decoration-none:hover {
  text-decoration: underline;
}

.btn-danger {
  border-radius: 4px;
}
.btn-outline-secondary {
  border-radius: 4px;
  border-color: #ddd;
  color: #333;
}

.form-range {
  accent-color: #E60012;
  height: 6px;
}
</style>
