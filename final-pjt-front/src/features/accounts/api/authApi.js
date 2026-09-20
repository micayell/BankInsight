import api from '../../shared/api/api.js';

export const authApi = {
  // 로그인 & 회원가입
  login: (credentials) => api.post('/dj-rest-auth/login/', credentials),
  signup: (userData) => api.post('/dj-rest-auth/registration/', userData),
  logout: () => api.post('/dj-rest-auth/logout/'),
  
  // 프로필 관련
  getProfile: (username) => api.get(`/accounts/profile/${username}/`),
  updateProfile: (username, data) => api.put(`/accounts/profile/${username}/`, data),
};