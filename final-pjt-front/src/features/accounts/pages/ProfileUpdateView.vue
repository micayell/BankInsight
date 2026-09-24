<template>
  <div class="profile-update-container my-5 p-4 shadow rounded bg-white">
    <h2 class="text-center mb-4">프로필 수정</h2>
    <div v-if="isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">사용자 정보를 불러오는 중입니다...</p>
    </div>
    <form @submit.prevent="submitUpdate" v-else-if="editableProfile">
      <div class="row">
        <div class="col-md-5 text-center mb-4 mb-md-0">
          <img :src="imagePreviewUrl || defaultProfileImageUrl" alt="프로필 미리보기" class="profile-img-preview rounded-circle img-thumbnail mb-3">
          <div class="mb-3">
            <label for="profile_img" class="form-label">프로필 이미지 변경</label>
            <input type="file" class="form-control form-control-sm" id="profile_img" @change="handleImageUpload" accept="image/*">
          </div>
          <div class="mb-3">
            <label for="nickname" class="form-label">닉네임</label>
            <input type="text" class="form-control" id="nickname" v-model="editableProfile.nickname" required>
          </div>
          <div class="mb-3">
            <label for="age" class="form-label">나이 (세)</label>
            <input type="number" class="form-control" id="age" v-model.number="editableProfile.age" min="0">
          </div>
        </div>

        <div class="col-md-7">
          <div class="mb-3">
            <label for="salary" class="form-label">연봉 (만원)</label>
            <input type="number" class="form-control" id="salary" v-model.number="editableProfile.salary" min="0">
          </div>
          <div class="mb-3">
            <label for="wealth" class="form-label">자산 (만원)</label>
            <input type="number" class="form-control" id="wealth" v-model.number="editableProfile.wealth" min="0">
          </div>
          <div class="mb-3">
            <label for="tendency" class="form-label">투자 성향</label>
            <select class="form-select" id="tendency" v-model.number="editableProfile.tendency">
              <option v-for="(text, value) in tendencyMapForUpdate" :key="value" :value="Number(value)">
                {{ text }}
              </option>
            </select>
            <div class="form-text">{{ tendencyDescription(editableProfile.tendency) }}</div>
          </div>
          <div class="mb-3">
            <label for="desirePeriod" class="form-label">희망 투자 기간 (개월)</label>
            <select class="form-select" id="desirePeriod" v-model.number="editableProfile.desirePeriod">
              <option value="6">6개월</option>
              <option value="12">12개월 (1년)</option>
              <option value="24">24개월 (2년)</option>
              <option value="36">36개월 (3년)</option>
              </select>
          </div>
        </div>
      </div>

      <hr class="my-4">
      
      <div class="d-grid gap-2 d-md-flex justify-content-md-end">
        <button type="button" class="btn btn-outline-secondary me-md-2" @click="cancelUpdate">취소</button>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          <i v-else class="bi bi-check-circle-fill me-2"></i>
          수정 완료
        </button>
      </div>
    </form>
    <div v-else class="alert alert-warning text-center">
      프로필 정보를 수정할 수 없습니다. 다시 시도해주세요.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/features/accounts/store/userStore';
import swal from 'sweetalert';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const editableProfile = ref(null); 
const imageFile = ref(null); 
const imagePreviewUrl = ref(null); 
const isLoading = ref(true);
const isSubmitting = ref(false);

const API_BASE_URL = 'http://127.0.0.1:8000';
const defaultProfileImageUrl = `${API_BASE_URL}/media/images/default_profile.png`;

const tendencyMapForUpdate = {
  0: '0: 원금 보존 최우선형', 1: '1: 원금 보존 추구형', 2: '2: 낮은 위험 선호형',
  3: '3: 위험 중립형', 4: '4: 약간의 위험 감수형', 5: '5: 시장 평균 수익 추구형',
  6: '6: 성장성 중시형', 7: '7: 고수익 추구형', 8: '8: 공격 투자형',
  9: '9: 초고위험/초고수익 추구형', 10: '10: 최고 위험 감수형'
};

const tendencyDescription = (value) => {
  const map = {
    0: '매우 안정적인 투자를 선호합니다.', 1: '안정적인 투자를 추구합니다.', 2: '다소 안정적인 투자를 선호합니다.',
    3: '위험과 수익의 균형을 중요시합니다.', 4: '약간의 위험을 감수하며 수익을 기대합니다.', 5: '시장 평균 수준의 위험과 수익을 기대합니다.',
    6: '성장 가능성이 높은 곳에 투자하는 것을 선호합니다.', 7: '높은 수익을 위해 상당한 위험을 감수할 수 있습니다.', 8: '매우 공격적인 투자를 통해 높은 수익을 추구합니다.',
    9: '최고의 수익을 위해 매우 높은 위험을 감수합니다.', 10: '극단적인 위험을 감수하며 최고의 수익을 목표합니다.'
  };
  return map[value] || '';
};


const loadUserProfile = async () => {
  isLoading.value = true;
  const username = route.params.username;
  if (userStore.isLogin && userStore.userInfo?.username === username) {
    try {
      await userStore.getProfile(username); 
      if (userStore.userProfile) {
        editableProfile.value = { ...userStore.userProfile }; 
        if (editableProfile.value.profile_img) {
            let path = editableProfile.value.profile_img;
            if (path.includes(API_BASE_URL)) { imagePreviewUrl.value = path; }
            else if (path.startsWith('/media/')) { imagePreviewUrl.value = `${API_BASE_URL}${path}`; }
            else if (path.startsWith('images/')) { imagePreviewUrl.value = `${API_BASE_URL}/media/${path}`; }
            else { imagePreviewUrl.value = `${API_BASE_URL}/media/${path}`; }
        } else {
            imagePreviewUrl.value = defaultProfileImageUrl;
        }
      } else {
        throw new Error("프로필 정보를 가져오지 못했습니다.");
      }
    } catch (error) {
      console.error("프로필 정보 로드 실패 (UpdateView):", error);
      swal("오류", "프로필 정보를 불러오는 데 실패했습니다. 다시 시도해주세요.", "error")
        .then(() => router.push({ name: 'profile', params: { username } }));
    }
  } else {
    swal("접근 불가", "자신의 프로필만 수정할 수 있습니다.", "warning")
      .then(() => router.push({ name: 'home' })); 
  }
  isLoading.value = false;
};

onMounted(() => {
  loadUserProfile();
});

watch(() => route.params.username, (newUsername) => {
  if (newUsername) {
    loadUserProfile();
  }
});

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    imageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreviewUrl.value = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    imageFile.value = null;
  }
};

const submitUpdate = async () => {
  if (!editableProfile.value) return;
  isSubmitting.value = true;

  const formData = new FormData();
  formData.append('nickname', editableProfile.value.nickname);
  formData.append('age', editableProfile.value.age);
  formData.append('salary', editableProfile.value.salary);
  formData.append('wealth', editableProfile.value.wealth);
  formData.append('tendency', editableProfile.value.tendency);
  formData.append('desirePeriod', editableProfile.value.desirePeriod);
  
  if (imageFile.value) {
    formData.append('profile_img', imageFile.value);
  }

  try {
    await userStore.updateProfile(formData, route.params.username);
    router.push({ name: 'profile', params: { username: route.params.username } });
  } catch (error) {
    console.error("프로필 업데이트 중 오류:", error);
  } finally {
    isSubmitting.value = false;
  }
};

const cancelUpdate = () => {
  router.back(); 
};

</script>

<style scoped>
.profile-update-container {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}
.profile-img-preview {
  width: 180px;
  height: 180px;
  object-fit: cover;
  border-radius: 50%;
  border: 3px solid #eee;
}
.form-label {
  font-weight: 500;
}
.form-text {
  font-size: 0.875rem;
  color: #6c757d;
}
</style>