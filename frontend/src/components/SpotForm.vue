<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue';
import type {
  Spot,
  SpotCreatePayload,
  SpotUpdatePayload,
} from '@/stores/spots';
import BaseButton from './BaseButton.vue';
import axios from 'axios';

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

const imageUrl = ref<string | null>(null);
const uploading = ref(false);
const uploadError = ref<string | null>(null);

watch(
  () => props.spot,
  (newSpot) => {
    if (newSpot) {
      form.value = { name: newSpot.name, description: newSpot.description };
      imageUrl.value = newSpot.photos?.[0] || null;
    } else {
      form.value = { name: '', description: '' };
      imageUrl.value = null;
    }
  }
);

const handleFileChange = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  uploading.value = true;
  uploadError.value = null;
  try {
    // Get presigned URL
    const { data } = await axios.post(`/api/spots/image-upload-url`, null, {
      params: {
        filename: file.name,
        content_type: file.type,
      },
    });
    const { url, public_url } = data;
    // Upload to R2
    await axios.put(url, file, {
      headers: { 'Content-Type': file.type },
    });
    imageUrl.value = public_url;
  } catch (err: any) {
    uploadError.value = 'Image upload failed.';
  } finally {
    uploading.value = false;
  }
};

const handleSave = () => {
  emit('save', {
    ...form.value,
    photos: imageUrl.value ? [imageUrl.value] : [],
  });
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
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Image</label>
          <input type="file" accept="image/*" @change="handleFileChange" />
          <div v-if="uploading" class="text-sm text-gray-500 mt-1">
            Uploading...
          </div>
          <div v-if="uploadError" class="text-sm text-red-500 mt-1">
            {{ uploadError }}
          </div>
          <div v-if="imageUrl" class="mt-2">
            <img
              :src="imageUrl"
              alt="Spot image"
              class="w-32 h-32 object-cover rounded border"
            />
          </div>
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
