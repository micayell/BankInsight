<template>
  <div class="container create-article-page py-4 article-update-view">
    <header class="view-header text-center mb-5">
      <h1 class="display-5 fw-bold">게시글 수정</h1>
    </header>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border" role="status" :style="{ color: 'var(--app-primary-color)' }">
        <span class="visually-hidden">게시글 정보를 불러오는 중...</span>
      </div>
      <p class="mt-3" :style="{ color: 'var(--app-text-medium)' }">게시글 정보를 불러오고 있습니다.</p>
    </div>

    <div v-else-if="fetchError" class="alert alert-danger text-center mx-auto my-4" style="max-width: 720px;">
      <p class="mb-1">{{ fetchError }}</p>
      <RouterLink v-if="props.id" :to="{ name: 'article-detail', params: { id: props.id } }" class="alert-link-custom">게시글로 돌아가기</RouterLink>
      <RouterLink v-else :to="{ name: 'article' }" class="alert-link-custom">목록으로</RouterLink>
    </div>
    
    <div v-else-if="!isAuthorized && userStore.isLogin && !isLoading" class="alert alert-warning text-center mx-auto my-4" style="max-width: 720px;">
      <p class="mb-1">이 게시글을 수정할 권한이 없습니다.</p>
      <RouterLink :to="{ name: 'article-detail', params: { id: props.id } }" class="alert-link-custom">게시글로 돌아가기</RouterLink>
    </div>

    <div v-else-if="articleToEdit" class="form-content-wrapper mx-auto">
      <form @submit.prevent="submitUpdate" class="article-creation-form">
        <div class="mb-4">
          <label for="title" class="form-label fs-5">제목</label>
          <input type="text" id="title" v-model.trim="title" class="form-control form-control-lg" required placeholder="제목을 입력하세요">
        </div>

        <div class="mb-4">
          <label for="content" class="form-label fs-5">내용</label>
          <textarea id="content" v-model.trim="content" class="form-control form-control-lg" rows="12" required placeholder="내용을 입력하세요"></textarea>
        </div>

        <div v-if="submitErrorMessage" class="alert alert-danger mt-3">
          {{ submitErrorMessage }}
        </div>

        <div class="d-flex justify-content-end gap-2 mt-5">
          <RouterLink :to="{ name: 'article-detail', params: { id: props.id } }" class="btn btn-outline-secondary btn-lg">
            취소
          </RouterLink>
          <button type="submit" class="btn btn-primary btn-lg" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isSubmitting ? '저장 중...' : '수정 완료' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, RouterLink, useRoute } from 'vue-router';
import { useArticleStore } from '@/features/articles/store/articleStore.js';
import { useUserStore } from '@/features/accounts/store/userStore.js';
import swal from 'sweetalert';

const props = defineProps({
  id: { type: [String, Number], required: true }
});

const router = useRouter();
const route = useRoute();
const articleStore = useArticleStore();
const userStore = useUserStore();

const articleToEdit = ref(null);
const title = ref('');
const content = ref('');

const isLoading = ref(true);
const isSubmitting = ref(false);
const fetchError = ref('');
const submitErrorMessage = ref('');
const isAuthorized = ref(false);

const initializeComponent = async (articleId) => {
  isLoading.value = true;
  fetchError.value = '';
  submitErrorMessage.value = '';
  articleToEdit.value = null;
  isAuthorized.value = false;

  if (!articleId) {
    fetchError.value = '잘못된 접근입니다. 게시글 ID가 제공되지 않았습니다.';
    isLoading.value = false;
    return;
  }

  try {
    const fetchedArticle = await articleStore.getArticleDetail(String(articleId));

    if (fetchedArticle) {
      articleToEdit.value = fetchedArticle;
      title.value = fetchedArticle.title;
      content.value = fetchedArticle.content;

      if (userStore.isLogin && userStore.userInfo && fetchedArticle.user) {
        isAuthorized.value = fetchedArticle.user.username === userStore.userInfo.username;
      } else {
        isAuthorized.value = false;
        fetchError.value = '로그인이 필요하거나 사용자 정보를 확인할 수 없습니다.';
      }
    } else {
      fetchError.value = `ID '${articleId}'에 해당하는 게시글을 찾을 수 없습니다.`;
    }
  } catch (error) {
    console.error('ArticleUpdateView - 게시글 로드 에러:', error);
    if (error.response) {
      fetchError.value = `게시글 로드 실패 (상태: ${error.response.status}). 서버 로그를 확인해주세요.`;
    } else {
      fetchError.value = '게시글 정보를 불러오는 중 네트워크 오류 또는 알 수 없는 오류가 발생했습니다.';
    }
    articleToEdit.value = null;
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  initializeComponent(props.id);
});

watch(() => route.params.id, (newId) => {
  if (newId && String(newId) !== String(props.id)) {
    initializeComponent(newId);
  }
});


const submitUpdate = async () => {
  submitErrorMessage.value = '';
  if (!title.value.trim() || !content.value.trim()) {
    submitErrorMessage.value = '제목과 내용을 모두 입력해주세요.';
    swal("입력 필요", submitErrorMessage.value, "warning");
    return;
  }

  if (!isAuthorized.value) {
    submitErrorMessage.value = '이 게시글을 수정할 권한이 없습니다.';
    swal("권한 없음", submitErrorMessage.value, "error");
    return;
  }

  isSubmitting.value = true;
  try {
    const databox = {
      articleId: String(props.id),
      title: title.value,
      content: content.value
    };
    await articleStore.updateArticle(databox);
    swal("수정 완료!", "게시글이 성공적으로 수정되었습니다.", "success")
      .then(() => {
        // The router.push is handled within articleStore.updateArticle
      });
  } catch (error) {
    console.error('ArticleUpdateView - 게시글 수정 실패:', error);
    if (error.response && error.response.data) {
      const backendErrors = error.response.data;
      let aggregatedMessage = '수정 중 오류가 발생했습니다: ';
      if (typeof backendErrors === 'string') {
        aggregatedMessage += backendErrors;
      } else if (typeof backendErrors === 'object') {
        for (const key in backendErrors) {
          aggregatedMessage += `\n- ${key}: ${Array.isArray(backendErrors[key]) ? backendErrors[key].join(', ') : backendErrors[key]}`;
        }
      }
      submitErrorMessage.value = aggregatedMessage;
    } else {
      submitErrorMessage.value = '게시글 수정 중 알 수 없는 오류가 발생했습니다.';
    }
    swal("수정 실패", submitErrorMessage.value, "error");
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.create-article-page {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f8f9fa;
  min-height: calc(100vh - 56px - 70px);
  color: #212529;
}

.view-header .display-5 { 
  color: #212529;
}

.form-content-wrapper {
  max-width: 720px;
  background-color: #fff;
  padding: 2.5rem;
  border-radius: 0.5rem; 
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,.05); 
  border: 1px solid #dee2e6;
}

.form-label {
  font-weight: 500; 
  color: #495057;
}

.form-control-lg { 
  font-size: 1rem;
  padding: 0.75rem 1.25rem;
}

.form-control-lg:focus {
  border-color: #003c82;
  box-shadow: 0 0 0 0.2rem rgba(0, 60, 130, 0.25);
}

textarea.form-control-lg {
  line-height: 1.6;
}

.btn-lg { 
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

.btn-primary {
  background-color: #003c82; 
  border-color: #003c82;
  font-weight: 500;
  color: #fff;
}
.btn-primary:hover {
  background-color: #002c66;
  border-color: #002a50;
}
.btn-primary:disabled {
  background-color: #003c82;
  border-color: #003c82;
  opacity: 0.65;
}

.btn-outline-secondary {
  font-weight: 500;
}

.alert {
  font-size: 0.9rem;
}

.alert-link-custom {
  font-weight: 500;
  color: #003c82;
  text-decoration: underline;
}
.alert-link-custom:hover {
  color: #002c66;
}
</style>