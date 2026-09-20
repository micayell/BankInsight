<template>
  <div class="container search-view-main py-4">
    <header class="search-view-header d-flex align-items-center pb-3 mb-4 border-bottom">
      <h1 class="h4 mb-0">비디오 검색</h1>
    </header>

    <section class="search-form-area mb-5">
      <SearchInput @get-videos="getVideos" />
    </section>

    <section class="search-results-display">
      <div v-if="isLoading" class="text-center">
        <LoadingIcon />
      </div>
      <div v-else>
        <div v-if="videoList.length === 0 && hasSearched" class="alert alert-info text-center" role="alert">
          "{{ lastSearchTerm }}"에 대한 검색 결과가 없습니다.
        </div>
        <div v-else-if="videoList.length === 0 && !hasSearched" class="text-center text-muted py-5">
          <p class="fs-5">검색어를 입력하여 비디오를 찾아보세요.</p>
        </div>
        <SearchVideoList v-else :video-list="videoList" />
      </div>
    </section>
  </div>
</template>

<script setup>
import SearchInput from "@/features/search/components/SearchInput.vue";
import SearchVideoList from "@/features/search/components/SearchVideoList.vue";
import { ref } from "vue";
import axios from "axios";
import dayjs from "dayjs";
import LoadingIcon from "@/features/shared/components/LoadingIcon.vue";
import swal from "sweetalert";

const URL = "https://www.googleapis.com/youtube/v3";
const API_KEY = import.meta.env.VITE_YOUTUBE_KEY;

const videoList = ref([]);
const lastSearchTerm = ref("");
const isLoading = ref(false);
const hasSearched = ref(false);

const getVideos = (userInput) => {
  if (!userInput.trim()) {
    videoList.value = [];
    hasSearched.value = true; 
    lastSearchTerm.value = userInput;
    return;
  }
  lastSearchTerm.value = userInput;
  isLoading.value = true;
  hasSearched.value = true;
  videoList.value = [];

  axios.get(`${URL}/search`, {
    params: {
      key: API_KEY,
      part: 'snippet',
      type: 'video',
      q: userInput,
      maxResults: 12, 
      regionCode: 'KR',
    }
  })
  .then((response) => {
    const parsedVideoList = response.data.items.map((item) => {
      return {
        videoId: item.id.videoId,
        title: item.snippet.title,
        description: item.snippet.description,
        publishTime: dayjs(item.snippet.publishTime).format("YYYY-MM-DD"),
        thumbnails: item.snippet.thumbnails,
      };
    });
    videoList.value = parsedVideoList;
  })
  .catch((error) => {
    console.error("YouTube API 에러:", error.response?.data || error.message);
    videoList.value = [];
    swal("검색 오류", "비디오를 검색하는 중 문제가 발생했습니다. API 키 또는 요청을 확인해주세요.", "error");
  })
  .finally(() => {
    isLoading.value = false;
  });
};
</script>

<style scoped>
.search-view-main {
  background-color: #f8f9fa; 
  min-height: calc(100vh - 56px); 
}
.search-view-header .h4 { 
  font-weight: 600;
  color: #343a40;
}
.alert-info { 
  max-width: 650px;
  margin: 0 auto;
}

</style>