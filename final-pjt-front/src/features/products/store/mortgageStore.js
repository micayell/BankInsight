import { defineStore } from 'pinia';
import { productApi } from '@/features/products/api/productApi.js';
import swal from 'sweetalert';
import { getBankLogoUrl } from '@/features/shared/utils/bankImageLoader.js';

export const useMortgageStore = defineStore('mortgage', {
  state: () => ({
    mortgages: [],
    currentMortgage: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchMortgages() {
      this.loading = true; this.error = null;
      try {
        let { data } = await productApi.getMortgages();
        this.mortgages = data.map(product => ({ ...product, logoUrl: getBankLogoUrl(product.kor_co_nm) }));
      } catch (e) {
        this.error = e; console.error('주택담보대출 로드 실패', e);
      } finally { this.loading = false; }
    },
    async loadMortgages() {
      try { await productApi.loadMortgages(); } catch(e) { console.error('DB 저장 실패', e); }
    },
    async getMortgageDetail(code) {
      this.loading = true; this.error = null;
      try {
        let { data } = await productApi.getMortgageDetail(code);
        
        let logoUrl = '/icons/bank/default.png';
        if (data.kor_co_nm) {
          logoUrl = getBankLogoUrl(data.kor_co_nm);
        }
        
        this.currentMortgage = { ...data, logoUrl };
        return this.currentMortgage;
      } catch (e) {
        this.error = e; 
        console.error('상세 조회 실패', e);
      } finally { this.loading = false; }
    },
    async likeMortgage(code) {
      try {
        await productApi.likeMortgage(code);
      } catch (e) {
        console.error('찜하기 실패:', e);
        throw e;
      }
    }
  }
});