<template>
  <div class="map-view-wrapper">
    <div class="map-view-row">
      <aside class="map-sidebar">
        <div class="sidebar-inner-scrollable">
          <h3 class="sidebar-main-title">은행 지점 검색</h3>
          <div class="form-section">
            <label for="sidoSelect" class="form-label">시/도:</label>
            <select id="sidoSelect" v-model="selectedSido" class="form-select form-select-sm">
              <option v-for="sido in mapStore.regionData.provinces" :key="sido" :value="sido">{{ sido }}</option>
            </select>
          </div>
          <div class="form-section">
            <label for="sigunguSelect" class="form-label">시/군/구:</label>
            <select id="sigunguSelect" v-model="selectedSigungu" class="form-select form-select-sm" :disabled="citiesList.length === 0">
              <option value="">전체</option>
              <option v-for="sigungu in citiesList" :key="sigungu" :value="sigungu">{{ sigungu }}</option>
            </select>
          </div>
          <div class="form-section">
            <label for="bankSelect" class="form-label">은행:</label>
            <select id="bankSelect" v-model="selectedBank" class="form-select form-select-sm">
              <option v-for="bank in mapStore.regionData.banks" :key="bank" :value="bank">{{ bank }}</option>
            </select>
          </div>
          <button @click="searchBanks" class="btn btn-primary btn-sm w-100 search-trigger-button">검색</button>
        </div>

        <div v-if="isFetchingRoute" class="route-info-box loading-route-info card">
           <div class="card-body text-center">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="info-text mb-0 mt-2"><small>경로 계산 중...</small></p>
          </div>
        </div>
        <div v-else-if="routeInfo.distance !== null && routeInfo.duration !== null" class="route-info-box card shadow-sm">
          <div class="card-body">
            <h6 class="info-title card-subtitle mb-2 fw-bold">경로 결과</h6>
            <p class="info-text mb-1"><strong>예상 거리:</strong> {{ formattedDistance }}</p>
            <p class="info-text mb-0"><strong>예상 시간:</strong> {{ formattedDuration }}</p>
          </div>
        </div>
      </aside>

      <main class="map-main-area">
        <div id="mapInstanceElement" class="map-render-target"></div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { useMapStore } from '@/stores/mapStore';
import swal from 'sweetalert';

const KAKAO_API_KEY = import.meta.env.VITE_KAKAO_API_KEY;
const KAKAO_MOBILITY_KEY = import.meta.env.VITE_KAKAO_MOBILITY_KEY;

const mapStore = useMapStore();

const selectedSido = ref(mapStore.regionData.provinces[0]);
const selectedSigungu = ref('');
const selectedBank = ref(mapStore.regionData.banks[0]);

const citiesList = computed(() => mapStore.regionData.cities[selectedSido.value] || []);

let map;
let ps;
let currentCustomOverlay = ref(null); 
const G_MULTICAMPUS_LAT = 35.205415950571926;
const G_MULTICAMPUS_LNG = 126.81160707543748;
let ORIGIN_COORDS;
let originMarker = null;
const markers = [];
const polylines = [];

const routeInfo = ref({ distance: null, duration: null });
const isFetchingRoute = ref(false);

const formattedDistance = computed(() => {
  if (routeInfo.value.distance === null) return '';
  const km = routeInfo.value.distance / 1000;
  return `${km.toFixed(1)} km`;
});

const formattedDuration = computed(() => {
  if (routeInfo.value.duration === null) return '';
  const totalSeconds = routeInfo.value.duration;
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  let result = '';
  if (hours > 0) result += `${hours}시간 `;
  if (minutes > 0 || hours === 0) result += `${minutes}분`;
  if (result === '') result = '1분 미만';
  return result;
});

function clearMapElements(arr) {
  arr.forEach(item => item.setMap(null));
  arr.length = 0;
}

function closeCustomOverlay() {
  if (currentCustomOverlay.value) {
    currentCustomOverlay.value.setMap(null);
  }
}



function initializeMap() {
  ORIGIN_COORDS = new kakao.maps.LatLng(G_MULTICAMPUS_LAT, G_MULTICAMPUS_LNG);
  const mapContainer = document.getElementById('mapInstanceElement');
  if (!mapContainer) return;
  const mapOptions = { center: ORIGIN_COORDS, level: 5 };
  map = new kakao.maps.Map(mapContainer, mapOptions);
  
  if (originMarker) originMarker.setMap(null);
  originMarker = new kakao.maps.Marker({ map: map, position: ORIGIN_COORDS, title: '출발지 (광주 멀티캠퍼스)' });
  originMarker.setMap(map);

  ps = new kakao.maps.services.Places();
}

async function searchBanks() {
  if (!selectedSigungu.value || !selectedBank.value) {
    swal("알림", "모든 검색 옵션을 선택해주세요.", "info");
    return;
  }
  const keyword = `${selectedSido.value} ${selectedSigungu.value} ${selectedBank.value}`.trim();
  
  clearMapElements(markers);
  clearMapElements(polylines);
  if (currentCustomOverlay.value) currentCustomOverlay.value.setMap(null); 
  routeInfo.value = { distance: null, duration: null };

  ps.keywordSearch(keyword, (data, status) => {
    if (status === kakao.maps.services.Status.OK) {
      const bounds = new kakao.maps.LatLngBounds();
      data.forEach(place => {
        const placePosition = new kakao.maps.LatLng(place.y, place.x);
        const marker = new kakao.maps.Marker({ map: map, position: placePosition, clickable: true }); 
        markers.push(marker);
        bounds.extend(placePosition);

        kakao.maps.event.addListener(marker, 'click', () => {
          displayCustomOverlay(place, marker);
          handleMarkerClick(place, placePosition); 
        });
      });
      if (markers.length > 0) map.setBounds(bounds);
      else swal("검색 결과 없음", "선택하신 조건에 맞는 은행을 찾을 수 없습니다.", "info");
    } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
      swal("검색 결과 없음", "선택하신 조건에 맞는 은행을 찾을 수 없습니다.", "info");
    } else {
      swal("검색 오류", `검색 중 오류가 발생했습니다. (상태: ${status})`, "error");
    }
  });
}

function displayCustomOverlay(place, markerOrPosition) {
  if (currentCustomOverlay.value) {
    currentCustomOverlay.value.setMap(null);
  }

  const content = `
    <div style="
      background-color: white; 
      border: 1px solid #ccc; 
      box-shadow: 0 2px 8px rgba(0,0,0,0.15); 
      border-radius: 6px; 
      padding: 15px; 
      font-size: 14px; 
      min-width: 250px; /* 최소 너비 */
      max-width: 360px; /* 최대 너비 증가 */
      line-height: 1.6;
    ">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <strong style="font-size: 16px; color: #111; overflow-wrap: break-word; word-break: keep-all;">${place.place_name}</strong>
        <button onclick="closeCurrentCustomOverlay()" style="border:none; background:transparent; font-size:18px; cursor:pointer; color:#888; padding:0 0 0 10px;">&times;</button>
      </div>
      <div style="font-size: 13px; color: #555; margin-bottom: 8px; overflow-wrap: break-word; word-break: keep-all;">
        ${place.road_address_name || place.address_name}
      </div>
      ${place.phone ? `<div style="font-size: 13px; color: #007bff; margin-top: 8px;">${place.phone}</div>` : ''}
    </div>`;

  const position = markerOrPosition instanceof kakao.maps.Marker ? markerOrPosition.getPosition() : markerOrPosition;

  currentCustomOverlay.value = new kakao.maps.CustomOverlay({
    position: position,
    content: content,
    xAnchor: 0.5,   
    yAnchor: 1.15, 
    zIndex: 10     
  });
  currentCustomOverlay.value.setMap(map);

  window.closeCurrentCustomOverlay = () => {
    if (currentCustomOverlay.value) {
      currentCustomOverlay.value.setMap(null);
    }
  };
}

async function handleMarkerClick(place, destinationLatLng) {

  clearMapElements(polylines);
  routeInfo.value = { distance: null, duration: null };
  isFetchingRoute.value = true;

  try {
    const routeData = await fetchRoute(destinationLatLng);
    if (routeData && routeData.path.length > 0) {
      polylines.push(new kakao.maps.Polyline({
        map: map, path: routeData.path, strokeWeight: 4, strokeColor: '#0056b3', strokeOpacity: 0.85, strokeStyle: 'solid'
      }));
      routeInfo.value = { distance: routeData.distance, duration: routeData.duration };
    }
  } catch (error) {
    console.error("handleMarkerClick에서 경로 가져오기 실패:", error);
  } finally {
    isFetchingRoute.value = false;
  }
}

async function fetchRoute(destination) {
  const url = `https://apis-navi.kakaomobility.com/v1/directions`;
  const queryParams = { 
    origin: `${ORIGIN_COORDS.getLng()},${ORIGIN_COORDS.getLat()}`,
    destination: `${destination.getLng()},${destination.getLat()}`,
    priority: 'RECOMMEND',
  };

  try {
    const response = await axios.get(url, { 
      params: queryParams,
      headers: { Authorization: `KakaoAK ${KAKAO_MOBILITY_KEY}` }
    });
    const routeSummary = response.data.routes?.[0]?.summary;
    const sections = response.data.routes?.[0]?.sections;

    if (!sections || sections.length === 0 || !routeSummary) {
      swal("경로 정보 없음", "선택한 목적지까지의 경로 정보를 찾을 수 없습니다.", "warning");
      return { path: [], distance: null, duration: null };
    }
    const pathCoordinates = [];
    sections.forEach(section => {
      section.roads.forEach(road => {
        for (let i = 0; i < road.vertexes.length; i += 2) {
          pathCoordinates.push(new kakao.maps.LatLng(road.vertexes[i + 1], road.vertexes[i]));
        }
      });
    });
    return { path: pathCoordinates, distance: routeSummary.distance, duration: routeSummary.duration };
  } catch (e) {
    console.error('카카오모빌리티 경로 요청 오류:', e.response || e);
    let errorMessage = e.message;
    if (e.response && e.response.data && e.response.data.msg) {
      errorMessage = e.response.data.msg;
    } else if (e.response && e.response.statusText) {
      errorMessage = e.response.statusText;
    }
    swal("경로 탐색 API 오류", `경로를 가져오는 데 실패했습니다: ${errorMessage}`, "error");
    return { path: [], distance: null, duration: null };
  }
}

watch(selectedSido, (newSido) => {
  const newCitiesList = mapStore.regionData.cities[newSido] || [];
  selectedSigungu.value = newCitiesList.length > 0 ? newCitiesList[0] : '';
});

onMounted(() => {
  if (citiesList.value.length > 0 && !selectedSigungu.value) {
    selectedSigungu.value = citiesList.value[0];
  }
  const kakaoSdkScript = document.createElement('script');
  kakaoSdkScript.type = 'text/javascript';
  kakaoSdkScript.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_API_KEY}&autoload=false&libraries=services,drawing`;
  document.head.appendChild(kakaoSdkScript);
  
  kakaoSdkScript.onload = () => {
    kakao.maps.load(() => {
      initializeMap();
    });
  };
});
</script>

<style scoped>

.map-view-wrapper {
  height: calc(100vh - 56px); 
  display: flex;
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f8f9fa;
}
.map-view-row {
  display: flex;
  flex-grow: 1;
  width: 100%;
  overflow: hidden; 
}
.map-sidebar {
  width: 320px; 
  flex-shrink: 0;
  background-color: #ffffff;
  padding: 1.75rem; 
  border-right: 1px solid #dee2e6;
  display: flex;
  flex-direction: column;
  overflow-y: hidden;
}
.sidebar-inner-scrollable {
  flex-grow: 1;
  overflow-y: auto;
  padding-right: 8px;
}
.sidebar-main-title {
  font-weight: 600;
  color: #343a40;
  font-size: 1.25rem;
  margin-bottom: 1.75rem;
}
.form-section { margin-bottom: 1.2rem; }
.form-label { font-size: 0.9rem; font-weight: 500; color: #495057; margin-bottom: 0.4rem; }
.form-select-sm { font-size: 0.9rem; }
.search-trigger-button { font-weight: 500; font-size: 0.95rem; padding: 0.45rem 0.75rem; }

.route-info-box {
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 0.375rem;
  font-size: 1.1rem;
  margin-top: 1.5rem; 
  flex-shrink: 0; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.07); 
}
.route-info-box.loading-route-info {
  padding: 1.3rem;
}
.route-info-box .card-body {
  padding: 1.3rem 1.6rem; 
}
.route-info-box .info-title {
  font-size: 1.2rem; 
  font-weight: 600; 
  color: #212529;
  margin-bottom: 1rem; 
}
.route-info-box .info-text {
  color: #343a40;
  font-size: 1.05em; 
  line-height: 1.7; 
}
.route-info-box .info-text strong {
  font-weight: 500; 
}

.map-main-area { flex-grow: 1; position: relative; background-color: #e9ecef; }
.map-render-target { width: 100%; height: 100%; }

@media (max-width: 991.98px) {
  .map-view-wrapper { flex-direction: column; height: auto; }
  .map-view-row { flex-direction: column; }
  .map-sidebar { width: 100%; height: auto; max-height: 48vh; border-right: none; border-bottom: 1px solid #dee2e6;}
  .map-main-area { width: 100%; height: calc(100vh - 56px - 48vh); min-height: 320px; } 
  .route-info-box { font-size: 1rem; }
  .route-info-box .card-body { padding: 1.1rem 1.3rem; }
}
@media (max-width: 767.98px) {
  .map-sidebar { max-height: 50vh; }
  .map-main-area { height: calc(100vh - 56px - 50vh); min-height: 280px; } 
  .sidebar-main-title { font-size: 1.1rem; }
  .search-trigger-button, .form-select-sm { font-size: 0.85rem; }
  .route-info-box { font-size: 0.95rem; }
  .route-info-box .card-body { padding: 0.9rem 1.1rem; }
}
</style>