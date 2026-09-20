<template>
  <div class="signup-wrapper">
    <div class="signup-card">
      <div class="text-center mb-4">
        <h1 class="app-logo">BankInsight</h1>
      </div>
      <form @submit.prevent="signUp">
        <div class="input-group mb-3">
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

        <div class="input-group mb-3">
          <span class="input-group-text">
            <i class="bi bi-chat-left-text-fill"></i>
          </span>
          <input
            type="text"
            class="form-control"
            v-model.trim="nickname"
            placeholder="닉네임을 입력해주세요"
            required
          />
        </div>

        <div class="input-group mb-3">
          <span class="input-group-text">
            <i class="bi bi-lock-fill"></i>
          </span>
          <input
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            v-model.trim="password1"
            placeholder="비밀번호를 입력해주세요"
            required
          />
          <span
            class="input-group-text password-toggle"
            @click="showPassword = !showPassword"
          >
            <i
              :class="showPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill'"
            ></i>
          </span>
        </div>

        <div class="input-group mb-3">
          <span class="input-group-text">
            <i class="bi bi-lock-fill"></i>
          </span>
          <input
            :type="showPassword2 ? 'text' : 'password'"
            class="form-control"
            v-model.trim="password2"
            placeholder="비밀번호를 다시 입력해주세요"
            required
          />
          <span
            class="input-group-text password-toggle"
            @click="showPassword2 = !showPassword2"
          >
            <i
              :class="showPassword2 ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill'"
            ></i>
          </span>
        </div>

        <div class="row gx-2 mb-3">
          <div class="col-6 input-group">
            <span class="input-group-text">
              <i class="bi bi-calendar-fill"></i>
            </span>
            <input
              type="number"
              class="form-control"
              v-model.number="age"
              placeholder="나이를 입력해주세요"
              required
            />
          </div>
        </div>
        <div class="row gx-2 mb-3">
          <div class="col-6 input-group">
            <span class="input-group-text">
              <i class="bi bi-clock-fill"></i>
            </span>
            <input
              type="number"
              class="form-control"
              v-model.number="desirePeriod"
              placeholder="예치 기간(개월)"
            />
          </div>
        </div>
        <div class="row gx-2 mb-3">
          <div class="col-6 input-group">
            <span class="input-group-text">
              <i class="bi bi-currency-won"></i>
            </span>
            <input
              type="number"
              class="form-control"
              v-model.number="salary"
              placeholder="연봉(만원)"
            />
          </div>
        </div>
        <div class="row gx-2 mb-3">
          <div class="col-6 input-group">
            <span class="input-group-text">
              <i class="bi bi-piggy-bank-fill"></i>
            </span>
            <input
              type="number"
              class="form-control"
              v-model.number="wealth"
              placeholder="자산(만원)"
            />
          </div>
        </div>
        <div class="mb-4">
          <label class="form-label">투자 성향 (1:안정 ~ 10:공격)</label>
          <input
            type="range"
            class="form-range"
            v-model.number="tendency"
            min="1"
            max="10"
          />
          <div class="text-end text-muted small">현재: {{ tendency }}</div>
        </div>
        <button type="submit" class="btn btn-danger w-100 mb-2">
          가입하기
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary w-100"
          @click="router.push({ name: 'login' })"
        >
          로그인으로 이동
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/features/accounts/store/userStore.js";
import swal from "sweetalert";

const router = useRouter();
const userStore = useUserStore();

const username = ref("");
const nickname = ref("");
const password1 = ref("");
const password2 = ref("");
const showPassword = ref(false);
const showPassword2 = ref(false);
const age = ref(null);
const salary = ref(null);
const wealth = ref(null);
const tendency = ref(5);
const desirePeriod = ref(null);

const signUp = async () => {
  if (password1.value !== password2.value) {
    return swal("오류", "비밀번호가 일치하지 않습니다.", "error");
  }
  try {
    await userStore.createUser({
      username: username.value,
      nickname: nickname.value,
      password1: password1.value,
      password2: password2.value,
      age: age.value,
      salary: salary.value,
      wealth: wealth.value,
      tendency: tendency.value,
      desirePeriod: desirePeriod.value,
    });
    await swal("회원가입 성공!", "로그인 페이지로 이동합니다.", "success");
    router.push({ name: "login" });
  } catch {
  }
};
</script>

<style scoped>
.signup-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 16px;
}

.signup-card {
  width: 100%;
  max-width: 360px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.app-logo {
  font-family: "Noto Sans KR", sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.input-group-text {
  background: #fff;
  border: 1px solid #ddd;
}

.form-control {
  border-left: 0;
  height: 48px;
}

.password-toggle {
  cursor: pointer;
}
</style>
