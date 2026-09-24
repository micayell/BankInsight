import api from '../../shared/api/api.js';

export const authApi = {
  // 로그인 & 회원가입
  login: (credentials) => api.post('/dj-rest-auth/login/', credentials),
  signup: (userData) => api.post('/dj-rest-auth/registration/', userData),
  logout: () => api.post('/dj-rest-auth/logout/'),
  
  // 프로필 관련
  getProfile: (username) => api.get(`/accounts/profile/${username}/`),
  updateProfile: (username, data) => api.put(`/accounts/profile/${username}/`, data),
  deleteAccount: (username) => api.delete(`/accounts/user/delete/${username}/`),

  // 비밀번호 찾기
  resetPassword: (email) => api.post('/dj-rest-auth/password/reset/', { email }),
  resetPasswordConfirm: (data) => api.post('/dj-rest-auth/password/reset/confirm/', data),

  // 이메일 인증
  sendVerifyEmail: (email) => api.post('/accounts/email-verify/send/', { email }),
  confirmVerifyEmail: (email, code) => api.post('/accounts/email-verify/confirm/', { email, code }),
};