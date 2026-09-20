<template>
  <div class="search-input-container">
    <div class="input-group">
      <input 
        type="text" 
        class="form-control form-control-lg"
        placeholder="검색어를 입력하세요..."
        v-model="userInput"
        @keyup.enter="getSearchData"
        aria-label="검색어 입력"
      />
      <button class="btn btn-primary px-4" type="button" @click="getSearchData">
        <span class="material-symbols-outlined me-1 align-middle" style="font-size: 1.2em;">search</span>
        검색
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const userInput = ref('');
const emit = defineEmits(['getVideos']);

const getSearchData = () => {
  if (userInput.value.trim()) {
    emit('getVideos', userInput.value);
  }
};
</script>

<style scoped>
.search-input-container {
  max-width: 650px; /* 검색창 최대 너비 */
  margin: 0 auto; /* 중앙 정렬 */
}
.form-control-lg {
  font-size: 1rem; /* 입력창 폰트 크기 */
  padding: 0.75rem 1.25rem; /* 입력창 패딩 */
}
.btn-primary {
  /* Bootstrap 기본 버튼 사용, 필요시 색상 커스텀 */
  /* background-color: #003c82; */
  /* border-color: #003c82; */
  font-weight: 500;
}
</style>