import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/features/shared/api/api.js';

export const useExchangeStore = defineStore('exchange', () => {
  const todayRates = ref([]);
  const yesterdayRates = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  const fetchRates = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const [todayResponse, yesterdayResponse] = await Promise.all([
        api.get('/exchange/today/'),
        api.get('/exchange/yesterday/')
      ]);

      if (Array.isArray(todayResponse.data) && todayResponse.data.length > 0 && todayResponse.data[0].result !== 1) {
          const errorMsg = todayResponse.data[0].error || todayResponse.data[0].msg || '오늘 환율 정보 로드 중 오류';
          error.value = `오늘 환율 API 오류: ${errorMsg} (코드: ${todayResponse.data[0].result})`;
          todayRates.value = [];
          yesterdayRates.value = [];
          return;
      }
      if (Array.isArray(yesterdayResponse.data) && yesterdayResponse.data.length > 0 && yesterdayResponse.data[0].result !== 1) {
          const errorMsg = yesterdayResponse.data[0].error || yesterdayResponse.data[0].msg || '전 영업일 환율 정보 로드 중 오류';
          error.value = `전 영업일 환율 API 오류: ${errorMsg} (코드: ${yesterdayResponse.data[0].result})`;
          todayRates.value = [];
          yesterdayRates.value = [];
          return;
      }
      
      todayRates.value = Array.isArray(todayResponse.data) ? todayResponse.data : [];
      yesterdayRates.value = Array.isArray(yesterdayResponse.data) ? yesterdayResponse.data : [];

    } catch (e) {
      if (e.response && e.response.status === 404) {
        console.error("환율 정보 가져오기 실패 (404 Not Found): 백엔드가 외부 API로부터 데이터를 가져오지 못했습니다.", e.response.data);
        error.value = '현재 환율 정보를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.';
      } else {
        console.error("환율 정보 가져오기 실패 (exchangeStore):", e);
        error.value = '환율 정보를 가져오는 중 예상치 못한 오류가 발생했습니다.';
      }
      todayRates.value = [];
      yesterdayRates.value = [];
    } finally {
      isLoading.value = false;
    }
  };

  return {
    todayRates,
    yesterdayRates,
    isLoading,
    error,
    fetchRates
  };
});