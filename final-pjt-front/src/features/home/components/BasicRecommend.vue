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
                  :class="{ active: i === activeSlideIndex }" 
                  aria-label="Slide"></button>
        </div>

        <!-- Carousel Items -->
        <div class="carousel-inner pb-5 pt-2" style="padding-left: 20px; padding-right: 20px;">
          <div 
            class="carousel-item" 
            v-for="(product, index) in allRecommended" 
            :key="product.fin_prdt_cd"
            :class="{ active: index === activeSlideIndex }"
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
import { computed, onMounted, ref } from 'vue';
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

const activeSlideIndex = ref(Number(sessionStorage.getItem('basicRecommendSlide')) || 0);

onMounted(async () => {
  if (userStore.isLogin) {
    if (depositStore.deposits.length === 0) depositStore.fetchDeposits();
    if (savingStore.savings.length === 0) savingStore.fetchSavings();
    if (mortgageStore.mortgages.length === 0) mortgageStore.fetchMortgages();
    if (jeonseStore.jeonses.length === 0) jeonseStore.fetchJeonses();
  }
  
  // Carousel 이벤트 리스너 등록 후 상태 저장
  setTimeout(() => {
    const carouselEl = document.getElementById('recommendCarousel');
    if (carouselEl) {
      carouselEl.addEventListener('slid.bs.carousel', (event) => {
        sessionStorage.setItem('basicRecommendSlide', event.to);
      });
    }
  }, 500);
});

const allRecommended = computed(() => {
  if (!userStore.isLogin) return [];
  
  const recommended = [];
  const userInfo = userStore.userInfo;
  const userPeriod = userInfo.desirePeriod || 12; // 목표 투자 기간 (개월)
  const userTendency = userInfo.tendency || 5;    // 투자 성향 (1~10)
  
  // 자산(wealth)과 연봉(salary)을 기반으로 자금 여력 계산 (단위: 만원)
  const totalPower = (userInfo.wealth || 0) + (userInfo.salary || 0); 
  // 기준치(예: 5000만원) 대비 여력 비율 (너무 극단적인 값을 막기 위해 0.5 ~ 2 사이로 제한)
  const powerRatio = Math.min(2, Math.max(0.5, totalPower / 5000));
  
  // 성향(tendency)과 자금 여력(powerRatio)을 융합하여 '변동금리 위험 페널티 가중치' 결정
  // 성향이 낮을수록(안정형), 여력이 적을수록 가중치(위험 민감도)가 커짐
  const riskPenaltyWeight = Math.max(0, (11 - userTendency) * 0.1) / powerRatio;
  
  // 1. 예금(Deposit) - 사용자의 목표 기간(desirePeriod)과 일치할수록 높은 점수
  if (depositStore.deposits.length > 0) {
    let mapped = depositStore.deposits.map(p => {
      let bestScore = -999;
      let bestRate = 0;
      p.options.forEach(o => {
        const rate = Number(o.intr_rate2 || o.intr_rate);
        if (!isNaN(rate) && rate > 0) {
          // 목표 기간과의 차이 1개월당 0.15%p 감점 적용
          const periodDiff = Math.abs((o.save_trm || 12) - userPeriod);
          const score = rate - (periodDiff * 0.15);
          if (score > bestScore) {
            bestScore = score;
            bestRate = rate;
          }
        }
      });
      return { ...p, score: bestScore, displayRate: bestRate, isLoan: false, categoryName: '정기예금', detailRoute: 'deposit-detail' };
    });
    // 유효한 점수를 기준으로 내림차순 정렬
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => b.score - a.score);
    if (mapped[0]) recommended.push(mapped[0]);
  }
  
  // 2. 적금(Saving) - 사용자의 목표 기간(desirePeriod) 페널티 동일 적용
  if (savingStore.savings.length > 0) {
    let mapped = savingStore.savings.map(p => {
      let bestScore = -999;
      let bestRate = 0;
      p.options.forEach(o => {
        const rate = Number(o.intr_rate2 || o.intr_rate);
        if (!isNaN(rate) && rate > 0) {
          const periodDiff = Math.abs((o.save_trm || 12) - userPeriod);
          const score = rate - (periodDiff * 0.15);
          if (score > bestScore) {
            bestScore = score;
            bestRate = rate;
          }
        }
      });
      return { ...p, score: bestScore, displayRate: bestRate, isLoan: false, categoryName: '정기적금', detailRoute: 'saving-detail' };
    });
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => b.score - a.score);
    if (mapped[0]) recommended.push(mapped[0]);
  }
  
  // 3. 전세자금대출(Jeonse) - 자금 여력과 투자 성향을 고려하여 최저금리와 금리변동폭(Spread) 종합 점수 계산
  if (jeonseStore.jeonses.length > 0) {
    let mapped = jeonseStore.jeonses.map(p => {
      let bestScore = -999; // 대출은 음수로 점수를 매겨 가장 높은 값(0에 가까운 값)이 1위
      let bestRate = 0;
      p.options.forEach(o => {
        const minRate = Number(o.lend_rate_min);
        const maxRate = Number(o.lend_rate_max) || minRate;
        if (!isNaN(minRate) && minRate > 0) {
          const spreadRisk = Math.max(0, maxRate - minRate);
          // 기본 금리 부담(-minRate)에 최고-최저 금리차(spread)에 따른 리스크 페널티 차감
          const score = -minRate - (spreadRisk * riskPenaltyWeight);
          if (score > bestScore) {
            bestScore = score;
            bestRate = minRate;
          }
        }
      });
      return { ...p, score: bestScore, displayRate: bestRate, isLoan: true, categoryName: '전세자금대출', detailRoute: 'jeonse-detail' };
    });
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => b.score - a.score); 
    if (mapped[0]) recommended.push(mapped[0]);
  }
  
  // 4. 주택담보대출(Mortgage) - 자금 여력과 투자 성향 고려 모델 반영
  if (mortgageStore.mortgages.length > 0) {
    let mapped = mortgageStore.mortgages.map(p => {
      let bestScore = -999;
      let bestRate = 0;
      p.options.forEach(o => {
        const minRate = Number(o.lend_rate_min);
        const maxRate = Number(o.lend_rate_max) || minRate;
        if (!isNaN(minRate) && minRate > 0) {
          const spreadRisk = Math.max(0, maxRate - minRate);
          const score = -minRate - (spreadRisk * riskPenaltyWeight);
          if (score > bestScore) {
            bestScore = score;
            bestRate = minRate;
          }
        }
      });
      return { ...p, score: bestScore, displayRate: bestRate, isLoan: true, categoryName: '주택담보대출', detailRoute: 'mortgage-detail' };
    });
    mapped = mapped.filter(p => p.displayRate > 0).sort((a, b) => b.score - a.score);
    if (mapped[0]) recommended.push(mapped[0]);
  }
  
  // 만약 저장된 슬라이드 인덱스가 결과 배열 크기를 초과하면 초기화
  if (activeSlideIndex.value >= recommended.length) {
    activeSlideIndex.value = 0;
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