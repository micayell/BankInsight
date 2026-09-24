import api from '@/features/shared/api/api.js';

const PREFIX = '/financial-products';

export const productApi = {
  // 예금 (Deposit)
  getDeposits: () => api.get(`${PREFIX}/deposits/`),
  getDepositDetail: (code) => api.get(`${PREFIX}/deposits/${code}/`),
  loadDeposits: (page = 1) => api.post(`${PREFIX}/load/deposits/?page=${page}`),
  likeDeposit: (code) => api.post(`${PREFIX}/deposits/${code}/like/`),

  // 적금 (Saving)
  getSavings: () => api.get(`${PREFIX}/savings/`),
  getSavingDetail: (code) => api.get(`${PREFIX}/savings/${code}/`),
  loadSavings: (page = 1) => api.post(`${PREFIX}/load/savings/?page=${page}`),
  likeSaving: (code) => api.post(`${PREFIX}/savings/${code}/like/`),

  // 주택담보대출 (Mortgage)
  getMortgages: () => api.get(`${PREFIX}/mortgages/`),
  getMortgageDetail: (code) => api.get(`${PREFIX}/mortgages/${code}/`),
  loadMortgages: () => api.post(`${PREFIX}/load/mortgages/`),
  likeMortgage: (code) => api.post(`${PREFIX}/mortgages/${code}/like/`),

  // 전세자금대출 (Jeonse)
  getJeonses: () => api.get(`${PREFIX}/jeonses/`),
  getJeonseDetail: (code) => api.get(`${PREFIX}/jeonses/${code}/`),
  loadJeonses: () => api.post(`${PREFIX}/load/jeonses/`),
  likeJeonse: (code) => api.post(`${PREFIX}/jeonses/${code}/like/`),

  // 추천상품 (Recommend)
  getRecommendFirstDeposit: (username) => api.get(`/products/recommend/deposit/${username}/`),
  getRecommendFirstSaving: (username) => api.get(`/products/recommend/saving/${username}/`),
  getRecommendSecondDeposit: (username) => api.get(`/products/recommend/deposit/second/${username}/`),
  getRecommendSecondSaving: (username) => api.get(`/products/recommend/saving/second/${username}/`),
};