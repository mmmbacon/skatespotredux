<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue';
import type {
  Spot,
  SpotCreatePayload,
  SpotUpdatePayload,
} from '@/stores/spots';
import BaseButton from './BaseButton.vue';

interface Props {
  spot: Spot | null;
  isVisible: boolean;
}
const props = defineProps<Props>();
const emit = defineEmits(['close', 'save']);

const form = ref<Partial<SpotCreatePayload | SpotUpdatePayload>>({
  name: '',
  description: '',
});

watch(
  () => props.spot,
  (newSpot) => {
    if (newSpot) {
      form.value = { name: newSpot.name, description: newSpot.description };
    } else {
      form.value = { name: '', description: '' };
    }
  }
);

const handleSave = () => {
  emit('save', form.value);
};
</script>

<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 bg-black bg-opacity-50 z-40 flex justify-center items-center"
  >
    <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
      <h2 class="text-2xl font-bold mb-4">
        {{ spot ? 'Edit Spot' : 'Create Spot' }}
      </h2>
      <form @submit.prevent="handleSave">
        <div class="mb-4">
          <label for="name" class="block text-sm font-medium text-gray-700"
            >Name</label
          >
          <input
            type="text"
            id="name"
            v-model="form.name"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div class="mb-4">
          <label
            for="description"
            class="block text-sm font-medium text-gray-700"
            >Description</label
          >
          <textarea
            id="description"
            v-model="form.description"
            rows="4"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          ></textarea>
        </div>
        <div class="flex justify-end space-x-4">
          <BaseButton type="button" variant="secondary" @click="$emit('close')">
            Cancel
          </BaseButton>
          <BaseButton type="submit" variant="default">
            {{ spot ? 'Save Changes' : 'Create Spot' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>
