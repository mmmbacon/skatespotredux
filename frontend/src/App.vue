<script setup lang="ts">
import Map from './components/Map.vue';
import { useAuth } from './composables/useAuth';

const { user, login, logout } = useAuth();
</script>

<template>
  <div id="app-container">
    <header class="main-header">
      <div class="logo">SkateSpot</div>
      <div class="auth-controls">
        <div v-if="user">
          <img :src="user.picture" alt="avatar" class="avatar" />
          <span>{{ user.name || user.email }}</span>
          <button @click="logout" class="auth-button">Logout</button>
        </div>
        <div v-else>
          <button @click="login" class="auth-button">Login with Google</button>
        </div>
      </div>
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
}

.logo {
  font-weight: bold;
  font-size: 1.5rem;
}

.auth-controls {
  display: flex;
  align-items: center;
}

.auth-controls .avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.auth-controls span {
  margin-right: 1rem;
}

.auth-button {
  border: 1px solid #ccc;
  background-color: #f8f8f8;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.auth-button:hover {
  background-color: #f0f0f0;
}

main {
  flex-grow: 1;
  position: relative;
  min-height: 0;
}
</style>
