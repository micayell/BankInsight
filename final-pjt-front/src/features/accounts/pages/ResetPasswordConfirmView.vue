<template>
  <div class="reset-confirm-wrapper">
    <div class="reset-confirm-card">
      <div class="text-center mb-4">
        <h1 class="app-logo">BankInsight</h1>
        <p class="text-muted mt-2">새로운 비밀번호 설정</p>
      </div>

      <div v-if="isSuccess" class="text-center py-4">
        <i class="bi bi-check-circle-fill text-success" style="font-size: 3rem;"></i>
        <h4 class="mt-3">비밀번호 변경 완료</h4>
        <p class="text-muted mt-2">비밀번호가 성공적으로 재설정되었습니다.<br>새로운 비밀번호로 로그인해주세요.</p>
        <button class="btn btn-primary w-100 mt-4" @click="router.push({ name: 'login' })">
          로그인하러 가기
        </button>
      </div>

      <form v-else @submit.prevent="submitNewPassword">
        <div class="input-group mb-3">
          <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
          <input
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            v-model.trim="newPassword1"
            placeholder="새 비밀번호 입력"
            required
            :disabled="isSubmitting"
          />
          <span class="input-group-text password-toggle" @click="showPassword = !showPassword">
            <i :class="showPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill'"></i>
          </span>
        </div>

        <div class="input-group mb-4">
          <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
          <input
            :type="showPassword2 ? 'text' : 'password'"
            class="form-control"
            v-model.trim="newPassword2"
            placeholder="새 비밀번호 확인"
            required
            :disabled="isSubmitting"
          />
          <span class="input-group-text password-toggle" @click="showPassword2 = !showPassword2">
            <i :class="showPassword2 ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill'"></i>
          </span>
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          비밀번호 변경하기
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { authApi } from '@/features/accounts/api/authApi.js';
import swal from 'sweetalert';

const route = useRoute();
const router = useRouter();

const newPassword1 = ref('');
const newPassword2 = ref('');
const showPassword = ref(false);
const showPassword2 = ref(false);
const isSubmitting = ref(false);
const isSuccess = ref(false);

const submitNewPassword = async () => {
  if (newPassword1.value !== newPassword2.value) {
    return swal("오류", "비밀번호가 일치하지 않습니다.", "error");
  }

  isSubmitting.value = true;
  try {
    await authApi.resetPasswordConfirm({
      uid: route.params.uid,
      token: route.params.token,
      new_password1: newPassword1.value,
      new_password2: newPassword2.value,
    });
    isSuccess.value = true;
  } catch (error) {
    console.error("비밀번호 재설정 실패:", error);
    swal("변경 실패", "유효하지 않거나 만료된 링크입니다. 다시 요청해주세요.", "error");
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.reset-confirm-wrapper { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f5f5f5; padding: 16px; }
.reset-confirm-card { width: 100%; max-width: 400px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); padding: 32px 24px; }
.app-logo { font-family: "Noto Sans KR", sans-serif; font-size: 1.75rem; font-weight: 700; color: #333; margin: 0; }
.input-group-text { background: #fff; border: 1px solid #ddd; }
.form-control { border-left: 0; height: 48px; }
.password-toggle { cursor: pointer; }
</style>