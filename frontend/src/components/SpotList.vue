<script setup lang="ts">
import { onMounted } from 'vue';
import { useSpotsStore } from '@/stores/spots';

const spotsStore = useSpotsStore();

onMounted(() => {
  spotsStore.fetchSpots();
});
</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Skate Spots</h1>
    <div v-if="spotsStore.isLoading" class="text-center">
      <p>Loading spots...</p>
    </div>
    <div v-else-if="spotsStore.error" class="text-red-500 text-center">
      <p>{{ spotsStore.error }}</p>
    </div>
    <div v-else-if="spotsStore.spots.length === 0" class="text-center">
      <p>No spots found. Be the first to add one!</p>
    </div>
    <ul v-else class="space-y-4">
      <li
        v-for="spot in spotsStore.spots"
        :key="spot.id"
        class="p-4 border rounded-lg shadow-sm"
      >
        <h2 class="text-xl font-semibold">{{ spot.name }}</h2>
        <p class="text-gray-700">{{ spot.description }}</p>
        <p class="text-sm text-gray-500 mt-2">Location: {{ spot.location }}</p>
      </li>
    </ul>
  </div>
</template>
