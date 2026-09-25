<template>
  <div class="map-view-wrapper">
    <div class="map-view-row">
      <aside class="map-sidebar">
        <div class="sidebar-inner-scrollable">
          <h3 class="sidebar-main-title">은행 지점 검색</h3>
          
          <div class="form-section">
            <label for="keywordInput" class="form-label">지점명 직접 검색:</label>
            <input type="text" id="keywordInput" v-model="searchKeyword" class="form-control form-control-sm" placeholder="예: 역삼동 국민은행" @keyup.enter="searchBanks">
          </div>

          <div class="form-section">
            <label for="sidoSelect" class="form-label">시/도:</label>
            <select id="sidoSelect" v-model="selectedSido" class="form-select form-select-sm" :disabled="searchKeyword.length > 0">
              <option v-for="sido in mapStore.regionData.provinces" :key="sido" :value="sido">{{ sido }}</option>
            </select>
          </div>
          <div class="form-section">
            <label for="sigunguSelect" class="form-label">시/군/구:</label>
            <select id="sigunguSelect" v-model="selectedSigungu" class="form-select form-select-sm" :disabled="citiesList.length === 0 || searchKeyword.length > 0">
              <option value="">전체</option>
              <option v-for="sigungu in citiesList" :key="sigungu" :value="sigungu">{{ sigungu }}</option>
            </select>
          </div>
          <div class="form-section">
            <label for="bankSelect" class="form-label">은행:</label>
            <select id="bankSelect" v-model="selectedBank" class="form-select form-select-sm" :disabled="searchKeyword.length > 0">
              <option value="">은행 선택</option>
              <option v-for="bank in mapStore.regionData.banks" :key="bank" :value="bank">{{ bank }}</option>
            </select>
          </div>

          <!-- ATM 제외 체크박스 추가 -->
          <div class="form-check mt-2 mb-3">
            <input class="form-check-input" type="checkbox" id="excludeAtm" v-model="excludeAtm">
            <label class="form-check-label form-label" for="excludeAtm" style="margin-top: 3px;">
              ATM 기기 제외하기
            </label>
          </div>

          <button @click="searchBanks" class="btn btn-primary btn-sm w-100 search-trigger-button mb-2">검색</button>
          <button @click="searchNearbyBanks" class="btn btn-outline-primary btn-sm w-100 search-trigger-button">내 주변 은행 탐색</button>
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
import { useMapStore } from '@/features/map/store/mapStore';
import { useUserStore } from '@/features/accounts/store/userStore';
import swal from 'sweetalert';

const KAKAO_MAP_API_KEY = import.meta.env.VITE_KAKAO_MAP_API_KEY;
const KAKAO_MOBILITY_KEY = import.meta.env.VITE_KAKAO_MOBILITY_KEY;

const mapStore = useMapStore();
const userStore = useUserStore();

const searchKeyword = ref('');
const excludeAtm = ref(true); // 기본적으로 ATM 제외 옵션 켜기

const selectedSido = ref(mapStore.regionData.provinces[0]);
const selectedSigungu = ref('');
const selectedBank = ref(''); // 은행 기본값 선택 안 됨 처리

const citiesList = computed(() => mapStore.regionData.cities[selectedSido.value] || []);

let map;
let ps;
let geocoder;
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

const normalizeSido = (name) => {
  if (!name) return '';
  if (name.includes('서울')) return '서울특별시';
  if (name.includes('부산')) return '부산광역시';
  if (name.includes('대구')) return '대구광역시';
  if (name.includes('인천')) return '인천광역시';
  if (name.includes('대전')) return '대전광역시';
  if (name.includes('울산')) return '울산광역시';
  if (name.includes('세종')) return '세종특별자치시';
  if (name.includes('경기')) return '경기도';
  if (name.includes('강원')) return '강원특별자치도';
  if (name.includes('충북') || name.includes('충청북도')) return '충청북도';
  if (name.includes('충남') || name.includes('충청남도')) return '충청남도';
  if (name.includes('전북') || name.includes('전라북도')) return '전북특별자치도';
  if (name.includes('경북') || name.includes('경상북도')) return '경상북도';
  if (name.includes('경남') || name.includes('경상남도')) return '경상남도';
  if (name.includes('제주')) return '제주특별자치도';
  
  // 새로 통합된 '전남광주통합특별시'로 묶어주기 위한 규칙 추가
  if (name.includes('전남') || name.includes('전라남도') || name.includes('광주')) {
    return '전남광주통합특별시';
  }
  
  return name;
};


function initializeMap() {
  ORIGIN_COORDS = new kakao.maps.LatLng(G_MULTICAMPUS_LAT, G_MULTICAMPUS_LNG);
  const mapContainer = document.getElementById('mapInstanceElement');
  if (!mapContainer) return;
  const mapOptions = { center: ORIGIN_COORDS, level: 5 };
  map = new kakao.maps.Map(mapContainer, mapOptions);
  
  originMarker = new kakao.maps.Marker({ map: map, position: ORIGIN_COORDS, title: '출발지 (드래그하여 이동 가능)', draggable: true });
  
  kakao.maps.event.addListener(originMarker, 'dragend', function() {
    ORIGIN_COORDS = originMarker.getPosition();
  });
  
  ps = new kakao.maps.services.Places();
  geocoder = new kakao.maps.services.Geocoder();

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
        var lat = position.coords.latitude, 
            lon = position.coords.longitude;
        
        ORIGIN_COORDS = new kakao.maps.LatLng(lat, lon);
        map.setCenter(ORIGIN_COORDS);
        originMarker.setPosition(ORIGIN_COORDS);
        originMarker.setTitle('현재 내 위치');
        
        // 역지오코딩 (좌표 -> 주소)
        geocoder.coord2RegionCode(lon, lat, (result, status) => {
          if (status === kakao.maps.services.Status.OK) {
             const region = result.find(r => r.region_type === 'H') || result[0];
             if (region) {
                const r1 = region.region_1depth_name;
                const r2 = region.region_2depth_name;
                
                const normalizedR1 = normalizeSido(r1);
                
                const matchedSido = mapStore.regionData.provinces.find(p => p === normalizedR1);
                
                if (matchedSido) {
                   selectedSido.value = matchedSido;
                   
                   setTimeout(() => {
                     const cities = mapStore.regionData.cities[matchedSido] || [];
                     let matchedSigungu = '';
                     
                     if (matchedSido === '세종특별자치시') {
                        matchedSigungu = '세종시';
                     } else {
                        matchedSigungu = cities.find(c => c === r2);
                        if (!matchedSigungu) {
                           matchedSigungu = cities.find(c => c.includes(r2) || r2.includes(c));
                        }
                     }
                     
                     if (matchedSigungu) {
                       selectedSigungu.value = matchedSigungu;
                     }
                   }, 50);
                }
             }
          }
        });

      }, function(error) {
        console.warn('위치 권한 거부 또는 에러: ', error);
      }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
  } else {
    console.warn("위치 정보를 가져올 수 없습니다. 기본값을 사용합니다.");
  }
}

async function searchNearbyBanks() {
  clearMapElements(markers);
  clearMapElements(polylines);
  if (currentCustomOverlay.value) currentCustomOverlay.value.setMap(null); 
  routeInfo.value = { distance: null, duration: null };

  // 은행을 선택하지 않았다면 '은행' 이라는 포괄적 키워드로 전체 은행 탐색
  const keyword = selectedBank.value || '은행';
  
  ps.keywordSearch(keyword, (data, status) => { processSearchResults(data, status); }, {
     location: ORIGIN_COORDS,
     radius: 3000, // 3km 반경으로 수정
     category_group_code: 'BK9'
  });
}


async function searchBanks() {
  let keyword = '';
  if (searchKeyword.value.trim().length > 0) {
    keyword = searchKeyword.value.trim();
  } else {
    if (!selectedSigungu.value || !selectedBank.value) {
      swal("알림", "모든 검색 옵션을 선택해주세요.", "info");
      return;
    }
    keyword = `${selectedSido.value} ${selectedSigungu.value} ${selectedBank.value}`.trim();
  }
  
  clearMapElements(markers);
  clearMapElements(polylines);
  if (currentCustomOverlay.value) currentCustomOverlay.value.setMap(null); 
  routeInfo.value = { distance: null, duration: null };

  ps.keywordSearch(keyword, (data, status) => { processSearchResults(data, status); });
}

function processSearchResults(data, status) {
  if (status === kakao.maps.services.Status.OK) {
      // ATM 필터링
      if (excludeAtm.value) {
        data = data.filter(place => !place.place_name.includes('365') && !place.place_name.toUpperCase().includes('ATM'));
      }
      
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
      else swal("검색 결과 없음", "선택하신 조건에 맞는 영업점을 찾을 수 없습니다.", "info");
    } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
      swal("검색 결과 없음", "선택하신 조건에 맞는 영업점을 찾을 수 없습니다.", "info");
    } else {
      swal("검색 오류", `검색 중 오류가 발생했습니다. (상태: ${status})`, "error");
    }
}

function displayCustomOverlay(place, markerOrPosition) {
  if (currentCustomOverlay.value) {
    currentCustomOverlay.value.setMap(null);
  }
  
  // 즐겨찾기 여부 확인
  let isFavorite = false;
  let favorites = [];
  if (userStore.isLogin) {
    if (userStore.userProfile && userStore.userProfile.favorite_banks) {
        favorites = userStore.userProfile.favorite_banks;
    } else if (userStore.userInfo && userStore.userInfo.favorite_banks) {
        favorites = userStore.userInfo.favorite_banks;
    }
  }
  
  if (Array.isArray(favorites)) {
      isFavorite = favorites.some(b => String(b.id) === String(place.id));
  }

  const starIcon = isFavorite ? '⭐' : '☆';
  const starColor = isFavorite ? '#ffc107' : '#ccc';

  const content = `
    <div style="
      background-color: white; 
      border: 1px solid #ccc; 
      box-shadow: 0 2px 8px rgba(0,0,0,0.15); 
      border-radius: 6px; 
      padding: 15px; 
      font-size: 14px; 
      min-width: 250px; 
      max-width: 360px; 
      line-height: 1.6;
    ">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <strong style="font-size: 16px; color: #111; overflow-wrap: break-word; word-break: keep-all;">
          <button onclick="window.toggleFavoriteBank('${place.id}', '${place.place_name}', '${place.road_address_name || place.address_name}', this)" style="border:none; background:transparent; font-size:18px; cursor:pointer; color:${starColor}; padding:0 5px 0 0;" title="관심 지점 등록/해제">
            ${starIcon}
          </button>
          ${place.place_name}
        </strong>
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
  
  // 즐겨찾기 글로벌 함수 노출 (DOM Element 직접 조작을 통해 토글 UI 동기화)
  window.toggleFavoriteBank = async (id, name, address, btnElement) => {
    if (!userStore.isLogin) {
      swal("로그인 필요", "관심 지점 등록은 로그인 후 이용 가능합니다.", "info");
      return;
    }
    
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/accounts/favorite-bank/", 
        { branch_id: id, branch_name: name, branch_address: address },
        { headers: { Authorization: `Token ${userStore.token}` } }
      );
      if (response.status === 200 || response.status === 201) {
          const newFavorites = response.data.favorite_banks || [];
          
          // 로컬 스토어 옵티미스틱 업데이트
          if (userStore.userProfile) userStore.userProfile.favorite_banks = newFavorites;
          if (userStore.userInfo) userStore.userInfo.favorite_banks = newFavorites;
          
          // 버튼 UI 즉시 토글
          const isFav = newFavorites.some(b => String(b.id) === String(id));
          if (btnElement) {
             btnElement.innerText = isFav ? '⭐' : '☆';
             btnElement.style.color = isFav ? '#ffc107' : '#ccc';
          }

          if (isFav) {
             swal("즐겨찾기 추가", `${name}이(가) 관심 지점으로 등록되었습니다.`, "success");
          } else {
             swal("즐겨찾기 해제", `${name}이(가) 관심 지점에서 제외되었습니다.`, "info");
          }
          
          // 프로필 동기화 콜
          try {
             userStore.getProfile();
          } catch(err) {
             // getProfile 에러 무시
          }
      }
    } catch (e) {
      console.error(e);
      swal("오류", "관심 지점 등록/해제에 실패했습니다.", "error");
    }
  };

  const kakaoSdkScript = document.createElement('script');
  kakaoSdkScript.type = 'text/javascript';
  kakaoSdkScript.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_MAP_API_KEY}&autoload=false&libraries=services,drawing`;
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
  margin-bottom: 1.25rem;
}
.form-section { margin-bottom: 1rem; }
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
