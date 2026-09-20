<template>
  <div class="search-video-list">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger text-center">
      영상을 불러오는 중 오류가 발생했습니다.
    </div>
    <div v-else-if="videos.length === 0" class="alert alert-info text-center">
      검색 결과가 없습니다.
    </div>
    <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="video in videos" :key="video.id.videoId" class="col">
        <EachVideo :video="video" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useVideoStore } from "@/features/search/videoStore.js";
import EachVideo from "@/features/shared/components/EachVideo.vue";

const store = useVideoStore();

const videos = computed(() => store.videos);
const loading = computed(() => store.loading);
const error = computed(() => store.error);
</script>

<style scoped>
.search-video-list {
  margin-top: 1.5rem;
}
</style>
