<template>
  <div class="homepage-container-main">
    
    <!-- 전체 와이드 화면을 차지하며 토스톤앤매너에 맞게 꾸며놓은 캐러셀 섹션 -->
    <section class="hero-carousel-section border-bottom">
      <HomeCarousel />
    </section>

    <!-- 사용자 맞춤 금융상품 추천 섹션 -->
    <section class="recommend-section-wrapper">
      <BasicRecommend />
    </section>
    
  </div>
</template>

<script setup>
import HomeCarousel from '@/features/home/components/HomeCarousel.vue';
import BasicRecommend from '@/features/home/components/BasicRecommend.vue';
</script>

<style scoped>
.homepage-container-main {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  min-height: calc(100vh - 60px);
  background-color: #f8f9fa;
}

.hero-carousel-section {
  background-color: #ffffff;
}

.recommend-section-wrapper {
  background-color: #f8f9fa; /* slightly off-white for contrast */
}
</style>