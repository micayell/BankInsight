<template>
  <div class="container article-detail-page py-4">
    <div v-if="article" class="content-wrapper">
      <header class="article-main-header mb-4 pb-3 border-bottom">
        <h1 class="display-5 fw-bold article-title-main mb-3">{{ article.title }}</h1>
        <div class="text-muted article-meta-info">
          <span>작성자: {{ article.user?.nickname || article.user?.username || '알 수 없음' }}</span>
          <span class="mx-2">|</span>
          <span>작성일: {{ formatDate(article.created_at) }}</span>
          <span v-if="article.created_at !== article.updated_at" class="ms-2">
            <span class="mx-2">|</span> 수정일: {{ formatDate(article.updated_at) }}
          </span>
        </div>
      </header>

      <section class="article-body-section mb-5">
        <div class="content-text lead" style="white-space: pre-wrap;">{{ article.content }}</div>
      </section>

      <div v-if="isAuthor" class="article-management-controls d-flex justify-content-end gap-2 mb-4">
        <button @click="editArticle" class="btn btn-outline-primary">게시글 수정</button>
        <button @click="confirmDeleteArticle" class="btn btn-outline-danger">게시글 삭제</button>
      </div>

      <hr class="my-5">

      <section class="comments-area">
        <h2 class="h4 mb-4 comments-main-title">댓글</h2>
        <div v-if="comments && comments.length > 0" class="list-group comment-list-group mb-4">
          <div v-for="comment in comments" :key="comment.id" class="list-group-item comment-item-display">
            <div class="d-flex w-100 justify-content-between">
              <h6 class="mb-1 comment-author-name">{{ comment.user?.nickname || comment.user?.username || '익명' }}</h6>
              <small class="text-muted">{{ formatDate(comment.created_at) }}</small>
            </div>
            <p class="mb-1 comment-text">{{ comment.content }}</p>
            <div class="text-end mt-2" v-if="userStore.isLogin && comment.user && userStore.userInfo && comment.user.username === userStore.userInfo.username">
              <button @click="confirmDeleteComment(comment.id)" class="btn btn-outline-danger btn-sm comment-delete-action">삭제</button>
            </div>
          </div>
        </div>
        <div v-else class="alert alert-light text-center">
          아직 등록된 댓글이 없습니다.
        </div>

        <div v-if="userStore.isLogin" class="new-comment-composer card mt-4">
          <div class="card-body">
            <form @submit.prevent="submitComment">
              <div class="mb-3">
                <textarea v-model="newCommentContent" class="form-control" placeholder="댓글을 입력하세요..." rows="3"></textarea>
              </div>
              <div class="text-end">
                <button type="submit" class="btn btn-primary">댓글 등록</button>
              </div>
            </form>
          </div>
        </div>
        <div v-else class="alert alert-secondary text-center mt-4">
          <RouterLink :to="{ name: 'login' }" class="alert-link">로그인</RouterLink> 후 댓글을 작성할 수 있습니다.
        </div>
      </section>
    </div>
    <div v-else-if="articleStoreLoading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">게시글을 불러오는 중입니다...</p>
    </div>
    <div v-else class="alert alert-warning text-center py-5">
      게시글을 찾을 수 없거나 로드 중 오류가 발생했습니다.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter, RouterLink } from 'vue-router';
import { useArticleStore } from '@/features/articles/store/articleStore.js';
import { useCommentStore } from '@/features/articles/store/commentStore.js';
import { useUserStore } from '@/features/accounts/store/userStore.js';
import swal from 'sweetalert';

const route = useRoute();
const router = useRouter();
const articleStore = useArticleStore();
const commentStore = useCommentStore();
const userStore = useUserStore();

const articleId = ref(route.params.id);
const newCommentContent = ref('');
const articleStoreLoading = ref(false);

const article = computed(() => articleStore.articleDetail);
const comments = computed(() => commentStore.comments);

const isAuthor = computed(() => {
  const loggedIn = userStore.isLogin;
  const currentArticle = article.value;
  const currentUserInfo = userStore.userInfo;
  if (!loggedIn) return false;
  if (!currentArticle || !currentArticle.user || typeof currentArticle.user.username === 'undefined') return false;
  if (!currentUserInfo || typeof currentUserInfo.username === 'undefined') return false;
  return currentArticle.user.username === currentUserInfo.username;
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleString('ko-KR', options);
};

const fetchArticleAndComments = async (id) => {
  if (id) {
    articleStoreLoading.value = true;
    articleStore.articleDetail = null; 
    commentStore.comments = []; 
    try {
      await articleStore.getArticleDetail(id);
      if (articleStore.articleDetail) {
        await commentStore.getCommentList(id);
      }
    } catch (error) {
      console.error("게시글 또는 댓글 로드 실패 (DetailView):", error);
    } finally {
      articleStoreLoading.value = false;
    }
  }
};

onMounted(() => {
  if (articleId.value) {
    fetchArticleAndComments(articleId.value);
  }
});

watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    articleId.value = newId;
    fetchArticleAndComments(newId);
  }
});

const submitComment = async () => {
  if (!newCommentContent.value.trim()) {
    swal("알림", "댓글 내용을 입력해주세요.", "warning");
    return;
  }
  try {
    await commentStore.createComment({
      articleId: articleId.value,
      content: newCommentContent.value
    });
    newCommentContent.value = '';
    await commentStore.getCommentList(articleId.value);
  } catch (error) {
    swal("오류", "댓글 작성에 실패했습니다. 다시 시도해주세요.", "error");
  }
};

const editArticle = () => {
  router.push({ name: 'articleupdate', params: { id: articleId.value } });
};

const confirmDeleteArticle = () => {
  swal({
    title: "정말로 이 게시글을 삭제하시겠습니까?",
    text: "삭제된 게시글은 복구할 수 없습니다.",
    icon: "warning",
    buttons: ["취소", "삭제"],
    dangerMode: true,
  })
  .then(async (willDelete) => {
    if (willDelete) {
      try {
        await articleStore.deleteArticle(articleId.value);
        swal("삭제 완료!", "게시글이 성공적으로 삭제되었습니다.", "success")
          .then(() => {
            router.push({ name: 'article' });
          });
      } catch (error) {
        swal("오류", "게시글 삭제에 실패했습니다.", "error");
      }
    }
  });
};

const confirmDeleteComment = (commentId) => {
    swal({
    title: "정말로 이 댓글을 삭제하시겠습니까?",
    icon: "warning",
    buttons: ["취소", "삭제"],
    dangerMode: true,
  })
  .then(async (willDelete) => {
    if (willDelete) {
      try {
        await commentStore.deleteComment(articleId.value, commentId);
        swal("삭제 완료!", "댓글이 삭제되었습니다.", "success");
        await commentStore.getCommentList(articleId.value);
      } catch (error) {
        swal("오류", "댓글 삭제에 실패했습니다.", "error");
      }
    }
  });
};
</script>

<style scoped>
.article-detail-page {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #fff;
  color: #212529;
}
.content-wrapper { 
  background-color: #fff;
}

.article-title-main { 
  color: #1c1c1c;
  word-break: keep-all;
}
.article-meta-info { 
  font-size: 0.9rem;
}
.content-text { 
  font-size: 1.05rem;
  line-height: 1.8;
}
.article-management-controls .btn { 
  font-weight: 500;
}
.comments-main-title { 
  font-weight: 600;
  color: #343a40;
  border-bottom: 2px solid #dee2e6; 
  padding-bottom: 0.5rem;
}
.comment-item-display { 
  padding-top: 1rem;
  padding-bottom: 1rem;
}
.comment-author-name { 
  font-weight: 500;
}
.comment-text { 
  font-size: 0.95rem;
  color: #495057;
}
.comment-delete-action { 
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
}
.new-comment-composer { 
  background-color: #f8f9fa;
  border-color: #e9ecef;
}
.new-comment-composer .btn-primary { 
  font-weight: 500;
}
.alert-link { 
  font-weight: 500;
}
</style>