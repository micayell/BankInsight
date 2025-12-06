<template>
  <div class="page-wrapper">
    <div class="content-container profile-view">
      <header class="page-section-header pb-3 mb-4 border-bottom">
        <div>
          <h1 class="h4 mb-0">마이 프로필</h1>
          <p class="text-muted mb-0 mt-1 subtitle-text">회원님의 정보를 확인하고 관리하세요.</p>
        </div>
      </header>

      <div v-if="!userStore.userProfile && userStore.loading" class="loading-indicator-kia text-center py-5">
        <div class="spinner-border" role="status" :style="{ color: 'var(--app-primary-color)' }">
          <span class="visually-hidden">프로필 정보를 불러오는 중...</span>
        </div>
        <p class="mt-3" :style="{ color: 'var(--app-text-medium)' }">프로필 정보를 불러오고 있습니다.</p>
      </div>
      <div v-else-if="!userStore.userProfile && !userStore.loading" class="alert alert-warning text-center my-5" role="alert">
        프로필 정보를 불러올 수 없습니다. 다시 로그인 해주세요.
      </div>
      
      <div v-else class="profile-layout py-md-4 py-3"> 
        <div class="row g-lg-5 g-4 justify-content-center">
          <div class="col-lg-4 col-md-5">
            <div class="card-kia profile-summary-card text-center p-4">
              <img 
                :src="profileImageUrl" 
                alt="프로필 이미지" 
                class="profile-image-lg mb-3"
              />
              <h2 class="profile-nickname-lg mb-1">{{ userStore.userProfile.nickname }}</h2>
              <p class="profile-username-md mb-4">{{ userStore.userProfile.username }}</p>
              
              <div v-if="isMyProfile" class="d-grid gap-2">
                <button class="btn btn-profile-edit-custom" @click="goToProfileEdit">
                  <i class="bi bi-pencil-square me-2"></i> 프로필 수정
                </button>
                <button class="btn btn-outline-danger" @click="confirmDeleteAccount">
                  <i class="bi bi-trash3 me-2"></i> 회원 탈퇴
                </button>
              </div>
            </div>
          </div>

          <div class="col-lg-8 col-md-7">
            <div class="card-kia profile-details-card">
              <div class="card-header profile-tabs-header">
                <ul class="nav nav-tabs nav-fill">
                  <li class="nav-item">
                    <a class="nav-link" :class="{ active: activeTab === 'info' }" @click.prevent="activeTab = 'info'" href="#">기본 정보</a>
                  </li>
                  <li class="nav-item">
                    <a class="nav-link" :class="{ active: activeTab === 'financial' }" @click.prevent="activeTab = 'financial'" href="#">나의 금융 정보</a>
                  </li>
                  <li class="nav-item">
                    <a class="nav-link" :class="{ active: activeTab === 'liked_products' }" @click.prevent="activeTab = 'liked_products'" href="#">관심 상품</a>
                  </li>
                </ul>
              </div>
              <div class="card-body p-sm-4 p-3"> 
                <div v-if="activeTab === 'info'" class="tab-content-section">
                  <h3 class="tab-section-title">계정 정보</h3>
                  <ul class="info-list-custom">
                    <li>
                      <span>이메일</span>
                      <strong>{{ userStore.userProfile.email || '미제공' }}</strong>
                    </li>
                    <li>
                      <span>나이</span>
                      <strong>{{ userStore.userProfile.age }} 세</strong>
                    </li>
                  </ul>
                </div>

                <div v-if="activeTab === 'financial'" class="tab-content-section">
                  <h3 class="tab-section-title">나의 금융 스타일</h3>
                  <ul class="info-list-custom">
                    <li>
                      <span>연봉</span>
                      <strong>{{ formatCurrency(userStore.userProfile.salary) }} 만원</strong>
                    </li>
                    <li>
                      <span>자산</span>
                      <strong>{{ formatCurrency(userStore.userProfile.wealth) }} 만원</strong>
                    </li>
                    <li>
                      <span>투자 성향</span>
                      <strong :style="{ color: getTendencyDisplay(userStore.userProfile.tendency).color }">
                        {{ getTendencyDisplay(userStore.userProfile.tendency).text }}
                      </strong>
                    </li>
                    <li>
                      <span>희망 투자 기간</span>
                      <strong>{{ userStore.userProfile.desirePeriod }} 개월</strong>
                    </li>
                  </ul>
                </div>
                
                <div v-if="activeTab === 'liked_products'" class="tab-content-section">
                  <div class="mb-4">
                    <h3 class="tab-section-title">관심 예금 상품</h3>
                    <div v-if="userStore.userProfile.interested_deposits && userStore.userProfile.interested_deposits.length > 0">
                      <ul class="product-link-list-custom">
                        <li v-for="item in userStore.userProfile.interested_deposits" :key="'dep-' + item.fin_prdt_cd" @click="goToProductDetail('deposit', item.fin_prdt_cd)" class="d-flex align-items-center justify-content-between">
                          <div class="d-flex align-items-center">
                            <img v-if="item.logoUrl" :src="item.logoUrl" :alt="`${item.kor_co_nm} 로고`" class="bank-logo-profile me-3">
                            <div class="product-info-profile">
                              <span class="product-name-profile">{{ item.fin_prdt_nm }}</span> 
                              <small class="text-muted d-block product-bank-profile">({{ item.kor_co_nm }})</small>
                            </div>
                          </div>
                          <small class="product-interest-rate text-nowrap">{{ getInterestRateRange(item.options) }}</small>
                        </li>
                      </ul>
                    </div>
                    <p v-else class="text-center text-muted p-3">관심 예금 상품이 없습니다.</p>
                  </div>
                  <div>
                    <h3 class="tab-section-title">관심 적금 상품</h3>
                    <div v-if="userStore.userProfile.interested_savings && userStore.userProfile.interested_savings.length > 0">
                      <ul class="product-link-list-custom">
                        <li v-for="item in userStore.userProfile.interested_savings" :key="'sav-' + item.fin_prdt_cd" @click="goToProductDetail('saving', item.fin_prdt_cd)" class="d-flex align-items-center justify-content-between">
                          <div class="d-flex align-items-center">
                            <img v-if="item.logoUrl" :src="item.logoUrl" :alt="`${item.kor_co_nm} 로고`" class="bank-logo-profile me-3">
                            <div class="product-info-profile">
                              <span class="product-name-profile">{{ item.fin_prdt_nm }}</span> 
                              <small class="text-muted d-block product-bank-profile">({{ item.kor_co_nm }})</small>
                            </div>
                          </div>
                          <small class="product-interest-rate text-nowrap">{{ getInterestRateRange(item.options) }}</small>
                        </li>
                      </ul>
                    </div>
                    <p v-else class="text-center text-muted p-3">관심 적금 상품이 없습니다.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useUserStore } from '@/stores/userStore';
import { useRouter, useRoute } from 'vue-router';
import swal from 'sweetalert';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

const activeTab = ref('info');
const profileUsername = ref(route.params.username);

const tendencyDetails = { 
  0: { text: '원금 보존 최우선형', color: '#2E7D32' },
  1: { text: '원금 보존 추구형', color: '#4CAF50' },
  2: { text: '낮은 위험 선호형', color: '#8BC34A' },
  3: { text: '위험 중립형', color: '#FBC02D' },
  4: { text: '약간의 위험 감수형', color: '#FF9800' },
  5: { text: '시장 평균 수익 추구형', color: '#FB8C00' },
  6: { text: '성장성 중시형', color: '#F57C00' },
  7: { text: '고수익 추구형', color: '#E65100' },
  8: { text: '공격투자형', color: '#D84315' },
  9: { text: '초고위험/초고수익 추구형', color: '#BF360C' },
  10: { text: '최고 위험 감수형', color: '#B71C1C' },
};
const defaultTendency = { text: '미설정', color: 'var(--app-text-medium)' };

const getTendencyDisplay = (tendencyValue) => {
  return tendencyDetails[tendencyValue] || defaultTendency;
};

const profileImageUrl = computed(() => {
  const profile = userStore.userProfile;
  if (profile && profile.profile_img) {
    if (profile.profile_img.startsWith('/media/') || profile.profile_img.startsWith('images/')) {
      const baseUrl = userStore.API_URL || 'http://127.0.0.1:8000';
      return `${baseUrl}${profile.profile_img.startsWith('/') ? '' : '/'}${profile.profile_img}`;
    }
    return profile.profile_img;
  }
  try {
    return new URL('@/assets/default_profile.png', import.meta.url).href;
  } catch (e) {
    return '/src/assets/default_profile.png'; 
  }
});

const isMyProfile = computed(() => {
  return userStore.isLogin && userStore.userInfo?.username === profileUsername.value;
});

const loadProfileData = async () => {
  if (profileUsername.value) {
    try {
      await userStore.getProfile(profileUsername.value);
    } catch (error) {
      console.error("ProfileView: 프로필 데이터 로드 중 에러:", error);
      if (error.response && (error.response.status === 401 || error.response.status === 403 || error.response.status === 404)) {
        swal("오류", "프로필 정보를 가져오는데 실패했거나 권한이 없습니다.", "error")
          .then(() => router.push({ name: 'login' }));
      } else {
        swal("오류", "프로필 정보를 가져오는 중 문제가 발생했습니다.", "error");
      }
    }
  }
};

onMounted(loadProfileData);

watch(() => route.params.username, (newUsername) => {
  if (newUsername && newUsername !== profileUsername.value) {
    profileUsername.value = newUsername;
    activeTab.value = 'info';
    loadProfileData();
  }
});

const goToProfileEdit = () => {
  router.push({ name: 'profile-edit', params: { username: profileUsername.value } });
};

const confirmDeleteAccount = () => {
  swal({
    title: "정말로 계정을 삭제하시겠습니까?",
    text: "삭제된 계정 정보는 복구할 수 없습니다. 이 작업은 되돌릴 수 없습니다.",
    icon: "warning",
    buttons: {
      cancel: { text: "취소", value: null, visible: true, closeModal: true },
      confirm: { text: "삭제", value: true, visible: true, className: "btn-danger-swal", closeModal: true }
    },
    dangerMode: true,
  })
  .then(async (willDelete) => {
    if (willDelete) {
      try {
        userStore.logout();
        await userStore.api.delete(`/accounts/user/delete/${profileUsername.value}/`);
        swal("삭제 완료", "계정이 성공적으로 삭제되었습니다. 이용해주셔서 감사합니다.", "success")
          .then(() => {
          });
      } catch (error) {
        console.error("회원 탈퇴 실패:", error.response?.data || error.message);
        swal("탈퇴 실패", `회원 탈퇴 처리 중 오류가 발생했습니다: ${error.response?.data?.error || error.message}`, "error");
      }
    }
  });
};

const formatCurrency = (value) => {
  if (value == null || isNaN(Number(value))) return '0';
  return Number(value).toLocaleString();
};

const goToProductDetail = (type, code) => {
  const routeName = type === 'deposit' ? 'deposit-detail' : 'saving-detail';
  router.push({ name: routeName, params: { code } });
};

const getInterestRateRange = (options) => {
  if (!options || options.length === 0) return '정보 없음';
  let minRate = Infinity;
  let maxRate = -Infinity;
  let hasRates = false;

  options.forEach(opt => {
    const rate1 = parseFloat(opt.intr_rate);
    const rate2 = parseFloat(opt.intr_rate2);

    if (!isNaN(rate1)) {
      minRate = Math.min(minRate, rate1);
      maxRate = Math.max(maxRate, rate1);
      hasRates = true;
    }
    if (!isNaN(rate2)) {
      maxRate = Math.max(maxRate, rate2);
      if (isNaN(rate1) || rate1 === null) { 
          minRate = Math.min(minRate, rate2);
      }
      hasRates = true;
    }
  });

  if (!hasRates || (minRate === Infinity && maxRate === -Infinity)) return '정보 없음';
  
  if (minRate === Infinity) minRate = maxRate;
  if (maxRate === -Infinity) maxRate = minRate;

  if (minRate === maxRate) {
    return `${maxRate.toFixed(2)}%`;
  }
  return `${minRate.toFixed(2)}% ~ ${maxRate.toFixed(2)}%`;
};

</script>

<style scoped>
.profile-view {
  background-color: var(--app-background-secondary, #f8f9fa);
  padding: 1.5rem;
  min-height: calc(100vh - 56px - 70px); 
}

.page-section-header {
  text-align: left;
}
.page-section-header .subtitle-text {
  font-size: 0.9rem;
}

.card-kia {
  background-color: var(--app-background-primary, #fff); 
  border: 1px solid var(--app-border-color, #dee2e6); 
  box-shadow: 0 1px 3px rgba(0,0,0,0.04); 
  border-radius: var(--app-border-radius); 
}

.profile-image-lg {
  width: 120px; 
  height: 120px;
  object-fit: cover;
  border-radius: 50%;
  border: 3px solid var(--app-background-primary, #fff); 
  box-shadow: 0 2px 6px rgba(0,0,0,0.08); 
  margin-left: auto;
  margin-right: auto;
}
.profile-nickname-lg {
  font-size: 1.4rem; 
  font-weight: 600;
  color: var(--app-text-dark);
}
.profile-username-md {
  font-size: 0.85rem; 
  color: var(--app-text-medium);
}

.profile-summary-card .btn {
  font-family: var(--app-font-sans-serif);
  border-radius: var(--app-border-radius);
  padding: 0.6rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out, color 0.2s ease-in-out;
}

.btn-profile-edit-custom {
  background-color: transparent;
  border: 1px solid var(--app-text-dark, #212529); 
  color: var(--app-text-dark, #212529);           
}
.btn-profile-edit-custom:hover {
  background-color: var(--app-primary-color,#212529);      
  border-color: var(--app-primary-color,#212529);          
  color: var(--app-background-primary, #fff);      
}


.profile-summary-card .btn-outline-danger {
  /* 부트스트랩 기본 스타일 활용 */
}


.profile-tabs-header {
  background-color: transparent; 
  padding: 0; 
  border-bottom: 1px solid var(--app-border-color);
}

.profile-tabs-header .nav-tabs {
  border-bottom: none;
}
.profile-tabs-header .nav-item .nav-link {
  color: var(--app-text-medium);
  border: none;
  border-bottom: 3px solid transparent; 
  padding: 0.75rem 1rem; 
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s, border-color 0.2s;
  text-align: center;
}
.profile-tabs-header .nav-item .nav-link.active {
  color: var(--app-primary-color);
  border-bottom-color: var(--app-primary-color);
  font-weight: 600; 
}
.profile-tabs-header .nav-item .nav-link:hover:not(.active) {
  color: var(--app-text-dark);
  border-bottom-color: var(--app-border-color-light, var(--app-border-color));
}

.tab-content-section {
  padding-top: 1.5rem; 
}
.tab-section-title {
  font-size: 1.1rem; 
  font-weight: 600;
  color: var(--app-text-dark);
  margin-bottom: 1.25rem; 
  padding-bottom: 0.75rem; 
  border-bottom: 1px solid var(--app-border-color-lighter, #f0f0f0);
}

.info-list-custom {
  list-style: none;
  padding-left: 0;
  font-size: 0.9rem; 
}
.info-list-custom li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0.25rem; 
  border-bottom: 1px solid var(--app-border-color-lighter, #f0f0f0); 
}
.info-list-custom li:last-child {
  border-bottom: none;
}
.info-list-custom li span { 
  color: var(--app-text-medium);
  margin-right: 1rem; 
}
.info-list-custom li strong { 
  color: var(--app-text-dark);
  font-weight: 500;
  text-align: right;
}

.product-link-list-custom {
  list-style: none;
  padding-left: 0;
}
.product-link-list-custom li {
  padding: 0.85rem 0.25rem; 
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid var(--app-border-color-lighter, #f0f0f0); 
  display: flex;
  align-items: center; 
  justify-content: space-between;
}
.product-link-list-custom li:last-child {
  border-bottom: none;
}
.product-link-list-custom li:hover { 
  background-color: var(--app-background-secondary, #f8f9fa);
}
.product-info-profile {
  display: flex;
  flex-direction: column;
}
.product-name-profile {
  font-size: 1.05rem;
  color: var(--app-text-dark);
  font-weight: 500;
  line-height: 1.3;
}
.product-bank-profile {
  font-size: 0.9rem;
  line-height: 1.2;
}
.product-link-list-custom li:hover .product-name-profile { 
  color: var(--app-primary-color);
}

.bank-logo-profile {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 6px;
  background-color: #fff;
  border: 1px solid #e9ecef;
  padding: 2px;
}
.product-interest-rate {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--app-primary-color);
  margin-left: 1rem;
}
</style>