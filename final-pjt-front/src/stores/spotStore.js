import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/apis/api";
import dayjs from "dayjs";

export const useSpotStore = defineStore("spot", () => {
  const start = ref("");
  const end = ref("");
  const asset = ref("gold");    
  const rawData = ref([]);       
  const loading = ref(false);
  const error = ref(null);

  function setPeriod(key) {
    const today = dayjs();
    let from;
    switch (key) {
      case "1m":
        from = today.subtract(1, "month");
        break;
      case "3m":
        from = today.subtract(3, "month");
        break;
      case "1y":
        from = today.subtract(1, "year");
        break;
      case "3y":
        from = today.subtract(3, "year");
        break;
      default:
        from = today.subtract(1, "month");
    }
    start.value = from.format("YYYY-MM-DD");
    end.value   = today.format("YYYY-MM-DD");
    loadData();
  }

  async function loadData() {
    loading.value = true;
    error.value   = null;

    const params = {};
    if (start.value) params.start = start.value;
    if (end.value)   params.end   = end.value;
    params.metal = asset.value === "gold" ? "금" : "은";

    try {
      const res = await api.get(`/spot/`, { params });
      rawData.value = Array.isArray(res.data) ? res.data : [];
    } catch (e) {
      error.value = e;
      rawData.value = [];
    } finally {
      loading.value = false;
    }
  }

  const dates  = computed(() => rawData.value.map(i => i.date));
  const prices = computed(() => rawData.value.map(i => i.price));

  return {
    start,
    end,
    asset,
    rawData,
    loading,
    error,
    dates,
    prices,
    setPeriod,
    loadData,
  };
});
