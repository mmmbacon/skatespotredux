<template>
  <div
    v-if="visible"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    style="z-index: 9999 !important"
    @click.self="$emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md mx-4"
      @click.stop
    >
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Create New Spot</h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <Icon
            icon="mdi:close"
            class="w-6 h-6"
          />
        </button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Spot Name *
          </label>
          <input
            v-model="spotName"
            type="text"
            placeholder="Enter spot name"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            v-model="spotDescription"
            placeholder="Describe the spot (optional)"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Location
          </label>
          <div
            class="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-2 rounded"
          >
            {{ formatCoordinates(lat, lng) }}
          </div>
        </div>
      </div>

      <div class="flex justify-end space-x-3 mt-6">
        <BaseButton
          @click="$emit('close')"
          variant="secondary"
        >
          Cancel
        </BaseButton>
        <BaseButton
          @click="handleCreate"
          :disabled="!spotName.trim()"
        >
          Create Spot
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue';
  import { Icon } from '@iconify/vue';
  import BaseButton from './BaseButton.vue';

  const props = defineProps<{
    visible: boolean;
    lat: number;
    lng: number;
  }>();

  const emit = defineEmits<{
    close: [];
    create: [payload: { name: string; description: string; lat: number; lng: number }];
  }>();

  const spotName = ref('');
  const spotDescription = ref('');

  // Reset form when modal opens/closes
  watch(
    () => props.visible,
    visible => {
      if (!visible) {
        spotName.value = '';
        spotDescription.value = '';
      }
    }
  );

  const formatCoordinates = (lat: number, lng: number): string => {
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  };

  const handleCreate = () => {
    if (spotName.value.trim()) {
      emit('create', {
        name: spotName.value.trim(),
        description: spotDescription.value.trim(),
        lat: props.lat,
        lng: props.lng,
      });
    }
  };
</script>
