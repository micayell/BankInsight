<template>
  <div class="container detail-view-container py-4">
    <div v-if="isLoading" class="loading-state d-flex justify-content-center align-items-center py-5">
      <LoadingIcon />
    </div>
    <div v-else-if="video && video.videoId">
      <header class="video-header mb-4">
        <h1 class="video-title display-5 fw-bold mb-3">{{ video.title }}</h1>
        <p class="video-publish-date text-muted mb-0">업로드 날짜: {{ video.publishedAt }}</p>
      </header>

      <section class="video-player-section mb-4">
        <div class="ratio ratio-16x9">
          <iframe
            :src="video.videoSrc"
            title="YouTube video player"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          ></iframe>
        </div>
      </section>

      <section class="video-description-section" v-if="video.description">
        <h2 class="h5 description-title mb-3">영상 설명</h2>
        <p class="description-text lh-lg">{{ video.description }}</p>
      </section>
    </div>
    <div v-else class="status-message-display alert alert-warning text-center" role="alert">
      비디오 정보를 불러오는 데 실패했거나, 비디오가 존재하지 않습니다.
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'; 
import { useRoute } from 'vue-router';
import { useVideoStore } from '@/stores/videoStore';
import { storeToRefs } from 'pinia';
import LoadingIcon from "@/components/common/LoadingIcon.vue"; 

const route = useRoute();
const store = useVideoStore();
const { video, isLoading } = storeToRefs(store);
const { fetchVideoById } = store;

onMounted(() => { 
  if (route.params.videoId) {
    fetchVideoById(route.params.videoId);
  } else {
    console.error("Video ID가 없습니다.");
    // 스토어의 로딩 상태를 직접 제어
    store.isLoading = false; 
  }
});
</script>

<style scoped>
.detail-view-container {
  max-width: 960px; 
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #212529; 
}
.loading-state {
  min-height: 300px; 
}

.video-header {
}

.video-title {
  color: #1c1c1c; 
  word-break: keep-all; 
}

.video-publish-date {
  font-size: 0.9rem;
}

.video-player-section .ratio {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1); 
  border-radius: 0.25rem; 
  overflow: hidden; 
}

.video-description-section {
  margin-top: 2.5rem; 
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef; 
}

.description-title {
  font-weight: 600;
  color: #343a40;
}

.description-text {
  font-size: 0.95rem;
  color: #495057;
  white-space: pre-wrap; 
}

.status-message-display {
  margin-top: 2rem;
}
</style>