<template>
  <div
    class="bg-white dark:bg-gray-800 z-10 flex flex-col border-l border-gray-200 dark:border-gray-700 h-full w-full transition-colors"
  >
    <div
      class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700"
    >
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
                  ? 'text-blue-600 dark:text-blue-600'
                  : '',
                !authStore.isAuthenticated
                  ? 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  : 'cursor-pointer text-gray-600 dark:text-gray-300',
              ]"
              >▲</span
            >
          </button>
          <span class="font-semibold text-gray-900 dark:text-white">{{
            spot.score
          }}</span>
          <button
            :disabled="!authStore.isAuthenticated"
            @click="() => handleVote(-1)"
            class="focus:outline-none"
            :title="!authStore.isAuthenticated ? 'Log in to vote' : ''"
          >
            <span
              :class="[
                spot.my_vote === -1 && authStore.isAuthenticated
                  ? 'text-red-600 dark:text-red-400'
                  : '',
                !authStore.isAuthenticated
                  ? 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  : 'cursor-pointer text-gray-600 dark:text-gray-300',
              ]"
              >▼</span
            >
          </button>
        </div>
        <!-- Spot title -->
        <div class="flex items-center">
          <div
            class="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded mr-3 flex-shrink-0"
          ></div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ spot.name }}
          </h2>
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
          @click="showQRModal = true"
          class="text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative group"
          title="Generate a QR code"
        >
          <Icon icon="mdi:qrcode" class="w-6 h-6" />
          <!-- Custom tooltip -->
          <div
            class="absolute right-full top-1/2 transform -translate-y-1/2 mr-2 px-3 py-2 bg-black text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-10"
          >
            Generate a QR code
            <div
              class="absolute left-full top-1/2 transform -translate-y-1/2 border-4 border-transparent border-l-black"
            ></div>
          </div>
        </button>
        <button
          @click="$emit('close')"
          class="text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 text-2xl ml-2 transition-colors"
        >
          &times;
        </button>
      </div>
    </div>
    <div class="p-4 flex-1 overflow-y-auto">
      <p v-if="spot.description" class="mb-4 text-gray-700 dark:text-gray-300">
        {{ spot.description }}
      </p>
      <p v-else class="mb-4 text-gray-400 dark:text-gray-500 italic">
        No description available for this spot.
      </p>
      <hr class="mb-4 border-gray-200 dark:border-gray-700" />
      <h4 class="font-semibold mb-2 text-gray-900 dark:text-white">Comments</h4>
      <CommentList :comments="spot.comments || []" />
      <CommentForm @submit-comment="handleAddComment" />
    </div>
    <LoginPromptModal
      v-if="showLoginPrompt"
      @close="showLoginPrompt = false"
      @login="handleLogin"
    />
    <QRCodeModal
      :isVisible="showQRModal"
      :spotName="spot.name"
      :spotId="spot.short_id"
      @close="showQRModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, computed } from 'vue';
import BaseButton from './BaseButton.vue';
import CommentList from './CommentList.vue';
import CommentForm from './CommentForm.vue';
import LoginPromptModal from './LoginPromptModal.vue';
import QRCodeModal from './QRCodeModal.vue';
import { useSpotsStore, type Spot } from '@/stores/spots';
import { useAuthStore } from '@/stores/auth';
import { Icon } from '@iconify/vue';

const props = defineProps<{ spot: Spot }>();
const emit = defineEmits(['close', 'edit-spot']);
const spotsStore = useSpotsStore();
const authStore = useAuthStore();
const showLoginPrompt = ref(false);
const showQRModal = ref(false);

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
