<template>
  <div class="card h-100 shadow-sm video-item-card" @click="moveToDetail" role="button">
    <img :src="thumbnailSrc" class="card-img-top video-thumbnail" :alt="title">
    <div class="card-body d-flex flex-column">
      <h6 class="card-title video-title flex-grow-1">{{ title }}</h6>
      </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  video: { type: Object, required: true },
});

const videoData = ref(props.video);

const thumbnailSrc = computed(() => {
  return videoData.value.thumbnails?.medium?.url || videoData.value.thumbnails?.default?.url || 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
});

const title = computed(() => {
  const fullTitle = videoData.value.title || '제목 없음';
  const maxLength = 45; 
  return fullTitle.length > maxLength ? fullTitle.substring(0, maxLength) + "..." : fullTitle;
});

const router = useRouter();

const moveToDetail = () => {
  if (videoData.value.videoId) {
    router.push(`/videos/${videoData.value.videoId}`);
  }
};
</script>

<style scoped>
.video-item-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  cursor: pointer;
}
.video-item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important; /* 더 강한 그림자 */
}
.video-thumbnail {
  aspect-ratio: 16 / 9; /* 16:9 비율 유지 */
  object-fit: cover;
}
.card-body {
  padding: 0.8rem 1rem; /* 카드 내부 패딩 조정 */
}
.video-title {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0;
  line-height: 1.4;
  /* 여러 줄 말줄임 (CSS만으로는 한계가 있어 스크립트에서 처리) */
}
/*
.video-publish-time {
  font-size: 0.75rem;
  margin-top: auto;
}
*/
</style>