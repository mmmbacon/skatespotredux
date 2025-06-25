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
const props = defineProps<{ selectedSpotId?: number }>();

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
  <div class="flex flex-col h-full pt-2 pb-4">
    <div class="flex items-center mb-2 ml-4 mr-4">
      <input
        v-model="search"
        type="text"
        placeholder="Search spots..."
        class="flex-1 rounded border px-2 py-1 text-sm bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-600 focus:border-transparent transition-colors"
      />
    </div>
    <div class="flex-1 overflow-y-auto space-y-0">
      <div
        v-for="spot in filteredSpots"
        :key="spot.id"
        class="cursor-pointer p-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700"
        :class="
          spot.id === selectedSpotId
            ? 'bg-gray-100 dark:bg-gray-700 border-l-4 border-blue-600'
            : 'border-l-4 border-transparent'
        "
        :style="
          spot.id === selectedSpotId
            ? 'border-left: 4px solid #2563eb;'
            : 'border-left: 4px solid transparent;'
        "
        @click="$emit('spot-selected', spot)"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div
              class="w-8 h-8 bg-gray-200 dark:bg-gray-600 rounded mr-3 flex-shrink-0"
            ></div>
            <div class="font-medium text-gray-900 dark:text-white">
              {{ spot.name }}
            </div>
          </div>
          <div class="flex items-center text-sm w-20 pr-4">
            <div class="text-right flex-1">
              <span class="font-bold text-blue-600 dark:text-blue-600">{{
                spot.score
              }}</span>
            </div>
            <div class="text-right flex-1">
              <span class="text-gray-400 dark:text-gray-500 ml-2">votes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
