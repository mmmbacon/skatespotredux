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
    console.log('SpotForm watch triggered with:', newSpot);
    if (newSpot) {
      form.value = { name: newSpot.name, description: newSpot.description };
      console.log('Form populated with:', form.value);
    } else {
      form.value = { name: '', description: '' };
      console.log('Form reset');
    }
  },
  { immediate: true }
);

const handleSave = () => {
  console.log('handleSave called', { spot: props.spot, form: form.value });
  
  // Validate that name is not empty
  if (!form.value.name || !form.value.name.trim()) {
    console.error('Name is required');
    return;
  }
  
  if (props.spot) {
    // For editing, only send the fields that can be updated
    const updateData: SpotUpdatePayload = {
      name: form.value.name.trim(),
      description: form.value.description?.trim() || '',
      // Keep the original location since we're not allowing location changes in edit mode
      location: props.spot.location
    };
    console.log('Emitting save with update data:', updateData);
    emit('save', updateData);
  } else {
    // For creating, send the full create payload
    emit('save', {
      name: form.value.name.trim(),
      description: form.value.description?.trim() || '',
      location: {
        type: 'Point',
        coordinates: [0, 0] // This should be set by the parent component
      }
    });
  }
};
</script>

<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center"
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
          <BaseButton 
            type="submit" 
            variant="default"
            @click="handleSave"
          >
            {{ spot ? 'Save Changes' : 'Create Spot' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>
