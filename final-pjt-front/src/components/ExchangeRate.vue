<template>
  <div class="exchange-rate-inner-content">
    <header class="view-header text-center mb-4">
      <h2 class="h3 page-main-title mb-1">주요 통화 환율 정보</h2>
      <p class="text-muted current-date-display mb-0">기준일: {{ todayDateFormatted }}</p>
    </header>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" style="width: 2.5rem; height: 2.5rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">환율 정보를 불러오는 중입니다...</p>
    </div>

    <div v-else-if="error" class="alert alert-warning text-center" role="alert">
      <p class="mb-0">{{ error }}</p>
    </div>

    <div v-else class="table-responsive exchange-table-wrapper">
      <table class="table table-hover align-middle text-center table-sm custom-exchange-table">
        <thead class="table-light">
          <tr>
            <th scope="col" class="text-start currency-header">통화</th>
            <th scope="col" class="text-nowrap rate-header">오늘 환율 (살때/팔때)</th>
            <th scope="col" class="text-nowrap fluctuation-header">전 영업일 대비 (등락/등락률)</th>
            <th scope="col" class="text-nowrap rate-header">전 영업일 환율 (살때/팔때)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rate in processedRates" :key="rate.unit" class="data-row-divider">
            <td class="text-start currency-name-cell align-middle">
              <div class="fw-bold">{{ rate.name }}</div>
              <small class="text-muted d-block">{{ rate.unit }}</small>
            </td>
            <td class="rate-cell">
              <div>{{ formatRate(rate.today?.tts) }}</div>
              <div class="sub-rate">{{ formatRate(rate.today?.ttb) }}</div>
            </td>
            <td class="fluctuation-cell">
              <div :class="getFluctuationClass(rate.fluctuation.tts_amount)">
                <span v-if="rate.fluctuation.tts_amount !== null && rate.fluctuation.tts_amount !== 0">
                  {{ rate.fluctuation.tts_amount > 0 ? '▲' : '▼' }} {{ formatRate(Math.abs(rate.fluctuation.tts_amount), true) }}
                  ({{ formatPercentage(rate.fluctuation.tts_percent) }})
                </span>
                <span v-else-if="rate.today?.tts && rate.yesterday?.tts">–</span>
                <span v-else>N/A</span>
              </div>
              <div :class="getFluctuationClass(rate.fluctuation.ttb_amount)" class="sub-rate">
                <span v-if="rate.fluctuation.ttb_amount !== null && rate.fluctuation.ttb_amount !== 0">
                  {{ rate.fluctuation.ttb_amount > 0 ? '▲' : '▼' }} {{ formatRate(Math.abs(rate.fluctuation.ttb_amount), true) }}
                  ({{ formatPercentage(rate.fluctuation.ttb_percent) }})
                </span>
                <span v-else-if="rate.today?.ttb && rate.yesterday?.ttb">–</span>
                <span v-else>N/A</span>
              </div>
            </td>
            <td class="rate-cell">
              <div>{{ formatRate(rate.yesterday?.tts) }}</div>
              <div class="sub-rate">{{ formatRate(rate.yesterday?.ttb) }}</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useExchangeStore } from '@/stores/exchangeStore';
import { storeToRefs } from 'pinia';

const exchangeStore = useExchangeStore();
const { todayRates, yesterdayRates, isLoading, error } = storeToRefs(exchangeStore);

const TARGET_CURRENCIES = [
  { code: 'USD', name: '미국 달러' },
  { code: 'CAD', name: '캐나다 달러' },
  { code: 'EUR', name: '유로' },
  { code: 'GBP', name: '영국 파운드' },
  { code: 'JPY(100)', name: '일본 옌 (100)' },
  { code: 'CNH', name: '중국 위안화' },
];

const todayDateFormatted = computed(() => {
  const today = new Date();
  return `${today.getFullYear()}년 ${today.getMonth() + 1}월 ${today.getDate()}일`;
});

onMounted(() => {
  exchangeStore.fetchRates();
});

const processedRates = computed(() => {
  if (isLoading.value || error.value) return [];
  return TARGET_CURRENCIES.map(target => {
    const todayData = todayRates.value.find(r => r.cur_unit === target.code);
    const yesterdayData = yesterdayRates.value.find(r => r.cur_unit === target.code);

    const parseRate = (rateStr) => rateStr ? parseFloat(rateStr.replace(/,/g, '')) : null;

    const todayTTS = parseRate(todayData?.tts);
    const todayTTB = parseRate(todayData?.ttb);
    const yesterdayTTS = parseRate(yesterdayData?.tts);
    const yesterdayTTB = parseRate(yesterdayData?.ttb);
    
    let fluctuationTTS_amount = null, fluctuationTTS_percent = null;
    if (todayTTS !== null && yesterdayTTS !== null && yesterdayTTS !== 0) {
        fluctuationTTS_amount = todayTTS - yesterdayTTS;
        fluctuationTTS_percent = (fluctuationTTS_amount / yesterdayTTS) * 100;
    }

    let fluctuationTTB_amount = null, fluctuationTTB_percent = null;
    if (todayTTB !== null && yesterdayTTB !== null && yesterdayTTB !== 0) {
        fluctuationTTB_amount = todayTTB - yesterdayTTB;
        fluctuationTTB_percent = (fluctuationTTB_amount / yesterdayTTB) * 100;
    }

    return {
      unit: target.code,
      name: todayData?.cur_nm || target.name,
      today: { tts: todayTTS, ttb: todayTTB },
      yesterday: { tts: yesterdayTTS, ttb: yesterdayTTB },
      fluctuation: { 
        tts_amount: fluctuationTTS_amount,
        tts_percent: fluctuationTTS_percent,
        ttb_amount: fluctuationTTB_amount,
        ttb_percent: fluctuationTTB_percent,
      }
    };
  });
});

const formatRate = (value, isAmount = false) => {
  if (value === null || value === undefined || isNaN(value)) return isAmount ? '–' : 'N/A';
  const numValue = Number(value);
  if (numValue === 0 && !isAmount) return "0.00";
  
  return numValue.toLocaleString('ko-KR', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  });
};

const formatPercentage = (value) => {
  if (value === null || value === undefined || isNaN(value)) return '– %';
  return `${value.toFixed(2)}%`;
};

const getFluctuationClass = (fluctuationAmount) => {
  if (fluctuationAmount === null || fluctuationAmount === 0) return 'text-body-secondary';
  return fluctuationAmount > 0 ? 'text-danger' : 'text-primary';
};
</script>

<style scoped>
.exchange-rate-inner-content {
  /* No large margins/paddings, controlled by parent IndexView */
}
.view-header .page-main-title {
  font-weight: 600;
  color: #2a2f36;
}
.current-date-display {
  font-size: 0.85rem;
  color: #6c757d;
}

.exchange-table-wrapper {
  background-color: #fff;
  border-radius: 0.4rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #e9ecef;
}

.table {
  margin-bottom: 0;
  font-size: 0.9rem; /* 테이블 기본 폰트 크기 */
}

.table th, .table td {
  vertical-align: middle;
  padding: 0.7rem 0.5rem; /* 셀 패딩 */
}

.table thead th {
  font-weight: 500;
  color: #495057;
  background-color: #f8f9fa;
  border-bottom-width: 2px; /* 헤더 하단 선 두께 */
  white-space: nowrap;
}

.currency-header { width: 25%; }
.rate-header { width: 25%; }
.fluctuation-header { width: 25%; }


.currency-name-cell {
  font-weight: 500;
  text-align: left;
  padding-left: 1.2rem !important;
}
.currency-name-cell .text-muted {
  font-size: 0.8em;
  font-weight: normal;
}

.rate-cell, .fluctuation-cell {
  text-align: right;
  padding-right: 1.2rem;
  font-variant-numeric: tabular-nums; /* 숫자 정렬 */
}
.fluctuation-cell {
  min-width: 180px; /* 등락 정보 충분한 너비 확보 */
}

.rate-cell div, .fluctuation-cell div {
  line-height: 1.5;
}

.sub-rate {
  font-size: 0.9em;
  color: #6c757d;
}

.text-danger {
  color: #e55353 !important;
}

.text-primary {
  color: #3b7ddd !important;
}

.data-row-divider {
  border-bottom: 1px solid #f0f2f5;
}
tbody tr:last-child {
  border-bottom: none;
}
</style>