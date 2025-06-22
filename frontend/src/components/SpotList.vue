<script setup lang="ts">
import { onMounted } from 'vue';
import { useSpotsStore } from '@/stores/spots';

const spotsStore = useSpotsStore();

onMounted(() => {
  // The fetch is already called in App.vue, so this is redundant
  // spotsStore.fetchSpots();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-4 text-gray-800">Skate Spots</h1>
    <div v-if="spotsStore.isLoading" class="text-center">
      <p class="text-gray-600">Loading spots...</p>
    </div>
    <div v-else-if="spotsStore.error" class="text-red-500 text-center">
      <p>{{ spotsStore.error }}</p>
    </div>
    <div v-else-if="spotsStore.spots.length === 0" class="text-center">
      <p class="text-gray-600">No spots found.</p>
    </div>
    <ul v-else class="space-y-4">
      <li
        v-for="spot in spotsStore.spots"
        :key="spot.id"
        class="p-4 bg-white border rounded-lg shadow-sm"
      >
        <h2 class="text-xl font-semibold text-gray-900">{{ spot.name }}</h2>
        <p class="text-gray-700">{{ spot.description }}</p>
      </li>
    </ul>
  </div>
</template>
