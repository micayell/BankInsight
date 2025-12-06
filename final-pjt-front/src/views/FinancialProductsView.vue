<template>
  <div class="page-wrapper">
    <div class="content-container financial-products-view">
      <header class="page-section-header pb-3 mb-4 border-bottom">
        <div>
          <h1 class="h4 mb-0">금융 상품</h1>
          <p class="text-muted mb-0 mt-1 subtitle-text">나에게 맞는 최적의 예금 및 적금 상품을 찾아보세요.</p>
        </div>
      </header>

      <div class="product-type-selector-bar mb-4">
        <button
          @click="selectProductType('deposits')"
          class="btn btn-custom me-2"
          :class="{ 'btn-custom-primary': activeProductType === 'deposits', 'btn-custom-outline-theme': activeProductType !== 'deposits' }">
          <i class="bi bi-wallet2 me-2"></i>정기예금
        </button>
        <button
          @click="selectProductType('savings')"
          class="btn btn-custom"
          :class="{ 'btn-custom-primary': activeProductType === 'savings', 'btn-custom-outline-theme': activeProductType !== 'savings' }">
          <i class="bi bi-piggy-bank me-2"></i>정기적금
        </button>
      </div>

      <div class="filter-bar card-kia p-3 mb-4">
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
            <button class="btn btn-custom btn-custom-primary" @click="applyActiveFilters">조회</button>
          </div>
          <div class="col-md-2 d-grid">
            <button class="btn btn-custom btn-custom-outline-theme" @click="resetAndSearchFilters">초기화</button>
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
          <div class="card product-card-custom h-100" @click="goToDetail(product)">
            <div class="card-header product-card-header d-flex align-items-center">
              <img v-if="product.logoUrl" :src="product.logoUrl" :alt="`${product.kor_co_nm} 로고`" class="bank-logo-financial me-2">
              <h5 class="product-title-custom mb-0">{{ product.fin_prdt_nm }}</h5>
            </div>
            <div class="card-body">
              <p class="product-bank-custom mb-3">{{ product.kor_co_nm }}</p>
              <div class="rate-info-custom mt-auto text-end">
                <small class="text-muted">최고 연 (세전)</small>
                <div class="product-max-rate-custom">{{ getMaxRate(product.options) }}%</div>
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
import { useDepositStore } from '@/stores/depositStore';
import { useSavingStore } from '@/stores/savingStore';
import { useRouter } from 'vue-router';

const depositStore = useDepositStore();
const savingStore = useSavingStore();
const router = useRouter();

const activeProductType = ref('deposits');
const isLoading = ref(true);
const hasError = ref(false);

const selectedBank = ref('');
const selectedTerm = ref('');

const activeFilters = ref({
  bank: '',
  term: ''
});

const currentStore = computed(() => {
  return activeProductType.value === 'deposits' ? depositStore : savingStore;
});

const currentProducts = computed(() => {
  const store = currentStore.value;
  return activeProductType.value === 'deposits' ? store.deposits : store.savings;
});

const filteredProducts = computed(() => {
  if (!currentProducts.value || currentProducts.value.length === 0) return [];
  return currentProducts.value.filter(product => {
    const bankMatch = activeFilters.value.bank ? product.kor_co_nm === activeFilters.value.bank : true;
    const termMatch = activeFilters.value.term
      ? product.options.some(opt => String(opt.save_trm) === activeFilters.value.term)
      : true;
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
      savingStore.fetchSavings()
    ]);
    applyActiveFilters();
  } catch (error) {
    console.error("FinancialProductsView: 상품 정보 로드 실패:", error);
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
  const routeName = activeProductType.value === 'deposits' ? 'deposit-detail' : 'saving-detail';
  router.push({ name: routeName, params: { code } });
};

const getMaxRate = (options) => {
  if (!options || options.length === 0) return 'N/A';
  let maxRate = 0;
  options.forEach(opt => {
    const rate = parseFloat(opt.intr_rate2 || opt.intr_rate || 0);
    if (rate > maxRate) {
      maxRate = rate;
    }
  });
  return maxRate.toFixed(2);
};
</script>

<style scoped>
.financial-products-view {
  background-color: var(--app-background-secondary, #f8f9fa);
  padding: 1.5rem;
  min-height: calc(100vh - 56px - 70px);
  border-radius: var(--app-border-radius);
}

.page-section-header .subtitle-text {
  font-size: 0.9rem;
}

.financial-products-view .product-type-selector-bar {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
}
.financial-products-view .product-type-selector-bar .btn-custom {
  padding: 0.65rem 1.3rem;
  font-size: 0.95rem;
}

.financial-products-view .btn-custom-primary {
  background-color: #007bff;
  border-color: #007bff;
  color: #ffffff !important;
  font-weight: 600;
}
.financial-products-view .btn-custom-primary:hover {
  background-color: #0056b3;
  border-color: #0050a0;
}

.financial-products-view .btn-custom-outline-theme {
  border: 1px solid #6c757d;
  color: #495057;
  background-color: transparent;
}
.financial-products-view .btn-custom-outline-theme:hover {
  background-color: #e9ecef;
  color: #495057;
  border-color: #6c757d;
}

.financial-products-view .filter-bar {
  background-color: var(--app-background-primary, #ffffff);
  padding: 1.25rem;
  border-radius: var(--app-border-radius);
  margin-bottom: 2rem;
  border: 1px solid var(--app-border-color, #dee2e6);
}
.financial-products-view .filter-bar .row {
  align-items: flex-end;
}
.financial-products-view .filter-label-custom {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--app-text-medium, #6c757d);
  margin-bottom: 0.5rem;
}
.financial-products-view .form-select-custom {
  border-radius: var(--app-border-radius);
  border: 1px solid #ced4da;
  background-color: var(--app-background-primary, #ffffff);
  color: var(--app-text-dark, #343a40);
  font-size: 0.9rem;
  padding: 0.5rem 0.75rem;
}
.financial-products-view .form-select-custom:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.financial-products-view .filter-bar .btn-custom {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  width: 100%;
}


.product-card-custom {
  background-color: var(--app-background-primary, #ffffff);
  border: 1px solid var(--app-border-color, #dee2e6);
  border-radius: var(--app-border-radius);
  transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
}
.product-card-custom:hover {
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
  border-color: #007bff;
}
.product-card-header {
  background-color: #f9f9f9;
  border-bottom: 1px solid var(--app-border-color, #dee2e6);
  padding: 0.75rem 1rem;
}
.bank-logo-financial {
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: 4px;
  background-color: #fff;
  border: 1px solid #eee;
}
.product-card-custom .card-body {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.product-title-custom {
  font-size: 1rem;
  font-weight: 600;
  color: var(--app-text-dark, #343a40);
  margin-bottom: 0;
  line-height: 1.3;
}
.product-bank-custom {
  font-size: 0.85rem;
  color: var(--app-text-medium, #6c757d);
  margin-bottom: 1rem;
}
.rate-info-custom {
  margin-top: auto;
}
.rate-info-custom small {
  font-size: 0.8rem;
  color: var(--app-text-light, #adb5bd);
}
.product-max-rate-custom {
  font-size: 1.6rem;
  font-weight: 700;
  color: #007bff; 
  line-height: 1;
}
.product-footer-custom {
  background-color: transparent;
  border-top: 1px solid var(--app-border-color, #dee2e6);
  padding: 0.75rem 1.25rem;
  font-size: 0.8rem;
  color: var(--app-text-medium, #6c757d);
}

.product-grid {
  padding-bottom: 2rem;
}

.alert .bi {
  font-size: 2.5rem !important;
}
</style>