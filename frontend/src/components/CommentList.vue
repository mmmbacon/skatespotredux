<script setup lang="ts">
import type { PropType } from 'vue';
import type { Comment } from '@/stores/spots';
import axios from 'axios';

function timeAgo(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000); // seconds
  if (diff < 60) {
    return `${diff} second${diff === 1 ? '' : 's'} ago`;
  } else if (diff < 3600) {
    const mins = Math.floor(diff / 60);
    return `${mins} minute${mins === 1 ? '' : 's'} ago`;
  } else if (diff < 86400) {
    const hours = Math.floor(diff / 3600);
    return `${hours} hour${hours === 1 ? '' : 's'} ago`;
  } else {
    const days = Math.floor(diff / 86400);
    return `${days} day${days === 1 ? '' : 's'} ago`;
  }
}

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
          {{ timeAgo(comment.created_at) }}
        </p>
      </div>
    </div>
  </div>
</template>
