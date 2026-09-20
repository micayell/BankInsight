<template>
  <div class="container spot-view-container py-4">
    <header class="view-header mb-4">
      <h1 class="h3 page-main-title">금/은 시세 변동 조회</h1>
    </header>

    <section class="controls-section card shadow-sm mb-4">
      <div class="card-body">
        <div class="mb-3 period-selector">
          <label class="form-label d-block mb-2 control-label">기간 선택</label>
          <div class="btn-group period-button-group" role="group">
            <button type="button" @click="selectPeriod('1m')" class="btn" :class="selectedPeriod === '1m' ? 'btn-dark' : 'btn-outline-secondary'">
              1개월
            </button>
            <button type="button" @click="selectPeriod('3m')" class="btn" :class="selectedPeriod === '3m' ? 'btn-dark' : 'btn-outline-secondary'">
              3개월
            </button>
            <button type="button" @click="selectPeriod('1y')" class="btn" :class="selectedPeriod === '1y' ? 'btn-dark' : 'btn-outline-secondary'">
              1년
            </button>
            <button type="button" @click="selectPeriod('3y')" class="btn" :class="selectedPeriod === '3y' ? 'btn-dark' : 'btn-outline-secondary'">
              3년
            </button>
          </div>
        </div>

        <hr class="my-3 control-divider">

        <div class="row g-3 align-items-end filter-input-group">
          <div class="col-md">
            <label for="startDate" class="form-label mb-1 control-label">시작일</label>
            <input type="date" id="startDate" v-model="tempSpotParameters.start" class="form-control form-control-sm" />
          </div>
          <div class="col-md">
            <label for="endDate" class="form-label mb-1 control-label">종료일</label>
            <input type="date" id="endDate" v-model="tempSpotParameters.end" class="form-control form-control-sm" />
          </div>
          <div class="col-md-auto asset-selector-group">
            <span class="form-label d-block mb-1 control-label">자산 선택</span>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" id="goldRadio" value="gold" v-model="tempSpotParameters.asset" />
              <label class="form-check-label" for="goldRadio">금</label>
            </div>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" id="silverRadio" value="silver" v-model="tempSpotParameters.asset" />
              <label class="form-check-label" for="silverRadio">은</label>
            </div>
          </div>
          <div class="col-md-auto fetch-button-wrapper">
            <button @click="applyParametersAndLoadData" class="btn btn-primary btn-sm w-100">조회</button>
          </div>
        </div>
      </div>
    </section>

    <section class="chart-display-section">
      <div v-if="spot.isLoadingData" class="loading-overlay text-center py-5">
        <div class="spinner-border text-dark" role="status" style="width: 3rem; height: 3rem;">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 mb-0 text-muted">시세 정보를 불러오는 중입니다...</p>
      </div>
      
      <div v-show="!spot.isLoadingData && currentDisplayParameters.dates && currentDisplayParameters.dates.length > 0" ref="chartRef" class="chart-render-area" />
      
      <div v-if="!spot.isLoadingData && (!currentDisplayParameters.dates || currentDisplayParameters.dates.length === 0)" class="no-data-message text-center text-muted py-5">
        <p>조회된 데이터가 없습니다. 기간 및 자산을 선택 후 "조회" 버튼을 눌러주세요.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, reactive, computed } from "vue"; 
import Plotly from "plotly.js-dist-min";
import { useSpotStore } from "@/features/spot/store/spotStore";

const spot = useSpotStore();
const chartRef = ref(null);
const selectedPeriod = ref("1y");

const tempSpotParameters = reactive({
  start: '',
  end: '',
  asset: 'gold' 
});

const currentDisplayParameters = reactive({
  dates: computed(() => spot.dates),
  prices: computed(() => spot.prices),
  asset: computed(() => spot.asset)
});

function selectPeriod(p) {
  const endDate = new Date();
  let startDate = new Date(endDate);

  switch (p) {
    case "1m": startDate.setMonth(endDate.getMonth() - 1); break;
    case "3m": startDate.setMonth(endDate.getMonth() - 3); break;
    case "1y": startDate.setFullYear(endDate.getFullYear() - 1); break;
    case "3y": startDate.setFullYear(endDate.getFullYear() - 3); break;
  }

  tempSpotParameters.start = startDate.toISOString().slice(0, 10);
  tempSpotParameters.end = endDate.toISOString().slice(0, 10);
  selectedPeriod.value = p;
}

function applyParametersAndLoadData() {
  spot.start = tempSpotParameters.start;
  spot.end = tempSpotParameters.end;
  spot.asset = tempSpotParameters.asset;
  spot.loadData(); 
}

watch([
  () => currentDisplayParameters.dates,
  () => currentDisplayParameters.prices,
  () => currentDisplayParameters.asset
], () => {
  if (spot.isLoadingData) return; 

  if (!chartRef.value || !currentDisplayParameters.dates || currentDisplayParameters.dates.length === 0) {
    if (chartRef.value) Plotly.purge(chartRef.value); 
    return;
  }

  const traceColor = currentDisplayParameters.asset === "gold" ? '#B8860B' : '#708090'; 
  const assetName = currentDisplayParameters.asset === "gold" ? "금 시세" : "은 시세";

  Plotly.react(
    chartRef.value,
    [{
      x: currentDisplayParameters.dates,
      y: currentDisplayParameters.prices,
      mode: "lines", 
      type: 'scatter',
      name: assetName,
      line: { color: traceColor, width: 2.5 }, 
    }],
    { 
      xaxis: { 
        title: { text: "날짜", font: { size: 13, color: '#555' } },
        type: 'date',
        gridcolor: '#f0f0f0', 
        zerolinecolor: '#ddd',
        linecolor: '#ddd',
      },
      yaxis: {
        title: { text: "시세 (KRW/g)", font: { size: 13, color: '#555' } },
        tickformat: ",.0f", 
        gridcolor: '#f0f0f0',
        zerolinecolor: '#ddd',
        linecolor: '#ddd',
      },
      margin: { t: 20, r: 20, b: 60, l: 60 }, 
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {
        family: '"Pretendard", Arial, sans-serif',
        size: 11,
        color: '#333'
      },
      hovermode: 'x unified',
      autosize: true, 
    },
    { responsive: true, displaylogo: false }
  );
}, { deep: true });

onMounted(() => {
  if (!tempSpotParameters.asset) { 
    tempSpotParameters.asset = 'gold';
  }
  selectPeriod(selectedPeriod.value); 
  
  if (chartRef.value) {
      Plotly.purge(chartRef.value);
  }
});
</script>

<style scoped>
.spot-view-container {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f4f6f8; 
  padding-top: 2rem;
  padding-bottom: 3rem;
  min-height: calc(100vh - 56px); 
}

.view-header .page-main-title {
  font-weight: 600;
  color: #212529;
  text-align: center; 
  margin-bottom: 1.8rem; 
}

.controls-section.card {
  border: 1px solid #e0e0e0; 
  border-radius: 0.375rem; 
  background-color: #fff;
}
.card-body {
  padding: 1.8rem; 
}

.control-label { 
  font-size: 0.875rem;
  font-weight: 500;
  color: #495057;
}

.period-button-group .btn {
  font-size: 0.85rem;
  padding: 0.4rem 0.9rem;
  font-weight: 500;
}
.btn-dark { 
  background-color: #343a40;
  border-color: #343a40;
  color: #fff;
}
.btn-dark:hover {
  background-color: #23272b;
  border-color: #1d2124;
}
.btn-outline-secondary { 
  color: #6c757d;
  border-color: #ced4da;
}
.btn-outline-secondary:hover {
  background-color: #e9ecef;
  color: #495057;
}

.control-divider {
  border-top: 1px solid #ebebeb; 
}

.filter-input-group .form-control-sm {
  font-size: 0.9rem;
  padding: 0.45rem 0.75rem; 
}

.asset-selector-group .form-check-label {
  font-size: 0.9rem;
  color: #333;
}
.asset-selector-group .form-check-inline {
  margin-right: 1.2rem;
}
.asset-selector-group .form-check-input:checked {
  background-color: #343a40; 
  border-color: #343a40;
}

.fetch-button-wrapper {
  padding-top: 1.45rem; 
}
.fetch-button-wrapper .btn-primary {
  background-color: #0062cc; 
  border-color: #005cbf;
  font-weight: 500;
  font-size: 0.9rem;
}
.fetch-button-wrapper .btn-primary:hover {
  background-color: #004a99;
  border-color: #004085;
}

.chart-display-section {
  background-color: #ffffff;
  padding: 1.5rem; 
  border-radius: 0.375rem;
  border: 1px solid #e0e0e0;
  margin-top: 2rem;
  min-height: 500px; 
  display: flex; 
  flex-direction: column;
  justify-content: center; 
}

.loading-overlay {
}

.chart-render-area {
  width: 100%;
  height: 480px; 
}

.no-data-message {
}
</style>