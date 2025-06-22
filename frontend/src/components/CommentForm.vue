<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import BaseButton from './BaseButton.vue';
import axios from 'axios';

const emit = defineEmits(['submit-comment']);
const content = ref('');

const handleSubmit = () => {
  if (content.value.trim()) {
    emit('submit-comment', content.value);
    content.value = '';
  }
};
</script>

<template>
  <form @submit.prevent="handleSubmit" class="mt-4">
    <textarea
      v-model="content"
      placeholder="Add a comment..."
      rows="3"
      class="w-full px-3 py-2 border rounded-lg mb-2"
      required
    ></textarea>
    <BaseButton type="submit" variant="default" size="sm">
      Post Comment
    </BaseButton>
  </form>
</template>
