import api from '../../shared/api/api.js';

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
};