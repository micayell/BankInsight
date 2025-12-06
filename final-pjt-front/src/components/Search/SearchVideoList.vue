<template>
  <div class="video-list-grid-container">
    <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4">
      <div
        v-for="video in videoList"
        :key="video.videoId"
        class="col"
      >
        <EachVideo :video="video" />
      </div>
    </div>
  </div>
</template>

<script setup>
import EachVideo from "@/components/Common/EachVideo.vue";

const props = defineProps({
  videoList: Array
});
</script>

<style scoped>
.video-list-grid-container {
  /* 필요한 경우 컨테이너 스타일 추가 */
}
/* 개별 아이템 스타일은 EachVideo.vue 에서 처리 */
</style>