<template>
  <!-- Context dot at click location -->
  <div
    v-if="visible"
    :style="{
      left: originalX - 8 + 'px',
      top: originalY - 8 + 'px',
      position: 'fixed',
      zIndex: 40,
    }"
    class="w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow-lg pointer-events-none animate-pulse"
  ></div>

  <!-- Context menu -->
  <div
    v-if="visible && !showDotOnly"
    :style="{ left: originalX + 'px', top: originalY + 'px' }"
    class="context-menu fixed bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-600 py-2 min-w-[160px]"
    style="z-index: 9999 !important; border-radius: 0 12px 12px 12px"
    @click.stop
  >
    <button
      @click="$emit('add-spot')"
      class="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2 text-gray-700 dark:text-gray-200 transition-colors cursor-pointer"
    >
      <Icon
        icon="mdi:map-marker-plus"
        class="w-4 h-4"
      />
      <span>Add Spot Here</span>
    </button>
    <hr class="border-gray-200 dark:border-gray-600 my-1" />
    <div class="px-4 py-1 text-xs text-gray-500 dark:text-gray-400">
      {{ formatCoordinates(lat, lng) }}
    </div>
  </div>
</template>

<script setup lang="ts">
  import { defineProps } from 'vue';
  import { Icon } from '@iconify/vue';

  defineProps<{
    visible: boolean;
    x: number;
    y: number;
    originalX: number;
    originalY: number;
    lat: number;
    lng: number;
    showDotOnly?: boolean;
  }>();

  defineEmits<{
    'add-spot': [];
  }>();

  const formatCoordinates = (lat: number, lng: number): string => {
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  };
</script>
