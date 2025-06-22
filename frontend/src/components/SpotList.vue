<script setup lang="ts">
import { onMounted, defineEmits } from 'vue';
import { useSpotsStore } from '@/stores/spots';
import type { Spot } from '@/stores/spots';
import { useAuthStore } from '@/stores/auth';
import BaseButton from './BaseButton.vue';

const spotsStore = useSpotsStore();
const authStore = useAuthStore();
const emit = defineEmits(['spot-selected', 'start-creating']);

onMounted(() => {
  // The fetch is already called in App.vue, so this is redundant
  // spotsStore.fetchSpots();
});

const handleSpotClick = (spot: Spot) => {
  emit('spot-selected', spot);
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold text-gray-800">Skate Spots</h1>
      <BaseButton
        @click="$emit('start-creating')"
        v-if="authStore.isAuthenticated"
      >
        Add Spot
      </BaseButton>
    </div>
    <div class="mb-4">
      <input
        type="text"
        v-model="spotsStore.searchQuery"
        placeholder="Search spots..."
        class="w-full px-3 py-2 border rounded-lg"
      />
    </div>
    <div v-if="spotsStore.isLoading" class="text-center">
      <p class="text-gray-600">Loading spots...</p>
    </div>
    <div v-else-if="spotsStore.error" class="text-red-500 text-center">
      <p>{{ spotsStore.error }}</p>
    </div>
    <div v-else-if="spotsStore.filteredSpots.length === 0" class="text-center">
      <p class="text-gray-600">No spots found.</p>
    </div>
    <ul v-else class="space-y-4">
      <li
        v-for="spot in spotsStore.filteredSpots"
        :key="spot.id"
        class="p-4 bg-white border rounded-lg shadow-sm cursor-pointer hover:bg-gray-50"
        @click="handleSpotClick(spot)"
      >
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">{{ spot.name }}</h2>
            <p class="text-gray-700">{{ spot.description }}</p>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>
