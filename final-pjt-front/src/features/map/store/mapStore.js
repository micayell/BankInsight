import { defineStore } from 'pinia';
import { regionData } from '@/features/map/constants/regionData.js';

export const useMapStore = defineStore('map', () => {
  return { regionData };
});
