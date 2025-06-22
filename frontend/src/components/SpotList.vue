<script setup lang="ts">
import { onMounted } from 'vue';
import { useSpotsStore } from '@/stores/spots';
import { useAuthStore } from '@/stores/auth';
import BaseButton from './BaseButton.vue';

const spotsStore = useSpotsStore();
const authStore = useAuthStore();

onMounted(() => {
  // The fetch is already called in App.vue, so this is redundant
  // spotsStore.fetchSpots();
});

const handleDelete = async (spotId: string) => {
  if (confirm('Are you sure you want to delete this spot?')) {
    await spotsStore.deleteSpot(spotId);
  }
};

const handleEdit = (spotId: string) => {
  // TODO: Implement edit functionality
  console.log('Edit spot:', spotId);
};
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
        <div
          v-if="authStore.user && authStore.user.id === spot.user_id"
          class="mt-4 flex space-x-2"
        >
          <BaseButton
            @click="handleEdit(spot.id)"
            variant="secondary"
            size="sm"
          >
            Edit
          </BaseButton>
          <BaseButton @click="handleDelete(spot.id)" variant="danger" size="sm">
            Delete
          </BaseButton>
        </div>
      </li>
    </ul>
  </div>
</template>
