import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/apis/api";
import { useCommentStore } from "@/stores/commentStore"; 
import { useRouter } from "vue-router";

export const useArticleStore = defineStore(
  "article",
  () => {
    const commentStore = useCommentStore();
    const articlesList = ref([]);
    const articleDetail = ref(null);
    const router = useRouter();

    //게시물 리스트 출력
    const getArticleList = async function () {
      try {
        const response = await api.get("/articles/");
        
        const articlesFromApi = response.data;
        const articlesWithCommentCounts = await Promise.all(
          articlesFromApi.map(async (article) => {
            try {
              const count = await commentStore.getCommentCountForArticle(article.id);
              return { ...article, comment_count: count };
            } catch (error) {
              console.error(`게시글 ID ${article.id}의 댓글 수 최종 처리 중 에러:`, error);
              return { ...article, comment_count: undefined }; 
            }
          })
        );
        
        articlesList.value = articlesWithCommentCounts;
        return articlesList.value; 
      } catch (err) {
        console.error("게시글 목록 로드 실패 (articleStore):", err.response?.data || err.message);
        articlesList.value = []; 
        throw err; 
      }
    };
    //게시물 상세보기
    const getArticleDetail = function (articleId) {
      return api.get(`/articles/${articleId}/`)
        .then((res) => {
          articleDetail.value = res.data;
          return res.data;
        })
        .catch((err) => {
          console.error(`게시글 상세 로드 실패 (articleId: ${articleId}):`, err.response?.data || err.message);
          articleDetail.value = null;
          throw err;
        });
    };
    //게시물생성 
    const createArticle = function (databox) {
      const { title, content } = databox;
      return api.post("/articles/", { title, content })
        .then((res) => {
          router.push({ name: "article" }); 
          return res.data;
        })
        .catch((err) => {
          console.error("게시글 생성 실패 (articleStore):", err.response?.data || err.message);
          throw err;
        });
    };

    const updateArticle = function (databox) {
      const { articleId, title, content } = databox;
      return api.put(`/articles/${articleId}/`, { title, content })
        .then((res) => {
          if (articleDetail.value && Number(articleDetail.value.id) === Number(articleId)) {
            articleDetail.value = res.data;
          }
          router.push({ name: "article-detail", params: { id: articleId } });
          return res.data;
        })
        .catch((err) => {
          console.error(`게시글 수정 실패 (articleId: ${articleId}):`, err.response?.data || err.message);
          throw err;
        });
    };

    const deleteArticle = function (articleId) {
      return api.delete(`/articles/${articleId}/`)
        .then((res) => {
          router.push({ name: "article" }); 
          return res;
        })
        .catch((err) => {
          console.error(`게시글 삭제 실패 (articleId: ${articleId}):`, err.response?.data || err.message);
          throw err;
        });
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