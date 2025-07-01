<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-sm relative">
      <button
        @click="$emit('close')"
        class="absolute top-2 right-2 text-gray-400 hover:text-gray-700 text-2xl"
      >
        &times;
      </button>
      <h2 class="text-xl font-bold mb-2">Create an Account</h2>
      <p class="mb-4 text-gray-700">
        When you create an account, you'll get access to more features like voting and commenting on
        spots.
      </p>
      <button
        @click="$emit('login')"
        class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-semibold"
      >
        Create Account / Log In
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  defineEmits(['close', 'login']);
</script>
