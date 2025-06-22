import { defineStore } from 'pinia';
import { ref, readonly } from 'vue';
import axios from 'axios';

export interface Spot {
  id: string;
  name: string;
  description?: string;
  location: string; // WKT string
  user_id: string;
  created_at: string;
  updated_at?: string;
}

export const useSpotsStore = defineStore('spots', () => {
  const spots = ref<Spot[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  async function fetchSpots() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await axios.get('/api/spots/');
      spots.value = response.data;
    } catch (e: any) {
      console.error('Failed to fetch spots', e);
      error.value = 'Could not load spots. Please try again later.';
    } finally {
      isLoading.value = false;
    }
  }

  return {
    spots,
    isLoading: readonly(isLoading),
    error: readonly(error),
    fetchSpots,
  };
});
