<template>
  <div
    class="bg-white z-10 flex flex-col border-l border-gray-200 h-full w-full"
  >
    <div class="flex justify-between items-center p-4 border-b">
      <div class="flex items-center">
        <!-- Voting controls: vertical stack -->
        <div class="flex flex-col items-center mr-4">
          <button
            :disabled="!authStore.isAuthenticated"
            @click="() => handleVote(1)"
            class="focus:outline-none"
            :title="!authStore.isAuthenticated ? 'Log in to vote' : ''"
          >
            <span
              :class="[
                spot.my_vote === 1 && authStore.isAuthenticated
                  ? 'text-blue-600'
                  : '',
                !authStore.isAuthenticated
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'cursor-pointer',
              ]"
              >▲</span
            >
          </button>
          <span class="font-semibold">{{ spot.score }}</span>
          <button
            :disabled="!authStore.isAuthenticated"
            @click="() => handleVote(-1)"
            class="focus:outline-none"
            :title="!authStore.isAuthenticated ? 'Log in to vote' : ''"
          >
            <span
              :class="[
                spot.my_vote === -1 && authStore.isAuthenticated
                  ? 'text-red-600'
                  : '',
                !authStore.isAuthenticated
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'cursor-pointer',
              ]"
              >▼</span
            >
          </button>
        </div>
        <!-- Spot title -->
        <div class="flex items-center">
          <div class="w-12 h-12 bg-gray-200 rounded mr-3 flex-shrink-0"></div>
          <h2 class="text-xl font-bold">{{ spot.name }}</h2>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <template v-if="canEdit">
          <BaseButton
            @click="$emit('edit-spot', spot)"
            variant="secondary"
            size="sm"
            >Edit</BaseButton
          >
          <BaseButton @click="handleDelete" variant="danger" size="sm"
            >Delete</BaseButton
          >
        </template>
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
    <LoginPromptModal
      v-if="showLoginPrompt"
      @close="showLoginPrompt = false"
      @login="handleLogin"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, computed } from 'vue';
import BaseButton from './BaseButton.vue';
import CommentList from './CommentList.vue';
import CommentForm from './CommentForm.vue';
import LoginPromptModal from './LoginPromptModal.vue';
import { useSpotsStore, type Spot } from '@/stores/spots';
import { useAuthStore } from '@/stores/auth';

const props = defineProps<{ spot: Spot }>();
const emit = defineEmits(['close', 'edit-spot']);
const spotsStore = useSpotsStore();
const authStore = useAuthStore();
const showLoginPrompt = ref(false);

const canEdit = computed(() => {
  return (
    authStore.isAuthenticated &&
    authStore.user &&
    props.spot.user &&
    authStore.user.id === props.spot.user.id
  );
});

const handleDelete = async () => {
  if (confirm('Are you sure you want to delete this spot?')) {
    await spotsStore.deleteSpot(props.spot.id);
    emit('close');
  }
};

const handleAddComment = async (content: string) => {
  await spotsStore.addComment(props.spot.id, content);
};

const handleVote = async (value: 1 | -1) => {
  if (!authStore.isAuthenticated) {
    showLoginPrompt.value = true;
    return;
  }
  if (props.spot.my_vote === value) {
    await spotsStore.clearVote(props.spot.id);
  } else {
    await spotsStore.voteSpot(props.spot.id, value);
  }
};

const handleLogin = () => {
  showLoginPrompt.value = false;
  authStore.login();
};
</script>

<style scoped>
/* Add any custom styles if needed */
</style>
