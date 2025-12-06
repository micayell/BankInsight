import { defineStore } from 'pinia';
import api from '@/apis/api';
import swal from 'sweetalert';
import { getBankLogoUrl } from '@/utils/bankImageLoader';
const PREFIX = '/financial-products';

export const useDepositStore = defineStore('deposit', {
  state: () => ({
    deposits: [],
    currentDeposit: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchDeposits() {
      this.loading = true;
      this.error = null;
      try {
        let { data } = await api.get(`${PREFIX}/deposits/`);
        if (!data.length && PREFIX === '/financial-products') {
          await this.loadDeposits();
          data = (await api.get(`${PREFIX}/deposits/`)).data;
        }
        this.deposits = data.map(product => ({
          ...product,
          logoUrl: getBankLogoUrl(product.kor_co_nm)
        }));
      } catch (e) {
        this.error = e;
        console.error("예금 목록 로드 실패:", e.response?.data || e.message);
      } finally {
        this.loading = false;
      }
    },

    async fetchDepositDetail(code) {
      this.loading = true;
      this.currentDeposit = null;
      this.error = null;
      try {
        const { data } = await api.get(`${PREFIX}/deposits/${code}/`);
        this.currentDeposit = {
          ...data,
          logoUrl: getBankLogoUrl(data.kor_co_nm)
        };
      } catch (e) {
        this.error = e;
        console.error(`예금 상세(${code}) 로드 실패:`, e.response?.data || e.message);
      } finally {
        this.loading = false;
      }
    },

    async likeDeposit (code) {
      try {
        const { data } = await api.post(`${PREFIX}/deposits/${code}/like/`);

        if (this.currentDeposit && this.currentDeposit.fin_prdt_cd === code) {
          this.currentDeposit.is_liked = data.is_liked;
        }
        swal({
          title: data.status === 'liked' ? "관심상품 등록!" : "관심상품 해제",
          text: data.message,
          icon: data.status === 'liked' ? "success" : "info",
        });
        return data;
      } catch (error) {
        console.error("예금 관심상품 등록/해제 실패:", error.response?.data || error.message);
        swal("오류", `작업에 실패했습니다: ${error.response?.data?.detail || error.message}`, "error");
        throw error;
      }
    },

    async loadDeposits (page = 1) {
      this.loading = true;
      try {
        const { data } = await api.post(`${PREFIX}/load/deposits/?page=${page}`);
        console.log("예금 상품 DB 적재 결과:", data.detail);
        return data.detail;
      } catch (e) {
        this.error = e;
        console.error("예금 상품 DB 적재 실패:", e.response?.data || e.message);
        throw e;
      } finally {
        this.loading = false;
      }
    },
  },
});