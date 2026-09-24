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
            <span class="material-symbols-outlined me-1 align-middle icon-state">
              {{ isSubscribed ? '관심 해제' : '관심 등록' }}
            </span>
          </button>
        </div>
      </header>

      <section class="product-info mb-4">
        <h2 class="section-title h5 mb-3">상품 기본 정보</h2>
        <div class="row g-3 item-list">
          <div class="col-md-6 info-item">
            <span class="info-label">가입 방법:</span>
            <span class="info-value">{{ product.join_way || '-' }}</span>
          </div>
          <div class="col-md-6 info-item">
            <span class="info-label">대출 한도:</span>
            <span class="info-value">{{ product.loan_lmt || '-' }}</span>
          </div>
          <div class="col-12 info-item" v-if="product.loan_inci_expn">
            <span class="info-label">부대 비용:</span>
            <span class="info-value" style="white-space: pre-wrap;">{{ product.loan_inci_expn }}</span>
          </div>
          <div class="col-12 info-item" v-if="product.erly_rpay_fee">
            <span class="info-label">중도상환수수료:</span>
            <span class="info-value" style="white-space: pre-wrap;">{{ product.erly_rpay_fee }}</span>
          </div>
          <div class="col-12 info-item" v-if="product.dly_rate">
            <span class="info-label">연체 이자율:</span>
            <span class="info-value" style="white-space: pre-wrap;">{{ product.dly_rate }}</span>
          </div>
        </div>
      </section>

      <section class="product-options mb-4">
        <h2 class="section-title h5 mb-3">금리 옵션 상세</h2>
        <div v-if="product.options && product.options.length > 0" class="list-group">
          <div v-for="opt in product.options" :key="opt.id" class="list-group-item option-item">
            <div class="fw-semibold option-header">{{ opt.mrtg_type_nm }} / {{ opt.rpay_type_nm }}</div>
            <div class="option-rates">
              <span class="rate-label">대출금리유형: </span><strong class="rate-value">{{ opt.lend_rate_type_nm }}</strong><br>
              <span class="rate-label">최저 금리: </span><strong class="rate-value">{{ formatRate(opt.lend_rate_min) }}%</strong>
              <span class="rate-label ms-3">최고 금리: </span><strong class="rate-value">{{ formatRate(opt.lend_rate_max) }}%</strong>
              <span class="rate-label ms-3">평균 금리: </span><strong class="rate-value">{{ formatRate(opt.lend_rate_avg) }}%</strong>
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
  name: 'MortgageDetailView',
  props: ['code'],
  data() {
    return {
      product: null,
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
      this.isLoading = true; this.product = null;
      const base = 'http://127.0.0.1:8000/financial-products';

      const headers = {};
      if (this.userStore.isLogin && this.userStore.token) {
        headers.Authorization = `Token ${this.userStore.token}`;
      }

      axios.get(`${base}/mortgages/${code}/`, { headers })
        .then((productRes) => { 
          this.product = productRes.data; 
          this.isSubscribed = this.product.is_liked;
        })
        .catch(err => { console.error(`상품 실패:`, err); this.product = null; })
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
        `${base}/mortgages/${this.code}/like/`, 
        null,
        { headers: { Authorization: `Token ${token}` } }
      )
        .then(res => {
          const isLikedAfterAction = res.data.is_liked; 
          swal("알림", res.data.message, isLikedAfterAction ? "success" : "info");
          this.isSubscribed = isLikedAfterAction; 
        })
        .catch(err => {
          swal("오류", "오류가 발생했습니다.", "error");
        });
    },
    formatRate(rate) {
      const parsedRate = parseFloat(rate);
      if (!isNaN(parsedRate)) return parsedRate.toFixed(2);
      return '-';
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
.section-title { color: #343a40; font-weight: 500; padding-bottom: 0.6rem; border-bottom: 2px solid #0056b3; display: inline-block; margin-bottom: 1.25rem !important; }
.product-info .info-item { font-size: 0.95rem; color: #495057; padding: 0.4rem 0; display: flex; }
.product-info .info-label { color: #212529; font-weight: 500; min-width: 120px; flex-shrink: 0; }
.product-options .list-group-item.option-item { background-color: #fff; border-color: #e9ecef; padding: 0.9rem 1.1rem; margin-bottom: 0.5rem; border-radius: 0.25rem; }
.option-header { font-size: 1rem; color: #0056b3; }
.option-rates { font-size: 0.9rem; color: #343a40; }
.option-rates .rate-label { color: #6c757d; }
.page-navigation-actions .btn-outline-secondary { font-weight: 500; padding: 0.6rem 1.75rem; }
</style>