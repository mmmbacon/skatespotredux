import { defineStore } from 'pinia';
import { ref, readonly, computed } from 'vue';
import axios from 'axios';

export interface User {
  id: string;
  name?: string;
  avatar_url?: string;
}

export interface Comment {
  id: string;
  content: string;
  spot_id: string;
  user_id: string;
  created_at: string;
  user: User;
}

export interface Spot {
  id: string;
  name: string;
  description?: string;
  location: {
    type: string;
    coordinates: [number, number];
  };
  user: User;
  user_id?: string;
  created_at: string;
  updated_at?: string;
  comments?: Comment[];
  score: number;
  my_vote?: number | null;
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
  const searchQuery = ref('');

  const filteredSpots = computed(() => {
    if (!searchQuery.value) {
      return spots.value;
    }
    return spots.value.filter(
      (spot) =>
        spot.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        spot.description
          ?.toLowerCase()
          .includes(searchQuery.value.toLowerCase())
    );
  });

  async function fetchSpots(bounds?: {
    north: number;
    south: number;
    east: number;
    west: number;
  }) {
    isLoading.value = true;
    error.value = null;
    try {
      const config = bounds ? { params: bounds } : {};
      const response = await axios.get('/api/spots/', config);
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
      const response = await axios.put(`/api/spots/${spotId}/`, spotData);
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
      await axios.delete(`/api/spots/${spotId}/`);
      spots.value = spots.value.filter((s) => s.id !== spotId);
    } catch (e: any) {
      console.error('Failed to delete spot', e);
      throw e;
    }
  }

  async function addComment(spotId: string, content: string) {
    try {
      const response = await axios.post(
        `/api/spots/${spotId}/comments`,
        { content },
        { withCredentials: true }
      );
      const comment = response.data;
      const spot = spots.value.find((s) => s.id === spotId);
      if (spot) {
        if (!spot.comments) {
          spot.comments = [];
        }
        spot.comments.push(comment);
      }
    } catch (e: any) {
      console.error('Failed to add comment', e);
      throw e;
    }
  }

  /* --- Voting --- */
  async function voteSpot(spotId: string, value: 1 | -1) {
    try {
      const response = await axios.post(
        `/api/spots/${spotId}/vote`,
        { value },
        {
          withCredentials: true,
        }
      );
      updateSpotFromServer(response.data);
    } catch (e) {
      console.error('Failed to vote', e);
    }
  }

  async function clearVote(spotId: string) {
    try {
      const response = await axios.delete(`/api/spots/${spotId}/vote`, {
        withCredentials: true,
      });
      updateSpotFromServer(response.data);
    } catch (e) {
      console.error('Failed to clear vote', e);
    }
  }

  function updateSpotFromServer(serverSpot: Spot) {
    const idx = spots.value.findIndex((s) => s.id === serverSpot.id);
    if (idx !== -1) {
      spots.value[idx] = serverSpot;
    }
  }

  return {
    spots,
    filteredSpots,
    searchQuery,
    isLoading: readonly(isLoading),
    error: readonly(error),
    fetchSpots,
    addSpot,
    updateSpot,
    deleteSpot,
    addComment,
    voteSpot,
    clearVote,
  };
});
