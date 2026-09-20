import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import dayjs from 'dayjs';

export const useVideoStore = defineStore('video', () => {
  const video = ref(null);
  const isLoading = ref(true);

  const youtubeApi = axios.create({
    baseURL: 'https://www.googleapis.com/youtube/v3',
  });

  const fetchVideoById = async (videoId) => {
    isLoading.value = true;
    video.value = null;
    try {
      const response = await youtubeApi.get('/videos', {
        params: {
          key: import.meta.env.VITE_YOUTUBE_KEY,
          part: 'snippet',
          id: videoId,
        },
      });

      if (response.data.items && response.data.items.length > 0) {
        const item = response.data.items[0];
        video.value = {
          videoId: item.id,
          title: item.snippet.title,
          description: item.snippet.description,
          publishedAt: dayjs(item.snippet.publishedAt).format('YYYY-MM-DD'),
          videoSrc: `https://www.youtube.com/embed/${item.id}?autoplay=1&rel=0`,
        };
      } else {
        console.error('해당 ID의 비디오를 찾을 수 없습니다.');
      }
    } catch (error) {
      console.error('YouTube API 상세 정보 요청 에러:', error);
    } finally {
      isLoading.value = false;
    }
  };

  return {
    video,
    isLoading,
    fetchVideoById,
  };
}); 