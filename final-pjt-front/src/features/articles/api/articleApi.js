import api from '../../shared/api/api.js';

export const articleApi = {
  getList: () => api.get('/articles/'),
  getDetail: (id) => api.get(`/articles/${id}/`),
  create: (data) => api.post('/articles/', data),
  update: (id, data) => api.put(`/articles/${id}/`, data),
  delete: (id) => api.delete(`/articles/${id}/`),
};