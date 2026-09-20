<template>
  <div class="page-wrapper">
    <div class="content-container article-list-view">
      <header class="page-section-header d-flex flex-column flex-md-row justify-content-md-between align-items-md-center pb-3 mb-4 border-bottom">
        <div>
          <h1 class="h4 mb-0">커뮤니티</h1>
          <p class="text-muted mb-0 mt-1 subtitle-text">다양한 금융 정보와 이야기를 나누어 보세요.</p>
        </div>
        <div class="mt-3 mt-md-0">
          <button v-if="userStore.isLogin" class="btn btn-custom btn-custom-primary" @click="goToCreate">
            <i class="bi bi-pencil-square me-2"></i>새 글 작성
          </button>
        </div>
      </header>

      <div v-if="articleStore.loading" class="loading-indicator-kia text-center py-5">
        <div class="spinner-border" role="status" :style="{ color: 'var(--app-primary-color)' }">
          <span class="visually-hidden">게시글 목록을 불러오고 있습니다...</span>
        </div>
        <p class="mt-3" :style="{ color: 'var(--app-text-medium)' }">게시글 목록을 불러오고 있습니다.</p>
      </div>
      <div v-else-if="articleStore.error" class="alert alert-danger text-center" role="alert">
        오류: {{ articleStore.error.message || '데이터를 불러오는데 실패했습니다.' }}
      </div>
      <div v-else-if="paginatedArticles.length === 0" class="alert alert-info text-center py-5" role="alert">
        <i class="bi bi-journal-richtext d-block mb-3" style="font-size: 2.5rem;"></i>
        <p class="fs-5 mb-1">아직 게시글이 없습니다.</p>
        <p class="mb-0">첫 번째 글을 작성해보세요!</p>
      </div>
      
      <div v-else class="table-responsive-lg">
        <table class="table table-hover align-middle article-table-styled">
          <thead class="table-light-custom">
            <tr>
              <th scope="col" class="text-center" style="width: 8%;">번호</th>
              <th scope="col" style="width: auto;">제목</th>
              <th scope="col" class="text-center" style="width: 15%;">작성자</th>
              <th scope="col" class="text-center" style="width: 10%;">댓글</th>
              <th scope="col" class="text-center" style="width: 15%;">작성일</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="article in paginatedArticles" :key="article.id" @click="goToDetail(article.id)" class="article-row">
              <td class="text-center">{{ article.id }}</td>
              <td>
                <span class="article-title-link">{{ article.title }}</span>
              </td>
              <td class="text-center">{{ article.user.nickname }}</td>
              <td class="text-center">
                <span v-if="article.comment_count > 0" class="badge bg-primary-custom rounded-pill">
                  {{ article.comment_count }}
                </span>
                <span v-else class="badge bg-secondary-custom rounded-pill">0</span>
              </td>
              <td class="text-center date-text">{{ formatDate(article.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <nav v-if="totalPages > 1" aria-label="Page navigation" class="d-flex justify-content-center mt-4 pt-3">
        <ul class="pagination pagination-custom">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)" aria-label="Previous">
              <span>&laquo;</span>
            </a>
          </li>
          <li class="page-item" v-for="page in pageRange" :key="page" :class="{ active: currentPage === page, 'ellipsis': page === '...' }">
            <span v-if="page === '...'" class="page-link">...</span>
            <a v-else class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)" aria-label="Next">
              <span>&raquo;</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useArticleStore } from '@/features/articles/store/articleStore';
import { useUserStore } from '@/features/accounts/store/userStore';
import { useRouter } from 'vue-router';
import dayjs from 'dayjs';

const articleStore = useArticleStore();
const userStore = useUserStore();
const router = useRouter();

const currentPage = ref(1);
const itemsPerPage = 10;
const pageDisplayRange = 5; 

onMounted(async () => {
  try {
    await articleStore.getArticleList();
  } catch (error) {
    console.error("ArticleListView: 게시글 목록 로드 중 에러", error);
  }
});

const totalPages = computed(() => {
  return Math.ceil((articleStore.articlesList?.length || 0) / itemsPerPage);
});

const paginatedArticles = computed(() => {
  if (!articleStore.articlesList || articleStore.articlesList.length === 0) return [];
  const sortedList = [...articleStore.articlesList].sort((a, b) => b.id - a.id); 
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  return sortedList.slice(startIndex, startIndex + itemsPerPage);
});

const pageRange = computed(() => {
  const range = [];
  const total = totalPages.value;
  const current = currentPage.value;
  const display = pageDisplayRange;
  let start = Math.max(1, current - Math.floor(display / 2));
  let end = Math.min(total, start + display - 1);

  if (end - start + 1 < display && total >= display) {
    start = Math.max(1, end - display + 1);
  }

  if (start > 1) {
    range.push(1);
    if (start > 2) range.push('...');
  }
  for (let i = start; i <= end; i++) {
    range.push(i);
  }
  if (end < total) {
    if (end < total - 1) range.push('...');
    range.push(total);
  }
  return range;
});

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const goToDetail = (articleId) => {
  router.push({ name: 'article-detail', params: { id: articleId } });
};

const goToCreate = () => {
  router.push({ name: 'articlecreate' });
};

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY.MM.DD');
};
</script>

<style scoped>
.article-list-view {
  background-color: #f8f9fa; 
  padding: 1.5rem; 
  min-height: calc(100vh - 56px - 70px); 
  border-radius: var(--app-border-radius); 
  box-shadow: 0 0 10px rgba(0,0,0,0.05); 
}

.page-section-header .subtitle-text {
  font-size: 0.9rem; 
}

.article-list-view .table-responsive-lg {
  border: 1px solid var(--app-border-color);
  border-radius: var(--app-border-radius);
  overflow: hidden;
}

.article-table-styled {
  margin-bottom: 0; 
}

.article-table-styled thead.table-light-custom th {
  background-color: var(--app-background-secondary); 
  color: var(--app-text-dark);
  font-weight: 600;
  font-size: 0.9rem;
  border-bottom: 2px solid var(--app-border-color);
  padding: 0.9rem 0.75rem;
  vertical-align: middle;
}

.article-table-styled tbody tr.article-row {
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}
.article-table-styled tbody tr.article-row:hover {
  background-color: #fdf5f2; 
}

.article-table-styled tbody td {
  color: var(--app-text-medium);
  font-size: 0.9rem;
  padding: 0.9rem 0.75rem;
  vertical-align: middle;
  border-top: 1px solid var(--app-border-color);
}

.article-title-link {
  color: var(--app-text-dark);
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}
.article-row:hover .article-title-link {
  color: var(--app-primary-color);
}

.badge.bg-primary-custom {
  background-color: var(--app-primary-color) !important;
  color: var(--app-background-primary);
}
.badge.bg-secondary-custom {
  background-color: var(--app-text-light) !important;
  color: var(--app-background-primary);
}
.date-text {
  font-size: 0.85rem;
}

.pagination-custom .page-item .page-link {
  color: var(--app-text-medium);
  border: 1px solid var(--app-border-color);
  margin: 0 0.2rem;
  border-radius: var(--app-border-radius);
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.pagination-custom .page-item.active .page-link {
  background-color: var(--app-primary-color);
  border-color: var(--app-primary-color);
  color: var(--app-background-primary);
  font-weight: 600;
  z-index: 1;
}
.pagination-custom .page-item.disabled .page-link {
  color: var(--app-text-light);
  border-color: var(--app-border-color);
}
.pagination-custom .page-item .page-link:hover:not(.active) {
  background-color: var(--app-background-secondary);
  border-color: var(--app-border-color);
  color: var(--app-text-dark);
}
.pagination-custom .page-item.ellipsis .page-link {
  border: none;
  background-color: transparent;
}

@media (max-width: 767.98px) {
  .page-section-header {
    align-items: flex-start; 
  }
  .page-section-header > div:last-child { 
    width: 100%; 
    text-align: right; 
  }
   .page-section-header > div:last-child .btn {
    width: auto; 
  }
}

</style>