<template>
  <div class="py-5">
    <div class="container-fluid max-w-1140 mx-auto px-lg-0 px-3 financial-products-view">
      <header class="page-section-header pb-3 mb-4 border-bottom">
        <div>
          <h1 class="h4 mb-0">금융 상품</h1>
          <p class="text-muted mb-0 mt-1 subtitle-text">나에게 맞는 최적의 예·적금 및 대출 상품을 찾아보세요.</p>
        </div>
      </header>

      <div class="product-type-selector-bar mb-4">
        <button @click="selectProductType('deposits')" class="btn btn me-2" :class="{ 'btn-primary text-white': activeProductType === 'deposits', 'btn-light text-muted border-0 bg-white shadow-sm': activeProductType !== 'deposits' }"><i class="bi bi-wallet2 me-2"></i>정기예금</button>
        <button @click="selectProductType('savings')" class="btn btn me-2" :class="{ 'btn-primary text-white': activeProductType === 'savings', 'btn-light text-muted border-0 bg-white shadow-sm': activeProductType !== 'savings' }"><i class="bi bi-piggy-bank me-2"></i>정기적금</button>
        <button @click="selectProductType('mortgages')" class="btn btn me-2" :class="{ 'btn-primary text-white': activeProductType === 'mortgages', 'btn-light text-muted border-0 bg-white shadow-sm': activeProductType !== 'mortgages' }"><i class="bi bi-house-door me-2"></i>주택담보대출</button>
        <button @click="selectProductType('jeonses')" class="btn btn-custom" :class="{ 'btn-primary text-white': activeProductType === 'jeonses', 'btn-light text-muted border-0 bg-white shadow-sm': activeProductType !== 'jeonses' }"><i class="bi bi-key me-2"></i>전세자금대출</button>
      </div>

      <div class="filter-bar bg-white shadow-sm rounded-4 border-0 p-3 mb-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label for="bankFilter" class="form-label filter-label-custom">은행 선택</label>
            <select id="bankFilter" class="form-select form-select-custom" v-model="selectedBank">
              <option value="">모든 은행</option>
              <option v-for="bank in availableBanks" :key="bank" :value="bank">{{ bank }}</option>
            </select>
          </div>
          <div class="col-md-4">
            <label for="termFilter" class="form-label filter-label-custom">가입 기간 (개월)</label>
            <select id="termFilter" class="form-select form-select-custom" v-model="selectedTerm">
              <option value="">모든 기간</option>
              <option v-for="term in availableTerms" :key="term" :value="term">{{ term }}개월</option>
            </select>
          </div>
          <div class="col-md-2 d-grid">
            <button class="btn btn btn-primary text-white" @click="applyActiveFilters">조회</button>
          </div>
          <div class="col-md-2 d-grid">
            <button class="btn btn btn-light text-muted border-0 bg-white shadow-sm" @click="resetAndSearchFilters">초기화</button>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="loading-indicator-kia text-center py-5">
        <div class="spinner-border" role="status" :style="{ color: 'var(--app-primary-color)' }">
          <span class="visually-hidden">상품 정보를 불러오는 중...</span>
        </div>
        <p class="mt-3" :style="{ color: 'var(--app-text-medium)' }">상품 정보를 불러오는 중입니다.</p>
      </div>
      <div v-else-if="hasError" class="alert alert-danger text-center" role="alert">
        오류: 상품 정보를 불러오는 데 실패했습니다.
      </div>
      <div v-else-if="filteredProducts.length === 0" class="alert alert-info text-center py-5" role="alert">
        <i class="bi bi-clipboard-x d-block mb-3" style="font-size: 2.5rem;"></i>
        <p class="fs-5 mb-1">조건에 맞는 상품이 없습니다.</p>
        <p class="mb-0">필터 설정을 변경해보세요.</p>
      </div>

      <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 product-grid">
        <div v-for="product in filteredProducts" :key="product.fin_prdt_cd" class="col">
          <div class="card card toss-product-card h-100 border-0 shadow-sm hover-grow h-100" @click="goToDetail(product)">
            <div class="card-header product-card-header d-flex align-items-center">
              <img v-if="product.logoUrl" :src="product.logoUrl" :alt="`${product.kor_co_nm} 로고`" class="bank-logo-financial me-2">
              <h5 class="product-title-custom mb-0">{{ product.fin_prdt_nm }}</h5>
            </div>
            <div class="card-body">
              <p class="product-bank-custom mb-3">{{ product.kor_co_nm }}</p>
              <div class="rate-info-custom mt-auto text-end">
                <small class="text-muted">최고 연 (세전)</small>
                <div class="text-primary fw-bold fs-2">{{ getMaxRate(product.options) }}%</div>
              </div>
            </div>
            <div class="card-footer product-footer-custom">
              <small>만기 후: {{ product.mtrt_int || '별도 문의' }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useDepositStore } from '@/features/products/store/depositStore';
import { useSavingStore } from '@/features/products/store/savingStore';
import { useMortgageStore } from '@/features/products/store/mortgageStore';
import { useJeonseStore } from '@/features/products/store/jeonseStore';
import { useRouter } from 'vue-router';

const depositStore = useDepositStore();
const savingStore = useSavingStore();
const mortgageStore = useMortgageStore();
const jeonseStore = useJeonseStore();
const router = useRouter();

const activeProductType = ref('deposits');
const isLoading = ref(true);
const hasError = ref(false);

const selectedBank = ref('');
const selectedTerm = ref('');

const activeFilters = ref({ bank: '', term: '' });

const currentStore = computed(() => {
  if (activeProductType.value === 'deposits') return depositStore;
  if (activeProductType.value === 'savings') return savingStore;
  if (activeProductType.value === 'mortgages') return mortgageStore;
  return jeonseStore;
});

const currentProducts = computed(() => {
  if (activeProductType.value === 'deposits') return depositStore.deposits;
  if (activeProductType.value === 'savings') return savingStore.savings;
  if (activeProductType.value === 'mortgages') return mortgageStore.mortgages;
  return jeonseStore.jeonses;
});

const filteredProducts = computed(() => {
  if (!currentProducts.value || currentProducts.value.length === 0) return [];
  return currentProducts.value.filter(product => {
    const bankMatch = activeFilters.value.bank ? product.kor_co_nm === activeFilters.value.bank : true;
    let termMatch = true;
    if (activeFilters.value.term && (activeProductType.value === 'deposits' || activeProductType.value === 'savings')) {
      termMatch = product.options.some(opt => String(opt.save_trm) === activeFilters.value.term);
    }
    return bankMatch && termMatch;
  });
});

const availableBanks = computed(() => {
  if (!currentProducts.value || currentProducts.value.length === 0) return [];
  const banks = new Set(currentProducts.value.map(p => p.kor_co_nm));
  return Array.from(banks).sort((a, b) => a.localeCompare(b));
});

const availableTerms = computed(() => {
  if (!currentProducts.value || currentProducts.value.length === 0) return [];
  if (activeProductType.value === 'mortgages' || activeProductType.value === 'jeonses') return [];
  const terms = new Set();
  currentProducts.value.forEach(product => {
    if (product.options && Array.isArray(product.options)) {
      product.options.forEach(opt => terms.add(String(opt.save_trm)));
    }
  });
  return Array.from(terms).sort((a, b) => parseInt(a) - parseInt(b));
});

const loadData = async () => {
  isLoading.value = true;
  hasError.value = false;
  try {
    await Promise.all([
      depositStore.fetchDeposits(),
      savingStore.fetchSavings(),
      mortgageStore.fetchMortgages(),
      jeonseStore.fetchJeonses()
    ]);
    applyActiveFilters();
  } catch (error) {
    console.error('상품 정보 로드 실패:', error);
    hasError.value = true;
  } finally {
    isLoading.value = false;
  }
};

onMounted(loadData);

const applyActiveFilters = () => {
  activeFilters.value.bank = selectedBank.value;
  activeFilters.value.term = selectedTerm.value;
};

const selectProductType = (type) => {
  activeProductType.value = type;
  selectedBank.value = '';
  selectedTerm.value = '';
  applyActiveFilters();
};

const resetAndSearchFilters = () => {
  selectedBank.value = '';
  selectedTerm.value = '';
  applyActiveFilters();
};

const goToDetail = (product) => {
  const code = product.fin_prdt_cd;
  let routeName = 'deposit-detail';
  if (activeProductType.value === 'savings') routeName = 'saving-detail';
  else if (activeProductType.value === 'mortgages') routeName = 'mortgage-detail';
  else if (activeProductType.value === 'jeonses') routeName = 'jeonse-detail';
  

  router.push({ name: routeName, params: { code } });
};

const getMaxRate = (options) => {
  if (!options || options.length === 0) return 'N/A';
  let maxRate = 0;
  options.forEach(opt => {
    const rate = parseFloat(opt.intr_rate2 || opt.intr_rate || opt.lend_rate_min || 0);
    if (rate && rate > maxRate) {
      maxRate = rate;
    }
  });
  return maxRate > 0 ? maxRate.toFixed(2) : 'N/A';
};
</script>

<style scoped>
.toss-product-card {
  border-radius: 16px !important;
  background-color: #ffffff;
  transition: all 0.2s ease;
}
.hover-grow:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08) !important;
}
.max-w-1140 {
  max-width: 1140px;
}
.btn-light.bg-white {
  background-color: #ffffff !important;
}
.btn {
  border-radius: 12px !important;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
}
.form-select {
  border-radius: 12px;
  border: 1px solid #e5e8eb;
  padding: 0.75rem 1rem;
}

.bank-logo-financial {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 50%;
  border: 1px solid #f2f4f6;
  background-color: #ffffff;
  padding: 4px;
}
.page-section-header h1 {

  font-weight: 700;
  font-size: 2rem;
  color: #191f28;
}
</style>