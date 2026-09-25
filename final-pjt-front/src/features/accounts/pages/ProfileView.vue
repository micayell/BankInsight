<template>
  <div class="page-wrapper profile-view">
    <div class="content-container">
      <header class="page-section-header">
        <h1 class="title">마이 페이지</h1>
        <p class="subtitle">나의 금융 프로필과 관심 중인 상품을 확인하세요</p>
      </header>

      <div class="row gy-4">
        <div class="col-lg-4">
          <div class="card bg-white border-0 shadow-sm rounded-4 h-100">
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
                  <div class="stat-value font-weight-bold">{{ profile.desirePeriod }}개월</div>
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
                  <span class="detail-data">{{ formatCurrency(profile.salary) }} 만원</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">자산</span>
                  <span class="detail-data">{{ formatCurrency(profile.wealth) }} 만원</span>
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
              <h3 class="h5 mb-0 font-weight-bold text-dark">관심 항목 목록</h3>
              <span class="badge bg-primary rounded-pill px-3 py-2" v-if="likedProductsCount > 0">{{ likedProductsCount }}개</span>
            </div>
            <div class="card-body p-4">
              
              <div v-if="loadingProducts" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">관심 항목을 불러오는 중입니다.</p>
              </div>
              <div v-else-if="likedProductsError" class="alert alert-danger text-center">
                정보를 불러오는 데 실패했습니다 ({{ likedProductsError }})
              </div>

              <div v-else-if="likedProductsCount > 0">
                <ul class="nav nav-tabs nav-pills mb-4 gap-2" id="likedProductsTab" role="tablist">
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
                  <li class="nav-item" role="presentation">
                    <button class="nav-link" id="mortgage-tab" data-bs-toggle="tab" data-bs-target="#mortgage-tab-pane" type="button" role="tab" aria-controls="mortgage-tab-pane" aria-selected="false">
                      주택담보대출<span class="badge bg-secondary ms-1">{{ likedMortgages.length }}</span>
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button class="nav-link" id="jeonse-tab" data-bs-toggle="tab" data-bs-target="#jeonse-tab-pane" type="button" role="tab" aria-controls="jeonse-tab-pane" aria-selected="false">
                      전세금대출<span class="badge bg-secondary ms-1">{{ likedJeonses.length }}</span>
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button class="nav-link" id="bank-tab" data-bs-toggle="tab" data-bs-target="#bank-tab-pane" type="button" role="tab" aria-controls="bank-tab-pane" aria-selected="false">
                      관심 영업점<span class="badge bg-warning text-dark ms-1">{{ likedBanks.length }}</span>
                    </button>
                  </li>
                </ul>

                <div class="tab-content" id="likedProductsTabContent">
                  <!-- 정기예금 -->
                  <div class="tab-pane fade show active" id="deposit-tab-pane" role="tabpanel" aria-labelledby="deposit-tab" tabindex="0">
                    <div v-if="likedDeposits.length === 0" class="text-center text-muted py-4">
                      관심있는 정기예금 상품이 없습니다.
                    </div>
                    <div class="row row-cols-1 row-cols-md-2 g-3" v-else>
                      <div v-for="product in likedDeposits" :key="product.fin_prdt_cd" class="col">
                         <div class="toss-product-card h-100 border-0 shadow-sm hover-grow cursor-pointer" @click="goToDepositDetail(product.fin_prdt_cd)" style="cursor: pointer;">
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

                  <!-- 정기적금 -->
                  <div class="tab-pane fade" id="saving-tab-pane" role="tabpanel" aria-labelledby="saving-tab" tabindex="0">
                    <div v-if="likedSavings.length === 0" class="text-center text-muted py-4">
                      관심있는 정기적금 상품이 없습니다.
                    </div>
                    <div class="row row-cols-1 row-cols-md-2 g-3" v-else>
                      <div v-for="product in likedSavings" :key="product.fin_prdt_cd" class="col">
                         <div class="toss-product-card h-100 border-0 shadow-sm hover-grow cursor-pointer" @click="goToSavingDetail(product.fin_prdt_cd)" style="cursor: pointer;">
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
                  
                  <!-- 주택담보 -->
                  <div class="tab-pane fade" id="mortgage-tab-pane" role="tabpanel" aria-labelledby="mortgage-tab" tabindex="0">
                    <div v-if="likedMortgages.length === 0" class="text-center text-muted py-4">
                      관심있는 주택담보대출 상품이 없습니다.
                    </div>
                    <div class="row row-cols-1 row-cols-md-2 g-3" v-else>
                      <div v-for="product in likedMortgages" :key="product.fin_prdt_cd" class="col">
                         <div class="toss-product-card h-100 border-0 shadow-sm hover-grow cursor-pointer" @click="goToMortgageDetail(product.fin_prdt_cd)" style="cursor: pointer;">
                            <div class="card-body p-3">
                              <p class="text-muted small mb-1">{{ product.kor_co_nm }}</p>
                              <h6 class="font-weight-bold mb-2 text-truncate" :title="product.fin_prdt_nm">{{ product.fin_prdt_nm }}</h6>
                              <div class="d-flex justify-content-between align-items-end mt-3">
                                <span class="badge bg-light text-dark border">주택담보대출</span>
                                <button class="btn btn-sm btn-outline-danger p-1 lh-1" @click.stop="toggleLikeMortgage(product.fin_prdt_cd)" title="관심 해제">
                                  <i class="bi bi-heart-fill"></i>
                                </button>
                              </div>
                            </div>
                         </div>
                      </div>
                    </div>
                  </div>

                  <!-- 전세금대출 -->
                  <div class="tab-pane fade" id="jeonse-tab-pane" role="tabpanel" aria-labelledby="jeonse-tab" tabindex="0">
                    <div v-if="likedJeonses.length === 0" class="text-center text-muted py-4">
                      관심있는 전세금대출 상품이 없습니다.
                    </div>
                    <div class="row row-cols-1 row-cols-md-2 g-3" v-else>
                      <div v-for="product in likedJeonses" :key="product.fin_prdt_cd" class="col">
                         <div class="toss-product-card h-100 border-0 shadow-sm hover-grow cursor-pointer" @click="goToJeonseDetail(product.fin_prdt_cd)" style="cursor: pointer;">
                            <div class="card-body p-3">
                              <p class="text-muted small mb-1">{{ product.kor_co_nm }}</p>
                              <h6 class="font-weight-bold mb-2 text-truncate" :title="product.fin_prdt_nm">{{ product.fin_prdt_nm }}</h6>
                              <div class="d-flex justify-content-between align-items-end mt-3">
                                <span class="badge bg-light text-dark border">전세금대출</span>
                                <button class="btn btn-sm btn-outline-danger p-1 lh-1" @click.stop="toggleLikeJeonse(product.fin_prdt_cd)" title="관심 해제">
                                  <i class="bi bi-heart-fill"></i>
                                </button>
                              </div>
                            </div>
                         </div>
                      </div>
                    </div>
                  </div>

                  <!-- 관심 영업지점 -->
                  <div class="tab-pane fade" id="bank-tab-pane" role="tabpanel" aria-labelledby="bank-tab" tabindex="0">
                    <div v-if="likedBanks.length === 0" class="text-center text-muted py-4">
                      저장된 관심 영업지점이 없습니다. 지도에서 별 모양을 눌러 추가해보세요!
                    </div>
                    <div class="row row-cols-1 row-cols-md-2 g-3" v-else>
                      <div v-for="bank in likedBanks" :key="bank.id" class="col">
                         <div class="toss-product-card h-100 border-0 shadow-sm hover-grow">
                            <div class="card-body p-3">
                              <p class="text-muted small mb-1">{{ bank.address }}</p>
                              <h6 class="font-weight-bold mb-2 text-truncate" :title="bank.name">
                                ⭐ {{ bank.name }}
                              </h6>
                              <div class="d-flex justify-content-between align-items-end mt-3">
                                <span class="badge bg-warning text-dark border border-warning">관심 영업점</span>
                                <button class="btn btn-sm btn-outline-secondary p-1 lh-1" @click.stop="removeFavoriteBank(bank)" title="관심 지점 삭제">
                                  <i class="bi bi-trash"></i>
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
                <p class="lead mb-2">아직 관심 목록에 아무 것도 없습니다.</p>
                <p class="text-muted mb-4 small">다양한 금융 상품과 영업점을 둘러보고 추가해보세요!</p>
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
import { useMortgageStore } from '@/features/products/store/mortgageStore.js';
import { useJeonseStore } from '@/features/products/store/jeonseStore.js';
import swal from 'sweetalert';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const depositStore = useDepositStore();
const savingStore = useSavingStore();
const mortgageStore = useMortgageStore();
const jeonseStore = useJeonseStore();

const username = route.params.username;
const profile = ref({});
const loadingProducts = ref(true);
const likedProductsError = ref(null);

const likedDeposits = ref([]);
const likedSavings = ref([]);
const likedMortgages = ref([]);
const likedJeonses = ref([]);
const likedBanks = ref([]);

const fetchProfileAndProducts = async () => {
    loadingProducts.value = true;
    likedProductsError.value = null;
    try {
        const userInfo = await userStore.getProfile(username);
        profile.value = userInfo;

        likedDeposits.value = userInfo.interested_deposits || [];
        likedSavings.value = userInfo.interested_savings || [];
        likedMortgages.value = userInfo.interested_mortgages || [];
        likedJeonses.value = userInfo.interested_jeonses || [];
        likedBanks.value = userInfo.favorite_banks || [];

    } catch (error) {
        console.error("프로필 및 상품 정보 로딩 실패:", error);
        likedProductsError.value = "정보를 불러오는 데 실패했습니다.";
        swal("오류", "프로필 정보를 불러오지 못했습니다.", "error");
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
  if (value == null || value === 0) return '미설정';
  if (value <= 2) return '안정형(위험 회피)';
  if (value <= 4) return '안정추구형';
  if (value <= 6) return '위험중립형';
  if (value <= 8) return '적극수익추구형';
  return '공격투자형(위험 선호)';
}

const formatCurrency = (value) => {
  if (!value) return 0;
  return new Intl.NumberFormat('ko-KR').format(value);
};

const likedProductsCount = computed(() => 
  likedDeposits.value.length + 
  likedSavings.value.length + 
  likedMortgages.value.length + 
  likedJeonses.value.length +
  likedBanks.value.length
);

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

const goToMortgageDetail = (code) => {
    router.push({ name: 'mortgage-detail', params: { code } });
};

const goToJeonseDetail = (code) => {
    router.push({ name: 'jeonse-detail', params: { code } });
};

const toggleLikeDeposit = async (code) => {
    try {
        await depositStore.likeDeposit(code);
        await fetchProfileAndProducts(); 
    } catch(e) {}
}
const toggleLikeSaving = async (code) => {
    try {
        await savingStore.likeSaving(code);
        await fetchProfileAndProducts();
    } catch(e) {}
}
const toggleLikeMortgage = async (code) => {
    try {
        await mortgageStore.likeMortgage(code);
        await fetchProfileAndProducts();
    } catch(e) {}
}
const toggleLikeJeonse = async (code) => {
    try {
        await jeonseStore.likeJeonse(code);
        await fetchProfileAndProducts();
    } catch(e) {}
}

const removeFavoriteBank = async (branch) => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/accounts/favorite-bank/", 
        { branch_id: branch.id, branch_name: branch.name, branch_address: branch.address },
        { headers: { Authorization: `Token ${userStore.token}` } }
      );
      if (response.status === 200 || response.status === 201) {
          swal("해제 완료", `${branch.name}이(가) 관심 지점에서 삭제되었습니다.`, "success");
          fetchProfileAndProducts(); 
      }
    } catch (e) {
      console.error(e);
      swal("오류", "관심 지점 삭제에 실패했습니다.", "error");
    }
}

const confirmDeleteAccount = () => {
    swal({
        title: "회원 탈퇴",
        text: "정말로 탈퇴하시겠습니까? 관심 내역이 모두 삭제되며 복구할 수 없습니다.",
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
.page-wrapper { padding: 3rem 0; }
.content-container { max-width: 1140px; margin: 0 auto; padding: 0 1rem; }
.page-section-header { text-align: center; margin-bottom: 3rem; }
.title { font-size: 2.2rem; font-weight: 700; color: #191f28; margin-bottom: 0.5rem; }
.subtitle { font-size: 1.1rem; color: #4e5968; }

.profile-image-wrapper {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
}
.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-stats-grid {
  display: flex;
  background-color: #f9fafb;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}
.stat-item {
  flex: 1;
}
.stat-item:first-child { border-right: 1px solid #e5e8eb; }
.stat-label { font-size: 0.85rem; color: #8b95a1; margin-bottom: 0.25rem; }
.stat-value { font-size: 1.1rem; }

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f2f4f6;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: #8b95a1; font-weight: 500; }
.detail-data { color: #191f28; font-weight: 600; }

.toss-product-card {
  background-color: #f9fafb;
  border-radius: 16px;
  border: 1px solid #f2f4f6 !important;
  transition: all 0.2s ease;
}
.hover-grow:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
  background-color: #ffffff;
  border-color: #e5e8eb !important;
}
.nav-pills .nav-link {
  border-radius: 12px;
  padding: 0.6rem 1.2rem;
  color: #4e5968;
  font-weight: 500;
  background-color: transparent;
}
.nav-pills .nav-link.active {
  background-color: #3182f6;
  color: white;
  font-weight: 600;
}
</style>
