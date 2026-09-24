<template>
  <div class="basic-recommend-section bg-white py-5" v-if="userStore.isLogin && allRecommended.length > 0">
    <div class="container px-4">
      <div class="mb-4">
        <h3 class="fw-bold fs-4 mb-2">
          <span class="text-primary">{{ userStore.userInfo.nickname || userStore.userInfo.username }}</span>님을 위한 맞춤 금융상품
        </h3>
        <p class="text-muted fw-medium mb-0">자주 찾는 4가지 카테고리별로 {{ userStore.userInfo.nickname || userStore.userInfo.username }}님께 가장 유리한 상품을 모아봤어요!</p>
      </div>

      <!-- Bootstrap Carousel -->
      <div id="recommendCarousel" class="carousel slide position-relative" data-bs-ride="carousel" data-bs-interval="3500">
        <!-- Indicators -->
        <div class="carousel-indicators custom-indicators">
          <button v-for="(p, i) in allRecommended" :key="'ind-'+i" type="button" 
                  data-bs-target="#recommendCarousel" 
                  :data-bs-slide-to="i" 
                  :class="{ active: i === 0 }" 
                  aria-label="Slide"></button>
        </div>

        <!-- Carousel Items -->
        <div class="carousel-inner pb-5 pt-2" style="padding-left: 20px; padding-right: 20px;">
          <div 
            class="carousel-item" 
            v-for="(product, index) in allRecommended" 
            :key="product.fin_prdt_cd"
            :class="{ active: index === 0 }"
          >
            <div class="toss-product-card shadow-sm d-flex justify-content-between align-items-center p-4 mx-3 cursor-pointer hover-grow" @click="goToDetail(product)">
              <div>
                <span class="badge bg-light text-primary border border-primary mb-2">
                  {{ product.categoryName }} 추천
                </span>
                <h4 class="fw-bold mb-1 fs-5 text-truncate" style="max-width: 250px;">{{ product.fin_prdt_nm }}</h4>
                <p class="text-muted mb-0 small">{{ product.kor_co_nm }}</p>
              </div>
              <div class="text-end ms-3">
                <div class="fs-6 text-muted mb-1">{{ product.isLoan ? '최저 금리' : '최고 금리' }}</div>
                <div class="text-primary fw-bold fs-2 lh-1">{{ product.displayRate.toFixed(2) }}%</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Carousel Controls (Outward positioned) -->
        <button class="carousel-control-prev custom-control-prev" type="button" data-bs-target="#recommendCarousel" data-bs-slide="prev">
          <span class="control-bg">
            <span class="carousel-control-prev-icon" aria-hidden="true" style="filter: invert(1) grayscale(100); opacity: 0.5;"></span>
          </span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next custom-control-next" type="button" data-bs-target="#recommendCarousel" data-bs-slide="next">
          <span class="control-bg">
            <span class="carousel-control-next-icon" aria-hidden="true" style="filter: invert(1) grayscale(100); opacity: 0.5;"></span>
          </span>
          <span class="visually-hidden">Next</span>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/features/accounts/store/userStore';
import { useDepositStore } from '@/features/products/store/depositStore';
import { useSavingStore } from '@/features/products/store/savingStore';
import { useMortgageStore } from '@/features/products/store/mortgageStore';
import { useJeonseStore } from '@/features/products/store/jeonseStore';

const router = useRouter();
const userStore = useUserStore();
const depositStore = useDepositStore();
const savingStore = useSavingStore();
const mortgageStore = useMortgageStore();
const jeonseStore = useJeonseStore();

onMounted(async () => {
  if (userStore.isLogin) {
    if (depositStore.deposits.length === 0) depositStore.fetchDeposits();
    if (savingStore.savings.length === 0) savingStore.fetchSavings();
    if (mortgageStore.mortgages.length === 0) mortgageStore.fetchMortgages();
    if (jeonseStore.jeonses.length === 0) jeonseStore.fetchJeonses();
  }
});

const allRecommended = computed(() => {
  if (!userStore.isLogin) return [];
  
  const recommended = [];
  
  // 1. 예금(Deposit) - 금리가 높은 순 (내림차순)
  if (depositStore.deposits.length > 0) {
    let mapped = depositStore.deposits.map(p => {
      const rates = p.options.map(o => Number(o.intr_rate2 || o.intr_rate)).filter(r => !isNaN(r));
      return { ...p, displayRate: rates.length ? Math.max(...rates) : 0, isLoan: false, categoryName: '정기예금', detailRoute: 'deposit-detail' };
    });
    // 유효한 금리가 있는 것만 남김
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => b.displayRate - a.displayRate);
    if(mapped[0]) recommended.push(mapped[0]);
  }
  
  // 2. 적금(Saving) - 금리가 높은 순 (내림차순)
  if (savingStore.savings.length > 0) {
    let mapped = savingStore.savings.map(p => {
      const rates = p.options.map(o => Number(o.intr_rate2 || o.intr_rate)).filter(r => !isNaN(r));
      return { ...p, displayRate: rates.length ? Math.max(...rates) : 0, isLoan: false, categoryName: '정기적금', detailRoute: 'saving-detail' };
    });
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => b.displayRate - a.displayRate);
    if(mapped[0]) recommended.push(mapped[0]);
  }
  
  // 3. 전세자금대출(Jeonse) - 최저금리가 낮은 순 (오름차순)
  if (jeonseStore.jeonses.length > 0) {
    let mapped = jeonseStore.jeonses.map(p => {
      const rates = p.options.map(o => Number(o.lend_rate_min)).filter(r => !isNaN(r) && r > 0);
      return { ...p, displayRate: rates.length ? Math.min(...rates) : 0, isLoan: true, categoryName: '전세자금대출', detailRoute: 'jeonse-detail' };
    });
    // 금리가 0인 항목 제외하고 오름차순 정렬
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => a.displayRate - b.displayRate);
    if(mapped[0]) recommended.push(mapped[0]);
  }
  
  // 4. 주택담보대출(Mortgage) - 최저금리가 낮은 순 (오름차순)
  if (mortgageStore.mortgages.length > 0) {
    let mapped = mortgageStore.mortgages.map(p => {
      const rates = p.options.map(o => Number(o.lend_rate_min)).filter(r => !isNaN(r) && r > 0);
      return { ...p, displayRate: rates.length ? Math.min(...rates) : 0, isLoan: true, categoryName: '주택담보대출', detailRoute: 'mortgage-detail' };
    });
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => a.displayRate - b.displayRate);
    if(mapped[0]) recommended.push(mapped[0]);
  }
  
  return recommended;
});

const goToDetail = (product) => {
  router.push({ name: product.detailRoute, params: { code: product.fin_prdt_cd } });
};
</script>

<style scoped>
.toss-product-card {
  background-color: #f9fafb;
  border-radius: 16px;
  border: 1px solid #f2f4f6;
  transition: all 0.2s ease;
  min-height: 120px;
}
.hover-grow:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
  background-color: #ffffff;
  border-color: #e5e8eb;
}
.cursor-pointer {
  cursor: pointer;
}

/* Custom Carousel Controls Setup */
.custom-control-prev,
.custom-control-next {
  width: 40px; /* 화살표 너비 축소해서 카드 밖으로 빼기 */
  z-index: 5;
  top: 50%;
  transform: translateY(-50%);
  height: 40px;
}
.custom-control-prev {
  left: -20px;
}
.custom-control-next {
  right: -20px;
}

.carousel-indicators {
  bottom: 0px;
}
.carousel-indicators [data-bs-target] {
  background-color: #ccc;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin: 0 4px;
}
.carousel-indicators .active {
  background-color: #0d6efd;
}
</style>
