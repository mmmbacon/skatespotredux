import { defineStore } from 'pinia';
import { ref, readonly } from 'vue';
import axios from 'axios';

export interface Spot {
  id: string;
  name: string;
  description?: string;
  location: {
    type: string;
    coordinates: [number, number];
  };
  user_id: string;
  created_at: string;
  updated_at?: string;
}

export interface SpotCreatePayload {
  name: string;
  description?: string;
  location: {
    type: string;
    coordinates: [number, number];
  };
}

export interface SpotUpdatePayload {
  name?: string;
  description?: string;
  location?: {
    type: string;
    coordinates: [number, number];
  };
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

  async function addSpot(spotData: SpotCreatePayload) {
    try {
      const response = await axios.post('/api/spots/', spotData);
      spots.value.push(response.data);
    } catch (e: any) {
      console.error('Failed to add spot', e);
      // Optionally re-throw or handle error state
      throw e;
    }
  }

  async function updateSpot(spotId: string, spotData: SpotUpdatePayload) {
    try {
      const response = await axios.put(`/api/spots/${spotId}`, spotData);
      const index = spots.value.findIndex((s) => s.id === spotId);
      if (index !== -1) {
        spots.value[index] = response.data;
      }
    } catch (e: any) {
      console.error('Failed to update spot', e);
      throw e;
    }
  }

  async function deleteSpot(spotId: string) {
    try {
      await axios.delete(`/api/spots/${spotId}`);
      spots.value = spots.value.filter((s) => s.id !== spotId);
    } catch (e: any) {
      console.error('Failed to delete spot', e);
      throw e;
    }
  }

  return {
    spots,
    isLoading: readonly(isLoading),
    error: readonly(error),
    fetchSpots,
    addSpot,
    updateSpot,
    deleteSpot,
  };
});
