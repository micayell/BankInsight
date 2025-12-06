import api from "@/apis/api";
import { defineStore } from "pinia";
import { ref } from "vue";
import { useUserStore } from "@/stores/userStore";

export const useCommentStore = defineStore("comment", () => {
  const userStore = useUserStore();
  const comments = ref([]);

  const getAuthHeaders = () => {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (userStore.token && typeof userStore.token === 'string') {
      headers['Authorization'] = `Token ${userStore.token}`;
    }
    return headers;
  };

  const getCommentList = function (articleId) {
    return api.get(`/articles/${articleId}/comments/`)
      .then((res) => {
        comments.value = res.data;
        return res.data;
      })
      .catch((err) => {
        console.error(`댓글 목록 로드 실패 (articleId: ${articleId}):`, err.response?.data || err.message);
        comments.value = [];
        throw err;
      });
  };

  const createComment = function (databox) {
    const { articleId, content } = databox;
    return api.post(`/articles/${articleId}/comments/`, { content })
      .then((res) => {
        return res.data;
      })
      .catch((err) => {
        console.error(`댓글 생성 실패 (articleId: ${articleId}):`, err.response?.data || err.message);
        throw err;
      });
  };

  const deleteComment = function (articleId, commentId) {
    return api.delete(`/articles/${articleId}/comments/${commentId}/`)
      .then((res) => {
        return res;
      })
      .catch((err) => {
        console.error(`댓글 삭제 실패 (commentId: ${commentId}):`, err.response?.data || err.message);
        throw err;
      });
  };

  const updateComment = function (articleId, commentId, content) {
    return api.put(`/articles/${articleId}/comments/${commentId}/`, { content })
      .then((res) => {
        return res.data;
      })
      .catch((err) => {
        console.error(`댓글 수정 실패 (commentId: ${commentId}):`, err.response?.data || err.message);
        throw err;
      });
  };

  const getCommentCountForArticle = async function (articleId) {
    try {
      const response = await api.get(`/articles/${articleId}/comments/`);
      return response.data.length;
    } catch (error) {
      console.error(`게시글(id:${articleId}) 댓글 개수 로드 실패 (commentStore):`, error.response?.data || error.message);
      return 0; 
    }
  };

  return {
    comments,
    getCommentList,
    createComment,
    deleteComment,
    updateComment,
    getCommentCountForArticle,
  };
});