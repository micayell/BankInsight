<template>
  <div class="reset-password-wrapper">
    <div class="reset-password-card">
      <div class="text-center mb-4">
        <h1 class="app-logo">BankInsight</h1>
        <p class="text-muted mt-2">비밀번호 찾기</p>
      </div>

      <div v-if="isSent" class="text-center py-4">
        <i class="bi bi-envelope-check text-success" style="font-size: 3rem;"></i>
        <h4 class="mt-3">이메일 발송 완료</h4>
        <p class="text-muted mt-2">
          {{ email }}으로 비밀번호 재설정 링크가 발송되었습니다.<br>
          이메일을 확인하여 비밀번호를 재설정해주세요.
        </p>
        <button class="btn btn-primary w-100 mt-4" @click="router.push({ name: 'login' })">
          로그인으로 돌아가기
        </button>
      </div>

      <form v-else @submit.prevent="requestPasswordReset">
        <p class="text-muted small mb-4">
          가입하신 이메일 주소를 입력하시면 비밀번호를 재설정할 수 있는 링크를 보내드립니다.
        </p>
        <div class="input-group mb-4">
          <span class="input-group-text">
            <i class="bi bi-envelope-fill"></i>
          </span>
          <input
            type="email"
            class="form-control"
            v-model.trim="email"
            placeholder="이메일을 입력해주세요"
            required
            :disabled="isSubmitting"
          />
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          링크 전송
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary w-100"
          @click="router.push({ name: 'login' })"
        >
          돌아가기
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '@/features/accounts/api/authApi.js';
import swal from 'sweetalert';

const router = useRouter();
const email = ref('');
const isSubmitting = ref(false);
const isSent = ref(false);

const requestPasswordReset = async () => {
  if (!email.value) return swal("알림", "이메일을 입력하세요.", "info");

  isSubmitting.value = true;
  try {
    await authApi.resetPassword(email.value);
    isSent.value = true;
  } catch (error) {
    console.error("비밀번호 재설정 이메일 전송 실패:", error);
    swal("발송 실패", "가입되지 않은 이메일이거나 서버 오류가 발생했습니다.", "error");
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.reset-password-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 16px;
}
.reset-password-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px 24px;
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
.form-control:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}
</style>