<script setup lang="ts">
  import type { PropType } from 'vue';
  import type { Comment } from '@/stores/spots';
  import axios from 'axios';

  function timeAgo(dateString: string): string {
    const now = new Date();
    // Ensure the date string is interpreted as UTC by appending 'Z' if it doesn't have timezone info
    const adjustedDateString =
      dateString.includes('Z') || dateString.includes('+') || dateString.includes('-')
        ? dateString
        : dateString + 'Z';
    const date = new Date(adjustedDateString);
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000); // seconds

    // Handle negative differences (future dates) gracefully
    if (diff < 0) {
      return 'just now';
    }

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
    <div
      v-if="comments.length === 0"
      class="text-gray-500 dark:text-gray-400"
    >
      No comments yet. Be the first to add one!
    </div>
    <div
      v-else
      v-for="comment in comments"
      :key="comment.id"
      class="flex items-start space-x-3"
    >
      <div class="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded-full flex-shrink-0"></div>
      <div class="flex-1">
        <p class="font-semibold text-gray-900 dark:text-white">
          {{ comment.user.name }}
        </p>
        <p class="text-gray-700 dark:text-gray-300">{{ comment.content }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {{ timeAgo(comment.created_at) }}
        </p>
      </div>
    </div>
  </div>
</template>
