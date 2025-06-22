<template>
  <div
    class="bg-white shadow-lg z-10 flex flex-col border-l border-gray-200 h-full w-full"
  >
    <div class="flex justify-between items-center p-4 border-b">
      <h2 class="text-xl font-bold">{{ spot.name }}</h2>
      <div class="flex items-center space-x-2">
        <BaseButton
          @click="$emit('edit-spot', spot)"
          variant="secondary"
          size="sm"
          >Edit</BaseButton
        >
        <BaseButton @click="handleDelete" variant="danger" size="sm"
          >Delete</BaseButton
        >
        <button
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-800 text-2xl ml-2"
        >
          &times;
        </button>
      </div>
    </div>
    <div class="p-4 flex-1 overflow-y-auto">
      <p v-if="spot.description" class="mb-2 text-gray-700">
        {{ spot.description }}
      </p>
      <hr class="mb-4" />
      <h4 class="font-semibold mb-2">Comments</h4>
      <CommentList :comments="spot.comments || []" />
      <CommentForm @submit-comment="handleAddComment" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import BaseButton from './BaseButton.vue';
import CommentList from './CommentList.vue';
import CommentForm from './CommentForm.vue';
import { useSpotsStore, type Spot } from '@/stores/spots';

const props = defineProps<{ spot: Spot }>();
const emit = defineEmits(['close', 'edit-spot']);
const spotsStore = useSpotsStore();

const handleDelete = async () => {
  if (confirm('Are you sure you want to delete this spot?')) {
    await spotsStore.deleteSpot(props.spot.id);
    emit('close');
  }
};

const handleAddComment = async (content: string) => {
  await spotsStore.addComment(props.spot.id, content);
};
</script>

<style scoped>
/* Add any custom styles if needed */
</style>
