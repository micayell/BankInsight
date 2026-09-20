<template>
  <div class="homepage-container-main">
    <section class="hero-section-visual" :style="{ backgroundImage: `url(${heroSectionBackgroundUrl})` }">
      <div class="hero-overlay-layer-main"></div>
      <div class="hero-text-content-main container">
        <h1 class="hero-primary-tagline">BankInsight</h1>
        <p class="hero-secondary-tagline">당신의 금융 여정을 밝혀줄 인사이트.</p>
      </div>
    </section>

    <section class="info-section-layout py-5 bg-white">
      <div class="container content-wrapper-inner text-center">
        <h2 class="mb-4 section-title">주요 금융 서비스</h2>
        <p class="lead mb-0 text-body-secondary mx-auto" style="max-width: 700px;">
          BankInsight는 고객님의 성공적인 자산 관리를 위한 최적의 솔루션을 제공하며, 늘 새로운 금융 경험을 선도합니다.
        </p>
      </div>
    </section>

    <section class="exchange-rate-section-wrapper py-5 bg-light">
      <div class="container">
        <ExchangeRate />
      </div>
    </section>
  </div>
</template>

<script setup>
const heroSectionBackgroundUrl = '/background.png';
import ExchangeRate from '@/features/spot/components/ExchangeRate.vue'; 
</script>

<style scoped>
.homepage-container-main {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.hero-section-visual {
  height: calc(100vh - 60px);
  min-height: 450px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #fff;
}

.hero-overlay-layer-main {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.35);
  z-index: 1;
}

.hero-text-content-main {
  position: relative;
  z-index: 2;
  padding: 20px;
  max-width: 800px;
}

.hero-primary-tagline {
  font-size: 3.5rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 20px;
  line-height: 1.2;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 5px rgba(0, 0, 0, 0.6);
}

.hero-secondary-tagline {
  font-size: 1.3rem;
  font-weight: 400;
  color: #f0f0f0;
  margin-bottom: 0;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.info-section-layout.bg-white {
  border-top: 1px solid #e9ecef;
  border-bottom: 1px solid #e9ecef;
}

.exchange-rate-section-wrapper.bg-light {
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: #343a40;
}

.info-section-layout .lead {
  font-size: 1.15rem;
  color: #495057;
  max-width: 720px;
}
</style>