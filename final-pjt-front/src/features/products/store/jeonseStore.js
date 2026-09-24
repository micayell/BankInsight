import { defineStore } from 'pinia';
import { productApi } from '@/features/products/api/productApi.js';
import swal from 'sweetalert';
import { getBankLogoUrl } from '@/features/shared/utils/bankImageLoader.js';

export const useJeonseStore = defineStore('jeonse', {
  state: () => ({
    jeonses: [],
    currentJeonse: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchJeonses() {
      this.loading = true; this.error = null;
      try {
        let { data } = await productApi.getJeonses();
        this.jeonses = data.map(product => ({ ...product, logoUrl: getBankLogoUrl(product.kor_co_nm) }));
      } catch (e) {
        this.error = e; console.error('전세자금대출 로드 실패', e);
      } finally { this.loading = false; }
    },
    async loadJeonses() {
      try { await productApi.loadJeonses(); } catch(e) { console.error('DB 저장 실패', e); }
    }
  }
});