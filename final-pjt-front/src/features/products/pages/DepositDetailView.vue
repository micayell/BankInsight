<template>
  <div class="container product-detail-page py-lg-5 py-4">
    <div v-if="isLoading && !product" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">상품 정보를 불러오는 중입니다...</p>
    </div>
    <div v-else-if="product && product.fin_prdt_cd" class="content-card p-4 p-md-5 shadow-sm">
      <header class="product-header border-bottom pb-3 mb-4">
        <div class="d-flex justify-content-between align-items-start flex-wrap">
          <div class="me-3">
            <h1 class="h3 fw-bold product-bank-name mb-1">{{ product.kor_co_nm }}</h1>
            <p class="h5 product-name text-muted mb-0">{{ product.fin_prdt_nm }}</p>
          </div>
          <button @click="subscribe" class="btn btn-sm subscribe-button mt-2 mt-md-0" 
                  :class="isSubscribed ? 'btn-outline-danger' : 'btn-outline-primary'"> 
            <span class="material-symbols-outlined me-1 align-middle icon-state" :class="{'is-filled': isSubscribed}">
            {{ isSubscribed ? '관심 해제' : '관심 등록' }}
             </span>
          </button>     
        </div>
      </header>

      <section class="product-info mb-4">
        <h2 class="section-title h5 mb-3">상품 기본 정보</h2>
        <div class="row g-3 item-list">
          <div class="col-md-6 info-item">
            <span class="info-label">기본 금리 (연):</span>
            <span class="info-value">{{ product.mtrt_int !== null ? product.mtrt_int : '-' }}%</span>
          </div>
          <div class="col-md-6 info-item">
            <span class="info-label">가입 방식:</span>
            <span class="info-value">{{ product.join_way || '-' }}</span>
          </div>
          <div class="col-12 info-item" v-if="product.spcl_cnd">
            <span class="info-label">우대 조건:</span>
            <span class="info-value">{{ product.spcl_cnd }}</span>
          </div>
          <div class="col-md-6 info-item" v-if="product.max_limit !== null && product.max_limit !== undefined">
            <span class="info-label">최대 한도:</span>
            <span class="info-value">{{ product.max_limit | number }}원</span>
          </div>
          <div class="col-12 info-item" v-if="product.join_member">
            <span class="info-label">가입 대상:</span>
            <span class="info-value">{{ product.join_member }}</span>
          </div>
           <div class="col-12 info-item" v-if="product.join_deny && product.join_deny !== '제한없음'">
            <span class="info-label">가입 제한:</span>
            <span class="info-value">{{ formatJoinDeny(product.join_deny) }}</span>
          </div>
          <div class="col-12 info-item" v-if="product.etc_note">
            <span class="info-label">기타 유의사항:</span>
            <span class="info-value">{{ product.etc_note }}</span>
          </div>
        </div>
      </section>

      <section class="product-options mb-4">
        <h2 class="section-title h5 mb-3">금리 옵션 상세</h2>
        <div v-if="options.length > 0" class="list-group">
          <div v-for="opt in options" :key="`${opt.intr_rate_type_nm}-${opt.save_trm}`" class="list-group-item option-item">
            <div class="fw-semibold option-header">{{ opt.intr_rate_type_nm }} ({{ opt.save_trm }}개월)</div>
            <div class="option-rates">
              <span class="rate-label">기본: </span><strong class="rate-value">{{ formatRate(opt.intr_rate) }}%</strong>
              <span class="rate-label ms-3">우대: </span><strong class="rate-value">{{ formatRate(opt.intr_rate2) }}%</strong>
            </div>
          </div>
        </div>
        <div v-else class="alert alert-secondary text-center py-4">
          금리 옵션 정보가 없습니다.
        </div>
      </section>

      <div class="page-navigation-actions text-center mt-5">
        <button @click="$router.back()" class="btn btn-outline-secondary px-4">뒤로 가기</button>
      </div>

    </div>
    <div v-else class="text-center py-5 mt-5">
      <p class="text-danger" v-if="!isLoading">상품 정보를 불러오지 못했거나, 해당 상품이 없습니다.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import swal from 'sweetalert';
import { useUserStore } from '@/features/accounts/store/userStore';

export default {
  name: 'DepositDetailView',
  props: ['code'],
  data() {
    return {
      product: null,
      options: [],
      isLoading: true,
      isSubscribed: false, 
      userStore: useUserStore(), 
    };
  },
  created() {
    this.fetchData(this.code);
  },
  watch: {
    code(newCode) {
      if (newCode) {
        this.fetchData(newCode);
      }
    },
    'userStore.isLogin'(isLoggedIn) {
      if (this.code) {
        this.fetchData(this.code);
      }
    }
  },
  methods: {
    fetchData(code) {
      if (!code) { this.isLoading = false; this.product = null; return; }
      this.isLoading = true; this.product = null; this.options = [];
      const base = 'http://127.0.0.1:8000/financial-products';

      const headers = {};
      if (this.userStore.isLogin && this.userStore.token) {
        headers.Authorization = `Token ${this.userStore.token}`;
      }

      const fetchProduct = axios.get(`${base}/deposits/${code}/`, { headers });
      const fetchOptions = axios.get(`${base}/deposits/${code}/options/`, { headers });
      
      Promise.all([fetchProduct, fetchOptions])
        .then(([productRes, optionsRes]) => { 
          this.product = productRes.data; 
          this.options = optionsRes.data;
          this.isSubscribed = this.product.is_liked;
        })
        .catch(err => { console.error(`예금 상품(code:${code}) 정보/옵션 실패:`, err); this.product = null; this.options = []; })
        .finally(() => { this.isLoading = false; });
    },
    subscribe() {
      const base = 'http://127.0.0.1:8000/financial-products';
      const token = this.userStore.token;

      if (!token) {
        swal("로그인 필요", "로그인이 필요한 기능입니다.", "warning", {
          buttons: { cancel: "닫기", login: { text: "로그인 하기", value: "login"}},
        }).then(value => { if (value === "login") this.$router.push({name: 'login'}); });
        return;
      }

      axios.post(
        `${base}/deposits/${this.code}/like/`, 
        null,
        { headers: { Authorization: `Token ${token}` } }
      )
        .then(res => {
          const isLikedAfterAction = res.data.is_liked; 
          const message = res.data.message || (isLikedAfterAction ? '관심 상품으로 등록되었습니다.' : '관심 상품 등록이 해제되었습니다.');
          
          swal("알림", message, isLikedAfterAction ? "success" : "info"); 
          this.isSubscribed = isLikedAfterAction; 
        })
        .catch(err => {
          console.error('관심상품 등록/해제 실패:', err.response?.data || err.message);
          let errorMsg = '요청 처리 중 오류가 발생했습니다.';
          if (err.response?.data?.detail) errorMsg = err.response.data.detail;
          else if (err.response?.data?.message) errorMsg = err.response.data.message;
          swal("오류", errorMsg, "error");
        });
    },
    formatRate(rate) {
      const parsedRate = parseFloat(rate);
      if (!isNaN(parsedRate)) {
        return parsedRate.toFixed(2);
      }
      return '-';
    },
    formatJoinDeny(value) {
        const denyMap = { '1': '제한없음', '2': '서민전용', '3': '일부제한' };
        return denyMap[value] || value;
    }
  },
  filters: {
    number(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '';
      return Number(val).toLocaleString();
    }
  }
};
</script>

<style scoped>
.product-detail-page { font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8f9fa; min-height: calc(100vh - 56px); }
.content-card { background-color: #fff; border: none; padding: 2rem; border-radius: 0.375rem; }
.product-header {}
.product-bank-name { font-weight: 600; color: #212529; }
.product-name { font-size: 1.25rem; font-weight: 400; }
.subscribe-button { font-weight: 500; font-size: 0.875rem; display: inline-flex; align-items: center; }
.subscribe-button .material-symbols-outlined { font-size: 1.1em; vertical-align: text-bottom; }
.subscribe-button .material-symbols-outlined.icon-filled-state { font-variation-settings: 'FILL' 1; } 
.section-title { color: #343a40; font-weight: 500; padding-bottom: 0.6rem; border-bottom: 2px solid #0056b3; display: inline-block; margin-bottom: 1.25rem !important; }
.product-info .info-item { font-size: 0.95rem; color: #495057; padding: 0.4rem 0; display: flex; }
.product-info .info-label { color: #212529; font-weight: 500; min-width: 120px; flex-shrink: 0; }
.product-options .list-group-item.option-item { background-color: #fff; border-color: #e9ecef; padding: 0.9rem 1.1rem; margin-bottom: 0.5rem; border-radius: 0.25rem; }
.option-header { font-size: 1rem; color: #0056b3; }
.option-rates { font-size: 0.9rem; color: #343a40; }
.option-rates .rate-label { color: #6c757d; }
.page-navigation-actions .btn-outline-secondary { font-weight: 500; padding: 0.6rem 1.75rem; }

</style>