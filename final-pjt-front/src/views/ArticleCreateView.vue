<template>
  <div class="container create-article-page py-4">
    <header class="view-header text-center mb-5">
      <h1 class="display-5 fw-bold">새 게시글 작성</h1>
    </header>

    <div class="form-content-wrapper mx-auto">
      <form @submit.prevent="submitData" class="article-creation-form">
        <div class="mb-4">
          <label for="title" class="form-label fs-5">제목</label>
          <input type="text" id="title" v-model.trim="title" class="form-control form-control-lg" placeholder="제목을 입력하세요">
        </div>

        <div class="mb-4">
          <label for="content" class="form-label fs-5">내용</label>
          <textarea id="content" v-model.trim="content" class="form-control form-control-lg" rows="12" placeholder="내용을 입력하세요"></textarea>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-5">
          <button type="button" @click="cancelCreation" class="btn btn-outline-secondary btn-lg">취소</button>
          <button type="submit" class="btn btn-primary btn-lg">작성 완료</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useArticleStore } from '@/stores/articleStore.js';
import { useRouter } from 'vue-router';
import swal from 'sweetalert';

const store = useArticleStore();
const router = useRouter();

const title = ref('');
const content = ref('');

const submitData = () => {
  if (!title.value || !content.value) {
    swal("입력 오류", "제목과 내용을 모두 입력해주세요.", "warning");
    return;
  }
  const article = {
    title: title.value,
    content: content.value
  };
  store.createArticle(article)
    .then(() => {
      title.value = '';      
      content.value = '';
    })
    .catch(err => {
      console.error("게시글 생성 실패(View):", err);
      const errorMessage = err.response?.data?.detail || err.message || '게시글 생성에 실패했습니다.';
      swal("생성 실패", errorMessage, "error");
    });
};

const cancelCreation = () => {
  if (title.value || content.value) {
    swal({
      title: "작성 취소",
      text: "작성 중인 내용이 있습니다. 정말 취소하시겠습니까?",
      icon: "warning",
      buttons: ["계속 작성", "나가기"],
      dangerMode: true,
    })
    .then((willCancel) => {
      if (willCancel) {
        router.push({ name: 'article' }); 
      }
    });
  } else {
    router.push({ name: 'article' });
  }
};
</script>

<style scoped>
.create-article-page {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f8f9fa;
  min-height: calc(100vh - 56px); 
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

.form-textarea { 
  min-height: 200px; 
}

.btn-lg { 
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

.btn-primary {
  background-color: #003c82; 
  border-color: #003c82;
  font-weight: 500;
}
.btn-primary:hover {
  background-color: #002c66;
  border-color: #002a50;
}

.btn-outline-secondary {
  font-weight: 500;
}
</style>