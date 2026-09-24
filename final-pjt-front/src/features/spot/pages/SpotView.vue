<template>
  <div class="container spot-view-container py-4">
    <header class="view-header mb-4">
      <h1 class="h3 page-main-title">금/석유 시세 변동 조회</h1>
    </header>

    <section class="controls-section bg-white border-0 shadow-sm rounded-4 p-3 mb-4">
      <div class="p-2">
        <div class="mb-3 period-selector">
          <label class="form-label d-block mb-2 control-label">기간 선택</label>
          <div class="btn-group period-button-group" role="group">
            <button type="button" @click="selectPeriod('1m')" class="btn" :class="selectedPeriod === '1m' ? 'btn-primary text-white' : 'btn-light text-muted border-0 bg-white'">
              1개월
            </button>
            <button type="button" @click="selectPeriod('3m')" class="btn" :class="selectedPeriod === '3m' ? 'btn-primary text-white' : 'btn-light text-muted border-0 bg-white'">
              3개월
            </button>
            <button type="button" @click="selectPeriod('1y')" class="btn" :class="selectedPeriod === '1y' ? 'btn-primary text-white' : 'btn-light text-muted border-0 bg-white'">
              1년
            </button>
            <button type="button" @click="selectPeriod('3y')" class="btn" :class="selectedPeriod === '3y' ? 'btn-primary text-white' : 'btn-light text-muted border-0 bg-white'">
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
              <input class="form-check-input" type="radio" id="oilRadio" value="oil" v-model="tempSpotParameters.asset" />
              <label class="form-check-label" for="oilRadio">석유</label>
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

  const traceColor = currentDisplayParameters.asset === "gold" ? '#B8860B' : '#000000'; 
  const assetName = currentDisplayParameters.asset === "gold" ? "금 시세" : "석유 시세";
  const yAxisTitle = currentDisplayParameters.asset === "gold" ? "시세 (KRW/g)" : "할인평균단가 (원)";

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
        title: { text: yAxisTitle, font: { size: 13, color: '#555' } },
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
  max-width: 1000px;
}
.page-main-title {
  font-weight: 700;
  font-size: 2rem;
  color: #191f28;
}
.control-label {
  font-weight: 600;
  color: #4e5968;
}
.btn-group .btn {
  border-radius: 8px !important;
  margin-right: 8px;
}
.form-control {
  border-radius: 12px;
  border: 1px solid #e5e8eb;
  padding: 0.75rem 1rem;
}
.toss-chart-card {
  border-radius: 16px;
}
</style>