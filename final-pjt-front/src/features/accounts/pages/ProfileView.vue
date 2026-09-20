<template>
  <div class="page-wrapper profile-view">
    <div class="content-container">
      <header class="page-section-header">
        <h1 class="title">마이 페이지</h1>
        <p class="subtitle">나의 금융 프로필과 관리 중인 상품을 확인하세요.</p>
      </header>

      <div class="row gy-4">
        <div class="col-lg-4">
          <div class="card card-custom h-100 profile-info-card">
            <div class="card-body text-center p-4">
              <div class="profile-image-wrapper mx-auto mb-4">
                <img :src="profileImageUrl" alt="프로필 이미지" class="profile-image" />
              </div>
              <h2 class="h4 font-weight-bold mb-1">{{ profile.nickname || profile.username }}님</h2>
              <p class="text-muted mb-4">{{ profile.email }}</p>

              <div class="profile-stats-grid mb-4">
                <div class="stat-item">
                  <div class="stat-label">투자 성향</div>
                  <div class="stat-value text-primary font-weight-bold">{{ getTendencyLabel(profile.tendency) }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">목표 기간</div>
                  <div class="stat-value font-weight-bold">{{ profile.desirePeriod }}년</div>
                </div>
              </div>
              
              <hr class="my-4 border-light" />
              
              <div class="profile-details text-start">
                <div class="detail-row">
                  <span class="detail-label">나이</span>
                  <span class="detail-data">{{ profile.age }} 세</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">연봉</span>
                  <span class="detail-data">{{ formatCurrency(profile.salary) }} 원</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">자산</span>
                  <span class="detail-data">{{ formatCurrency(profile.wealth) }} 원</span>
                </div>
              </div>

              <div class="mt-4 pt-2">
                 <button @click="goToUpdateProfile" class="btn btn-outline-primary w-100 btn-custom mb-2">
                   프로필 수정
                 </button>
                 <button @click="confirmDeleteAccount" class="btn btn-outline-danger w-100 btn-custom">
                   회원 탈퇴
                 </button>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="card card-custom h-100 liked-products-card">
            <div class="card-header bg-white border-bottom p-4 d-flex justify-content-between align-items-center">
              <h3 class="h5 mb-0 font-weight-bold text-dark">관심 상품 목록</h3>
              <span class="badge bg-primary rounded-pill px-3 py-2" v-if="likedProductsCount > 0">{{ likedProductsCount }}개</span>
            </div>
            <div class="card-body p-4">
              
              <div v-if="loadingProducts" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">관심 상품을 불러오는 중입니다.</p>
              </div>
              <div v-else-if="likedProductsError" class="alert alert-danger text-center">
                상품 정보를 불러오는 데 실패했습니다 ({{ likedProductsError }})
              </div>

              <div v-else-if="likedProductsCount > 0">
                <ul class="nav nav-tabs custom-tabs mb-4" id="likedProductsTab" role="tablist">
                  <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="deposit-tab" data-bs-toggle="tab" data-bs-target="#deposit-tab-pane" type="button" role="tab" aria-controls="deposit-tab-pane" aria-selected="true">
                      정기예금 <span class="badge bg-secondary ms-1">{{ likedDeposits.length }}</span>
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button class="nav-link" id="saving-tab" data-bs-toggle="tab" data-bs-target="#saving-tab-pane" type="button" role="tab" aria-controls="saving-tab-pane" aria-selected="false">
                      정기적금 <span class="badge bg-secondary ms-1">{{ likedSavings.length }}</span>
                    </button>
                  </li>
                </ul>

                <div class="tab-content" id="likedProductsTabContent">
                  <!-- 예금 탭 -->
                  <div class="tab-pane fade show active" id="deposit-tab-pane" role="tabpanel" aria-labelledby="deposit-tab" tabindex="0">
                    <div v-if="likedDeposits.length === 0" class="text-center text-muted py-4">
                      관심 있는 정기예금 상품이 없습니다.
                    </div>
                    <div class="row row-cols-1 row-cols-md-2 g-3" v-else>
                      <div v-for="product in likedDeposits" :key="product.fin_prdt_cd" class="col">
                         <div class="card h-100 mini-product-card shadow-sm border-0" @click="goToDepositDetail(product.fin_prdt_cd)" style="cursor: pointer;">
                            <div class="card-body p-3">
                              <p class="text-muted small mb-1">{{ product.kor_co_nm }}</p>
                              <h6 class="font-weight-bold mb-2 text-truncate" :title="product.fin_prdt_nm">{{ product.fin_prdt_nm }}</h6>
                              <div class="d-flex justify-content-between align-items-end mt-3">
                                <span class="badge bg-light text-dark border">정기예금</span>
                                <button class="btn btn-sm btn-outline-danger p-1 lh-1" @click.stop="toggleLikeDeposit(product.fin_prdt_cd)" title="관심 해제">
                                  <i class="bi bi-heart-fill"></i>
                                </button>
                              </div>
                            </div>
                         </div>
                      </div>
                    </div>
                  </div>

                  <!-- 적금 탭 -->
                  <div class="tab-pane fade" id="saving-tab-pane" role="tabpanel" aria-labelledby="saving-tab" tabindex="0">
                    <div v-if="likedSavings.length === 0" class="text-center text-muted py-4">
                      관심 있는 정기적금 상품이 없습니다.
                    </div>
                    <div class="row row-cols-1 row-cols-md-2 g-3" v-else>
                      <div v-for="product in likedSavings" :key="product.fin_prdt_cd" class="col">
                         <div class="card h-100 mini-product-card shadow-sm border-0" @click="goToSavingDetail(product.fin_prdt_cd)" style="cursor: pointer;">
                            <div class="card-body p-3">
                              <p class="text-muted small mb-1">{{ product.kor_co_nm }}</p>
                              <h6 class="font-weight-bold mb-2 text-truncate" :title="product.fin_prdt_nm">{{ product.fin_prdt_nm }}</h6>
                              <div class="d-flex justify-content-between align-items-end mt-3">
                                <span class="badge bg-light text-dark border">정기적금</span>
                                <button class="btn btn-sm btn-outline-danger p-1 lh-1" @click.stop="toggleLikeSaving(product.fin_prdt_cd)" title="관심 해제">
                                  <i class="bi bi-heart-fill"></i>
                                </button>
                              </div>
                            </div>
                         </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-5 empty-liked-state">
                <i class="bi bi-folder2-open display-4 text-light mb-3"></i>
                <p class="lead mb-2">아직 관심 목록에 담은 통장이 없습니다.</p>
                <p class="text-muted mb-4 small">다양한 금융 상품을 둘러보고 나에게 맞는 상품을 찾아보세요.</p>
                <button @click="goToFinancialProducts" class="btn btn-primary px-4 rounded-pill">금융 상품 탐색하기</button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/features/accounts/store/userStore.js';
import { useDepositStore } from '@/features/products/store/depositStore.js';
import { useSavingStore } from '@/features/products/store/savingStore.js';
import swal from 'sweetalert';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const depositStore = useDepositStore();
const savingStore = useSavingStore();

const username = route.params.username;
const profile = ref({});
const loadingProducts = ref(true);
const likedProductsError = ref(null);

const likedDeposits = ref([]);
const likedSavings = ref([]);

const fetchProfileAndProducts = async () => {
    loadingProducts.value = true;
    likedProductsError.value = null;
    try {
        const userInfo = await userStore.getUserInfo(username);
        profile.value = userInfo;

        if (userInfo.interest_deposit && userInfo.interest_deposit.length > 0) {
           await depositStore.fetchDeposits();
           likedDeposits.value = depositStore.deposits.filter(p => userInfo.interest_deposit.includes(p.fin_prdt_cd));
        } else {
           likedDeposits.value = [];
        }

        if (userInfo.interest_saving && userInfo.interest_saving.length > 0) {
           await savingStore.fetchSavings();
           likedSavings.value = savingStore.savings.filter(p => userInfo.interest_saving.includes(p.fin_prdt_cd));
        } else {
           likedSavings.value = [];
        }

    } catch (error) {
        console.error("프로필 및 상품 정보 로딩 싪패:", error);
        likedProductsError.value = "정보를 불러오는 데 실패했습니다.";
        swal("오류", "프로필 정보를 불러올 수 없습니다.", "error");
    } finally {
        loadingProducts.value = false;
    }
};

onMounted(() => {
    fetchProfileAndProducts();
});

const profileImageUrl = computed(() => {
  if (profile.value && profile.value.profile_img) {
    if (profile.value.profile_img.startsWith('http')) {
      return profile.value.profile_img;
    }
    return `http://127.0.0.1:8000${profile.value.profile_img}`;
  }
  return '/default_profile.png';
});

const getTendencyLabel = (value) => {
    const tendencies = {
        0: '위험 회피형',
        1: '안정 추구형',
        2: '위험 중립형',
        3: '적극 수익 추구형',
        4: '위험 선호형'
    };
    return tendencies[value] || '미설정';
}

const formatCurrency = (value) => {
  if (!value) return 0;
  return new Intl.NumberFormat('ko-KR').format(value);
};

const likedProductsCount = computed(() => likedDeposits.value.length + likedSavings.value.length);

const goToUpdateProfile = () => {
    router.push({ name: 'profile-edit', params: { username: profile.value.username } });
};

const goToFinancialProducts = () => {
    router.push({ name: 'financial-products' });
}

const goToDepositDetail = (code) => {
    router.push({ name: 'deposit-detail', params: { code } });
};

const goToSavingDetail = (code) => {
    router.push({ name: 'saving-detail', params: { code } });
};

const toggleLikeDeposit = async (code) => {
    try {
        await depositStore.likeDeposit(code);
        await fetchProfileAndProducts(); 
    } catch(e) {
    }
}
const toggleLikeSaving = async (code) => {
    try {
        await savingStore.likeSaving(code);
        await fetchProfileAndProducts();
    } catch(e) {
    }
}

const confirmDeleteAccount = () => {
    swal({
        title: "회원 탈퇴",
        text: "정말로 탈퇴하시겠습니까? 관련 데이터가 모두 삭제되며 복구할 수 없습니다.",
        icon: "warning",
        buttons: ["취소", "확인"],
        dangerMode: true,
    })
    .then((willDelete) => {
        if (willDelete) {
            userStore.deleteAccount(profile.value.username)
        }
    });
};
</script>

<style scoped>
/* ... (existing styles) ... */
.profile-view { }
</style>