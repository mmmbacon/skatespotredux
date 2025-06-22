<script setup lang="ts">
import { onMounted } from 'vue';
import { useSpotsStore } from './stores/spots';
import { useAuthStore } from './stores/auth';
import Map from './components/Map.vue';
import BaseButton from './components/BaseButton.vue';

const authStore = useAuthStore();
const spotsStore = useSpotsStore();

onMounted(() => {
  spotsStore.fetchSpots();
});
</script>

<template>
  <header class="bg-gray-800 text-white p-4 flex justify-between items-center">
    <h1 class="text-xl">SkateSpot</h1>
    <div v-if="authStore.isAuthenticated">
      <span>Welcome, {{ authStore.user?.name }}</span>
      <BaseButton @click="authStore.logout" class="ml-4">Logout</BaseButton>
    </div>
    <div v-else>
      <BaseButton @click="authStore.login">Login with Google</BaseButton>
    </div>
  </header>
  <main class="relative" style="height: calc(100vh - 64px)">
    <Map :spots="spotsStore.spots" />
  </main>
</template>

<style>
/* Reset some default browser styles */
body,
html {
  margin: 0;
  padding: 0;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
    Arial, sans-serif;
  overflow: hidden; /* Prevent scrollbars from appearing */
}

#app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #fff;
  border-bottom: 1px solid #eaeaea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 1000; /* Ensure header is above the map */
  position: relative;
  color: #213547; /* Explicitly set dark text color for header */
}

.logo {
  font-weight: bold;
  font-size: 1.5rem;
  color: #213547; /* Ensure logo text is dark */
}

.auth-controls,
.auth-controls * {
  color: #213547 !important; /* Ensure all header controls are dark */
}

.auth-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

main {
  flex-grow: 1;
  position: relative;
  min-height: 0;
}
</style>
