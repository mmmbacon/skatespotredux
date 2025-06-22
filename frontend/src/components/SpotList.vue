<script setup lang="ts">
import { onMounted, defineEmits, ref, computed } from 'vue';
import { useSpotsStore } from '@/stores/spots';
import type { Spot } from '@/stores/spots';
import { useAuthStore } from '@/stores/auth';
import BaseButton from './BaseButton.vue';

const spotsStore = useSpotsStore();
const authStore = useAuthStore();
const emit = defineEmits(['spot-selected', 'start-creating']);
const search = ref('');

onMounted(() => {
  // The fetch is already called in App.vue, so this is redundant
  // spotsStore.fetchSpots();
});

const handleSpotClick = (spot: Spot) => {
  emit('spot-selected', spot);
};

const filteredSpots = computed(() => {
  if (!search.value) return spotsStore.spots;
  return spotsStore.spots.filter(
    (spot) =>
      spot.name.toLowerCase().includes(search.value.toLowerCase()) ||
      (spot.description &&
        spot.description.toLowerCase().includes(search.value.toLowerCase()))
  );
});
</script>

<template>
  <div class="flex flex-col h-full p-4">
    <div class="flex items-center mb-2">
      <input
        v-model="search"
        type="text"
        placeholder="Search spots..."
        class="flex-1 rounded border px-2 py-1 text-sm"
      />
    </div>
    <div class="flex-1 overflow-y-auto">
      <div
        v-for="spot in filteredSpots"
        :key="spot.id"
        class="mb-2 cursor-pointer rounded hover:bg-gray-100 p-2"
        @click="$emit('spot-selected', spot)"
      >
        <div class="font-semibold">{{ spot.name }}</div>
        <div v-if="spot.description" class="text-xs text-gray-500">
          {{ spot.description }}
        </div>
      </div>
    </div>
  </div>
</template>
