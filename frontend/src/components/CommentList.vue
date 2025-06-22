<script setup lang="ts">
import type { PropType } from 'vue';
import type { Comment } from '@/stores/spots';
import axios from 'axios';

defineProps({
  comments: {
    type: Array as PropType<Comment[]>,
    required: true,
    default: () => [],
  },
});
</script>

<template>
  <div class="space-y-4">
    <div v-if="comments.length === 0" class="text-gray-500">
      No comments yet. Be the first to add one!
    </div>
    <div
      v-else
      v-for="comment in comments"
      :key="comment.id"
      class="flex items-start space-x-3"
    >
      <img
        :src="comment.user.avatar_url || '/default-avatar.png'"
        alt="user avatar"
        class="w-10 h-10 rounded-full"
      />
      <div class="flex-1">
        <p class="font-semibold">{{ comment.user.name }}</p>
        <p class="text-gray-700">{{ comment.content }}</p>
        <p class="text-xs text-gray-500 mt-1">
          {{ new Date(comment.created_at).toLocaleString() }}
        </p>
      </div>
    </div>
  </div>
</template>
