<script setup lang="ts">
import Map from './components/Map.vue';
import { useAuthStore } from './stores/auth';
import BaseButton from './components/BaseButton.vue';

const auth = useAuthStore();
</script>

<template>
  <div id="app-container">
    <header class="main-header">
      <div class="logo">SkateSpot</div>
      <nav class="auth-controls">
        <div v-if="auth.isAuthenticated" class="user-info">
          <img
            v-if="auth.user?.picture"
            :src="auth.user.picture"
            alt="User avatar"
            class="avatar"
          />
          <span>{{ auth.user?.name || auth.user?.email }}</span>
          <BaseButton @click="auth.logout">Sign Out</BaseButton>
        </div>
        <BaseButton v-else @click="auth.login">Log In with Google</BaseButton>
      </nav>
    </header>
    <main>
      <Map />
    </main>
  </div>
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
