<script setup lang="ts">
  import { ref, defineEmits } from 'vue';
  import BaseButton from './BaseButton.vue';
  import axios from 'axios';
  import { useAuthStore } from '@/stores/auth';
  import LoginPromptModal from './LoginPromptModal.vue';

  const emit = defineEmits(['submit-comment']);
  const content = ref('');
  const authStore = useAuthStore();
  const showField = ref(false);
  const showLoginPrompt = ref(false);

  const handleSubmit = () => {
    if (content.value.trim()) {
      emit('submit-comment', content.value);
      content.value = '';
      showField.value = false;
    }
  };

  const handleShowField = () => {
    if (authStore.isAuthenticated) {
      showField.value = true;
    } else {
      showLoginPrompt.value = true;
    }
  };

  const handleLogin = () => {
    showLoginPrompt.value = false;
    authStore.login();
  };
</script>

<template>
  <form
    @submit.prevent="handleSubmit"
    class="mt-4"
  >
    <template v-if="authStore.isAuthenticated">
      <template v-if="showField">
        <textarea
          v-model="content"
          placeholder="Add a comment..."
          rows="3"
          class="w-full px-3 py-2 border rounded-lg mb-2"
          required
        ></textarea>
        <BaseButton
          type="submit"
          color="primary"
          size="sm"
        >
          Post Comment
        </BaseButton>
      </template>
      <template v-else>
        <BaseButton
          type="button"
          color="primary"
          size="sm"
          @click="handleShowField"
        >
          Post Comment
        </BaseButton>
      </template>
    </template>
    <template v-else>
      <BaseButton
        type="button"
        color="primary"
        size="sm"
        @click="handleShowField"
      >
        Post Comment
      </BaseButton>
      <LoginPromptModal
        v-if="showLoginPrompt"
        @close="showLoginPrompt = false"
        @login="handleLogin"
      />
    </template>
  </form>
</template>
