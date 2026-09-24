import { defineStore } from 'pinia';
import { productApi } from '@/features/products/api/productApi.js';
import swal from 'sweetalert';
import { getBankLogoUrl } from '@/features/shared/utils/bankImageLoader.js';

export const useSavingStore = defineStore('saving', {
  state: () => ({
    savings: [],
    currentSaving: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchSavings() {
      this.loading = true;
      this.error = null;
      try {
        let { data } = await productApi.getSavings();
        if (!data.length) {
          await this.loadSavings();
          data = (await productApi.getSavings()).data;
        }
        this.savings = data.map(product => ({
          ...product,
          logoUrl: getBankLogoUrl(product.kor_co_nm)
        }));
      } catch (e) {
        this.error = e;
        console.error("적금 목록 로드 실패:", e.response?.data || e.message);
      } finally {
        this.loading = false;
      }
    },

    async fetchSavingDetail(code) {
      this.loading = true;
      this.currentSaving = null;
      this.error = null;
      try {
        const { data } = await productApi.getSavingDetail(code);
        this.currentSaving = {
          ...data,
          logoUrl: getBankLogoUrl(data.kor_co_nm)
        };
      } catch (e) {
        this.error = e;
        console.error(`적금 상세(${code}) 로드 실패:`, e.response?.data || e.message);
      } finally {
        this.loading = false;
      }
    },

    async likeSaving (code) {
      try {
        const { data } = await productApi.likeSaving(code);

        if (this.currentSaving && this.currentSaving.fin_prdt_cd === code) {
          this.currentSaving.is_liked = data.is_liked;
        }
        swal({
          title: data.status === 'liked' ? "관심상품 등록!" : "관심상품 해제",
          text: data.message,
          icon: data.status === 'liked' ? "success" : "info",
        });
        return data;
      } catch (error) {
        console.error("적금 관심상품 등/해제 실패:", error.response?.data || error.message);
        swal("오류", `작업에 실패했습니다: ${error.response?.data?.detail || error.message}`, "error");
        throw error;
      }
    },

    async loadSavings (page = 1) {
      this.loading = true;
      try {
        const { data } = await productApi.loadSavings(page);
        console.log("적금 상품 DB 적재 결과:", data.detail);
        return data.detail;
      } catch (e) {
        this.error = e;
        console.error("적금 상품 DB 적재 실패:", e.response?.data || e.message);
        throw e;
      } finally {
        this.loading = false;
      }
    },
  },
});