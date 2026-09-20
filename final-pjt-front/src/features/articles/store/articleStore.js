import { defineStore } from "pinia";
import { ref } from "vue";
import { articleApi } from "@/features/articles/api/articleApi.js"; // 새로 만든 API 모듈 import
import { useCommentStore } from "@/features/articles/store/commentStore.js";

export const useArticleStore = defineStore(
  "article",
  () => {
    const commentStore = useCommentStore();
    const articlesList = ref([]);
    const articleDetail = ref(null);

    // 게시물 리스트 출력
    const getArticleList = async function () {
      try {
        // API 호출 변경
        const { data } = await articleApi.getList();
        
        articlesList.value = await Promise.all(
          data.map(async (article) => {
            try {
              const count = await commentStore.getCommentCountForArticle(article.id);
              return { ...article, comment_count: count };
            } catch (error) {
              console.error(`게시글 ID ${article.id} 댓글 수 조회 실패:`, error);
              return { ...article, comment_count: 0 }; 
            }
          })
        );
        
        return articlesList.value; 
      } catch (err) {
        console.error("게시글 목록 로드 실패:", err);
        articlesList.value = []; 
        throw err; 
      }
    };

    // 게시물 상세보기
    const getArticleDetail = async function (articleId) {
      try {
        const { data } = await articleApi.getDetail(articleId);
        articleDetail.value = data;
        return data;
      } catch (err) {
        console.error(`게시글 상세 로드 실패 (${articleId}):`, err);
        articleDetail.value = null;
        throw err;
      }
    };

    // 게시물 생성
    const createArticle = async function (payload) {
      try {
        const { data } = await articleApi.create(payload);
        return data;
      } catch (err) {
        console.error("게시글 생성 실패:", err);
        throw err;
      }
    };

    // 게시물 수정
    const updateArticle = async function (articleId, payload) {
      try {
        const { data } = await articleApi.update(articleId, payload);
        // 현재 보고 있는 글이면 상세 정보 업데이트
        if (articleDetail.value && Number(articleDetail.value.id) === Number(articleId)) {
          articleDetail.value = data;
        }
        return data;
      } catch (err) {
        console.error(`게시글 수정 실패 (${articleId}):`, err);
        throw err;
      }
    };

    // 게시물 삭제
    const deleteArticle = async function (articleId) {
      try {
        await articleApi.delete(articleId);
        // 삭제 성공 시 리스트에서도 제거하는 로직 추가
        articlesList.value = articlesList.value.filter(a => a.id !== articleId);
        return true;
      } catch (err) {
        console.error(`게시글 삭제 실패 (${articleId}):`, err);
        throw err;
      }
    };

    return {
      articlesList,
      articleDetail,
      getArticleList,
      getArticleDetail,
      createArticle,
      updateArticle,
      deleteArticle,
    };
  },
);