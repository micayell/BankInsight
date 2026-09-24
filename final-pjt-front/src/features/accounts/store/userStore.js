import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import swal from 'sweetalert';
import router from '@/app/index.js';
import { getBankLogoUrl } from '@/features/shared/utils/bankImageLoader.js';
import { authApi } from '@/features/accounts/api/authApi.js';

export const useUserStore = defineStore(
  'user',
  () => {
    const token = ref(localStorage.getItem('token') || null);
    const userInfo = ref(JSON.parse(localStorage.getItem('userInfo')) || null);
    const userProfile = ref(null);
    const isLogin = computed(() => !!token.value && !!userInfo.value?.username);

    const setToken = k => { token.value = k; localStorage.setItem('token', k); };
    const setUserInfoState = (data) => {
      if (data && typeof data === 'object') {
        userInfo.value = data;
        localStorage.setItem('userInfo', JSON.stringify(data));
      } else {
        userInfo.value = null;
        localStorage.removeItem('userInfo');
        console.warn("setUserInfoState: 유효하지 않은 사용자 정보가 전달되었습니다", data);
      }
    };
    const removeTokenAndUserInfo = () => {
      token.value = null;
      userInfo.value = null;
      userProfile.value = null;
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
    };

    const createUser = async payload => {
      try {
        const response = await authApi.signup(payload);
        swal('회원가입 성공!', '입력하신 이메일로 인증 메일이 발송되었습니다. 이메일 인증 후 로그인해주세요.', 'success');
        router.push({ name: 'login' });
        return response.data;
      } catch (error) {
        console.error("회원가입 실패 (userStore):", error.response?.data || error.message);
        const errorMessages = [];
        if (error.response && error.response.data) {
          for (const key in error.response.data) {
            if (Array.isArray(error.response.data[key])) {
              errorMessages.push(`${key}: ${error.response.data[key].join(', ')}`);
            } else {
              errorMessages.push(`${key}: ${error.response.data[key]}`);
            }
          }
        }
        swal('오류', `회원가입에 실패했습니다: ${errorMessages.join('\\n') || error.message}`, 'error');
        throw error;
      }
    };

    const login = async ({ username, password }) => {
      let response;
      try {
        response = await authApi.login({ username, password });
      } catch (error) {
        handleLoginError(error);
        throw error;
      }

      console.log("로그인 API 응답:", response.data);

      if (response.data && response.data.key && response.data.user && typeof response.data.user.username === 'string') {
        setToken(response.data.key);
        setUserInfoState(response.data.user);
        try {
          await getProfile(response.data.user.username);
        } catch (e) {
             // profile 에러 무시 등 처리
        }
        swal('환영합니다.', '로그인에 성공했습니다.', 'success');
        router.push('/');
        return response.data;
      } else {
        console.error("로그인 응답 형식 오류: 'key' 또는 'user' 객체 또는 'user.username'이 응답에 없습니다.", response.data);
        const formatError = new Error("로그인 응답 형식이 올바르지 않습니다. (key/user/username 누락)");
        handleLoginError(formatError);
        throw formatError;
      }
    };

    const handleLoginError = (error) => {
      console.error("로그인 실패 (userStore):", error.response?.data || error.message, error);
      removeTokenAndUserInfo();
      let swalErrorMessage = '로그인에 실패했습니다.';
      if (error.message === "로그인 응답 형식이 올바르지 않습니다. (key/user/username 누락)") {
          swalErrorMessage = error.message + " 관리자에게 문의하세요.";
      } else if (error.response?.data?.non_field_errors?.[0]) {
          swalErrorMessage += `: ${error.response.data.non_field_errors[0]}`;
      } else if (error.message) {
          swalErrorMessage += `: ${error.message}`;
      }
      swal('오류', swalErrorMessage, 'error');
    };

    const loginUser = p => login(p);

    const logout = async () => {
      try {
        if (token.value) {
            await authApi.logout();
        }
      } catch (error) {
        console.error("로그아웃 API 호출 실패 (무시하고 로컬 로그아웃 진행):", error.response?.data || error.message);
      } finally {
        removeTokenAndUserInfo();
        swal('안녕히가세요!', '로그아웃 되었습니다.', 'success');
        router.push({ name: 'home' });
      }
    };
    const logoutUser = () => logout();

    const getProfile = async targetUsername => {
      const usernameToFetch = targetUsername || (userInfo.value ? userInfo.value.username : null);

      if (typeof usernameToFetch !== 'string' || !usernameToFetch.trim()) {
        console.error(`getProfile: 유효하지 않은 사용자 이름으로 프로필을 조회할 수 없습니다. (입력값: ${usernameToFetch})`);
        if (isLogin.value) {
          swal("오류", "사용자 정보를 정확히 가져올 수 없습니다. 다시 로그인해주세요. (ERR_GP_INVALID_UN)", "error")
            .then(() => logout());
        }
        throw new Error(`유효하지 않은 사용자 이름: ${usernameToFetch}`);
      }

      console.log(`getProfile: "${usernameToFetch}"의 프로필 정보 요청 시작`);
      try {
        const { data, status } = await authApi.getProfile(usernameToFetch);
        console.log(`getProfile: "${usernameToFetch}" 프로필 정보 수신 성공 (상태 코드: ${status})`);

        const processedData = { ...data };
        if (processedData.interested_deposits) {
          processedData.interested_deposits = processedData.interested_deposits.map(item => ({
            ...item,
            logoUrl: getBankLogoUrl(item.kor_co_nm)
          }));
        }
        if (processedData.interested_savings) {
          processedData.interested_savings = processedData.interested_savings.map(item => ({
            ...item,
            logoUrl: getBankLogoUrl(item.kor_co_nm)
          }));
        }

        userProfile.value = processedData;
        return processedData;
      } catch (error) {
        console.error(
            `getProfile ("${usernameToFetch}") 실패:`,
            error.response ?
                { status: error.response.status, data: error.response.data } :
                error.message
        );
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
            swal("인증 오류", "세션이 만료되었거나 권한이 없습니다. 다시 로그인해주세요.", "error")
              .then(() => logout());
        }
        throw error;
      }
    };

    const updateProfile = async (payload, targetUsername) => {
      const usernameToUpdate = targetUsername || (userInfo.value ? userInfo.value.username : null);
      if (!usernameToUpdate) {
        swal('오류', '프로필을 업데이트할 사용자 정보가 없습니다.', 'error');
        throw new Error("업데이트할 사용자 이름이 없습니다.");
      }

      try {
        const { data } = await authApi.updateProfile(usernameToUpdate, payload);
        await getProfile(usernameToUpdate);
        swal('성공', '프로필이 수정되었습니다.', 'success');
        return data;
      } catch (error) {
        console.error(`프로필 수정 실패 (${usernameToUpdate}):`, error.response?.data || error.message);
        const errorDetail = error.response?.data;
        let errorMessage = "프로필 수정에 실패했습니다.";
        if (typeof errorDetail === 'object' && errorDetail !== null) {
            errorMessage += Object.entries(errorDetail).map(([key, value]) => `\n- ${key}: ${Array.isArray(value) ? value.join(', ') : value}`).join('');
        } else if (typeof errorDetail === 'string') {
            errorMessage += `\n${errorDetail}`;
        }
        swal('오류', errorMessage, 'error');
        throw error;
      }
    };

    return {
      token, isLogin, userInfo, userProfile,
      createUser, login, loginUser, logout, logoutUser,
      getProfile, updateProfile,
      setToken,
      removeTokenAndUserInfo,
      setUserInfoState,
    };
  },
  { persist: {
      storage: localStorage,
      paths: ['token', 'userInfo'],
    }
  }
);