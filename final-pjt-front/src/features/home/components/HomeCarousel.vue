<template>
  <div class="toss-hero-section">
    <div id="homeMainCarousel" class="carousel slide toss-carousel" data-bs-ride="carousel">
      
      <div class="carousel-indicators toss-indicators">
        <button type="button" data-bs-target="#homeMainCarousel" data-bs-slide-to="0" :class="{ active: activeSlideIndex === 0 }" aria-current="true"></button>
        <button type="button" data-bs-target="#homeMainCarousel" data-bs-slide-to="1" :class="{ active: activeSlideIndex === 1 }"></button>
        <button type="button" data-bs-target="#homeMainCarousel" data-bs-slide-to="2" :class="{ active: activeSlideIndex === 2 }"></button>
      </div>
      
      <div class="carousel-inner h-100">
        <!-- 1번 슬라이드: 맞춤 금융상품 -->
        <div class="carousel-item slide-item" :class="{ active: activeSlideIndex === 0 }" data-bs-interval="5000">
          <div class="container d-flex flex-column justify-content-center align-items-center h-100 text-center px-4">
            <h2 class="fw-bold text-dark mb-3 slide-title">나에게 딱 맞는<br/>금융상품 찾기</h2>
            <p class="text-muted fs-5 mb-5 slide-desc">복잡한 예적금, 대출 비교는 더 이상 그만!<br>BankInsight에서 한눈에 비교하고 자산을 키워보세요.</p>
            <RouterLink to="/financial-products" class="btn btn-toss-primary btn-lg px-5 shadow-sm hover-grow">
              금융상품 비교하기
            </RouterLink>
          </div>
        </div>

        <!-- 2번 슬라이드: 환율 정보 -->
        <div class="carousel-item slide-item" :class="{ active: activeSlideIndex === 1 }" data-bs-interval="4000">
          <div class="container d-flex flex-column justify-content-center align-items-center h-100 text-center px-4">
            <h2 class="fw-bold text-dark mb-3 slide-title">오늘의 환율은?</h2>
            <p class="text-muted fs-5 mb-5 slide-desc">주요 국가의 실시간 환율을 빠르게 확인하세요.</p>
            
            <div class="d-flex gap-4 justify-content-center flex-wrap align-items-center">
              <template v-if="majorRates.length > 0">
                <div class="toss-card shadow-sm" v-for="rate in majorRates" :key="rate.cur_unit">
                  <div class="toss-card-title">{{ getCurrencyName(rate.cur_unit) }}</div>
                  <div class="toss-card-value">{{ formatCurrency(rate.deal_bas_r || rate.bkpr) }}<span class="currency-unit">원</span></div>
                </div>
              </template>
              <div v-else-if="exchangeStore.error" class="toss-card shadow-sm text-danger" style="color:#d9534f !important;">
                {{ exchangeStore.error }}
              </div>
              <div v-else-if="!exchangeStore.isLoading" class="toss-card shadow-sm">
                <div class="mt-2 text-muted">환율 데이터가 없습니다.</div>
              </div>
              <div v-else class="toss-card loading-card shadow-sm">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <div class="mt-2 text-muted">불러오는 중...</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3번 슬라이드: 금 시세 -->
        <div class="carousel-item slide-item" :class="{ active: activeSlideIndex === 2 }" data-bs-interval="4000">
          <div class="container d-flex flex-column justify-content-center align-items-center h-100 text-center px-4">
            <h2 class="fw-bold text-dark mb-3 slide-title">반짝이는 금 시세</h2>
            <p class="text-muted fs-5 mb-5 slide-desc">안전 자산의 대명사, 오늘의 금 1g 가격을 확인해보세요.</p>
            
            <div class="toss-gold-card shadow-sm mb-5" v-if="latestGoldPrice">
              <span class="gold-price">{{ formatCurrency(latestGoldPrice) }}</span>
              <span class="gold-unit">원 / 1g</span>
            </div>
            <div class="toss-gold-card shadow-sm mb-5 text-danger" v-else-if="spotStore.error" style="color:#d9534f !important;">
              금 시세를 불러오지 못했습니다. <br> <span style="font-size: 0.9rem;">(데이터 없음)</span>
            </div>
            <div class="toss-gold-card shadow-sm mb-5 text-muted" v-else-if="!spotStore.loading">
              최근 금 시세 데이터가 없습니다.
            </div>
            <div class="toss-gold-card shadow-sm mb-5" v-else>
               <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            </div>
            
            <RouterLink to="/spot" class="btn btn-toss-secondary px-4 hover-grow">
              차트·시세 더보기
            </RouterLink>
          </div>
        </div>
      </div>
      
      <button class="carousel-control-prev toss-control" type="button" data-bs-target="#homeMainCarousel" data-bs-slide="prev">
        <div class="control-circle">
          <i class="bi bi-chevron-left fs-4"></i>
        </div>
      </button>
      <button class="carousel-control-next toss-control" type="button" data-bs-target="#homeMainCarousel" data-bs-slide="next">
        <div class="control-circle">
          <i class="bi bi-chevron-right fs-4"></i>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useExchangeStore } from '@/features/spot/store/exchangeStore';
import { useSpotStore } from '@/features/spot/store/spotStore';

const exchangeStore = useExchangeStore();
const spotStore = useSpotStore();

const activeSlideIndex = ref(Number(sessionStorage.getItem('homeMainSlide')) || 0);

onMounted(() => {
  if (exchangeStore.todayRates.length === 0 && !exchangeStore.isLoading) {
    exchangeStore.fetchRates();
  }
  if (spotStore.rawData.length === 0 && !spotStore.loading) {
    spotStore.setPeriod('1m'); 
  }

  // Carousel 이벤트 리스너 등록 후 상태 저장
  setTimeout(() => {
    const carouselEl = document.getElementById('homeMainCarousel');
    if (carouselEl) {
      carouselEl.addEventListener('slid.bs.carousel', (event) => {
        sessionStorage.setItem('homeMainSlide', event.to);
      });
    }
  }, 500);
});

const majorRates = computed(() => {
  const targetCurrencies = ['USD', 'JPY(100)', 'EUR'];
  return exchangeStore.todayRates.filter(rate => targetCurrencies.includes(rate.cur_unit));
});

const getCurrencyName = (code) => {
  const names = {
    'USD': '미국 USD',
    'JPY(100)': '일본 JPY',
    'EUR': '유럽 EUR'
  };
  return names[code] || code;
}

const latestGoldPrice = computed(() => {
  if (spotStore.prices.length > 0) {
    return spotStore.prices[spotStore.prices.length - 1]; 
  }
  return null;
});

const formatCurrency = (value) => {
  if (!value) return '-';
  const numString = String(value).replace(/,/g, '');
  return new Intl.NumberFormat('ko-KR').format(parseInt(numString));
};
</script>

<style scoped>
.toss-hero-section {
  background-color: #f2f4f6;
  padding: 40px 0 60px 0;
}

#homeMainCarousel {
  height: 480px; 
}

.slide-item {
  height: 100%;
}

.slide-title {
  font-size: 2.8rem;
  letter-spacing: -1px;
  line-height: 1.3;
  color: #191f28 !important;
}

.slide-desc {
  font-size: 1.15rem;
  color: #4e5968 !important;
  line-height: 1.6;
}

/* Toss Style Buttons */
.btn-toss-primary {
  background-color: #3182f6;
  color: #ffffff;
  border: none;
  font-weight: 600;
  font-size: 1.15rem;
  padding: 16px 32px;
  border-radius: 16px;
  transition: background-color 0.2s ease;
}

.btn-toss-primary:hover {
  background-color: #1b64da;
}

.btn-toss-secondary {
  background-color: #e8f3ff;
  color: #1b64da;
  border: none;
  font-weight: 600;
  font-size: 1.05rem;
  padding: 14px 28px;
  border-radius: 12px;
  transition: background-color 0.2s ease;
}
.btn-toss-secondary:hover {
  background-color: #d1e6ff;
}

/* Toss Style Cards */
.toss-card {
  background-color: #ffffff;
  padding: 24px 32px;
  border-radius: 20px;
  min-width: 160px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}

.toss-card-title {
  font-size: 1rem;
  color: #8b95a1;
  margin-bottom: 8px;
  font-weight: 500;
}

.toss-card-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #191f28;
}
.currency-unit {
  font-size: 1.1rem;
  font-weight: 500;
  margin-left: 4px;
}

.toss-gold-card {
  background-color: #ffffff;
  padding: 24px 48px;
  border-radius: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}

.gold-price {
  font-size: 2.2rem;
  font-weight: 700;
  color: #191f28;
}

.gold-unit {
  margin-left: 8px;
  font-size: 1.2rem;
  color: #8b95a1;
  font-weight: 500;
}

.hover-grow {
  transition: transform 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.hover-grow:hover {
  transform: translateY(-4px);
}

/* Custom Toss Carousel Controls */
.toss-control {
  width: 10%;
  opacity: 1;
}
.control-circle {
  width: 48px;
  height: 48px;
  background-color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  color: #4e5968;
  transition: background-color 0.2s, color 0.2s;
}
.toss-control:hover .control-circle {
  background-color: #f2f4f6;
  color: #191f28;
}

.toss-indicators {
  margin-bottom: -10px;
}
.toss-indicators button {
  width: 8px !important;
  height: 8px !important;
  border-radius: 50%;
  background-color: #b0b8c1 !important;
  border: none !important;
  margin: 0 6px !important;
  opacity: 0.5;
  transition: opacity 0.2s, background-color 0.2s;
}
.toss-indicators button.active {
  background-color: #3182f6 !important;
  opacity: 1;
}
</style>