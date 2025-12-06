<template>
  <div>
    <h2>은 시세</h2>
    <canvas ref="silverCanvas"></canvas>
  </div>
</template>

<script>
import axios from "axios";
import { Chart, registerables } from "chart.js"; // Chart.js v3+
Chart.register(...registerables);

export default {
  name: "SilverChart",
  data() {
    return {
      silverPrices: [],
      chartInstance: null,
    };
  },
  async mounted() {
    await this.fetchSilverPrices();

    // DOM 업데이트가 완료된 후 차트 렌더링을 시도 (ref 사용 시 nextTick이 더 안정적일 수 있음)
    this.$nextTick(() => {
      if (this.silverPrices && this.silverPrices.length > 0) {
        this.renderChart();
      } else {
        this.displayNoDataMessage();
        console.warn("[silver.vue] No data to render silver chart after fetch.");
      }
    });
  },
  methods: {
    async fetchSilverPrices() {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/spot/api/silver-prices/"
        );
        console.log("[silver.vue] Silver API response status:", response.status);
        console.log(
          "[silver.vue] Raw Silver API response.data (first 3):",
          JSON.parse(JSON.stringify(response.data.slice(0, 3))) // 전체 데이터 로그는 너무 길 수 있으므로 일부만
        );

        if (Array.isArray(response.data)) {
          this.silverPrices = response.data;
        } else {
          console.error(
            "[silver.vue] Silver API did not return an array. Received:",
            response.data
          );
          this.silverPrices = [];
        }
      } catch (error) {
        console.error("[silver.vue] Error fetching silver prices:", error);
        if (error.response) {
          console.error("[silver.vue] Error response data:", error.response.data);
          console.error("[silver.vue] Error response status:", error.response.status);
        }
        this.silverPrices = [];
      }
    },

    renderChart() {
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      // ref를 사용하여 canvas 요소 가져오기
      const canvas = this.$refs.silverCanvas;
      if (!canvas) {
        console.error("[silver.vue] Canvas element (this.$refs.silverCanvas) not found.");
        return;
      }
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        console.error("[silver.vue] Failed to get 2D context from canvas.");
        return;
      }

      const labels = this.silverPrices.map((price) => price.date);
      const buyData = this.silverPrices.map((price) => {
        const value = parseFloat(price.buy_price_per_don);
        return isNaN(value) ? null : value;
      });
      const sellData = this.silverPrices.map((price) => {
        const value = parseFloat(price.sell_price_per_don);
        return isNaN(value) ? null : value;
      });

      console.log(
        "[silver.vue] Data for Chart - Labels (first 5):",
        JSON.stringify(labels.slice(0, 5))
      );
      console.log(
        "[silver.vue] Data for Chart - Buy Data (first 5, after parseFloat):",
        JSON.stringify(buyData.slice(0, 5))
      );
      console.log(
        "[silver.vue] Data for Chart - Sell Data (first 5, after parseFloat):",
        JSON.stringify(sellData.slice(0, 5))
      );

      const hasValidBuyData = buyData.some(d => d !== null);
      const hasValidSellData = sellData.some(d => d !== null);

      if (labels.length === 0 || (!hasValidBuyData && !hasValidSellData)) {
        console.warn("[silver.vue] No valid data points to plot after processing.");
        this.displayNoDataMessage("차트를 그릴 유효한 데이터가 없습니다.");
        return;
      }

      this.chartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "내가 살때 (원/3.75g)",
              data: buyData,
              borderColor: "rgb(255, 99, 132)",
              backgroundColor: "rgba(255, 99, 132, 0.5)",
              tension: 0.1,
              spanGaps: true, // null 데이터 지점을 선으로 이어줌 (선택 사항)
            },
            {
              label: "내가 팔때 (원/3.75g)",
              data: sellData,
              borderColor: "rgb(54, 162, 235)",
              backgroundColor: "rgba(54, 162, 235, 0.5)",
              tension: 0.1,
              spanGaps: true, // null 데이터 지점을 선으로 이어줌 (선택 사항)
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: false,
              ticks: {
                callback: function(value) {
                  return value.toLocaleString(); // Y축 눈금에 콤마 추가
                }
              }
            },
            x: {
              ticks: {
                autoSkip: true,
                maxTicksLimit: 15, // X축 눈금 최대 개수 제한 (데이터 양에 따라 조절)
              }
            }
          },
          plugins: {
            tooltip: {
              mode: "index",
              intersect: false,
              callbacks: { // 툴팁 값에도 콤마 추가
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += context.parsed.y.toLocaleString();
                    }
                    return label;
                }
              }
            },
            title: {
              display: true,
              text: "일자별 은 시세 (3.75g 기준)",
            },
          },
        },
      });
    },

    displayNoDataMessage(message = "은 시세 데이터를 불러오지 못했거나 데이터가 없습니다.") {
      const canvas = this.$refs.silverCanvas;
      if (canvas) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.font = "16px Arial";
          ctx.textAlign = "center";
          ctx.fillStyle = "grey"; // 메시지 색상
          ctx.fillText(message, canvas.width / 2, canvas.height / 2);
        }
      }
    }
  },
};
</script>

<style scoped>
/* 필요한 스타일링 추가 */
div { /* 컴포넌트 루트 div에 대한 스타일 */
  width: 100%;
  max-width: 800px; /* 차트 최대 너비 */
  margin: 20px auto; /* 가운데 정렬 및 상하 여백 */
}
canvas {
  width: 100% !important; /* 부모 요소 너비에 맞춤 */
  height: auto !important; /* 종횡비에 따라 높이 자동 조절 */
  max-height: 400px; /* 차트 최대 높이 (선택 사항) */
}
</style>