<script setup lang="ts">
import { ref } from 'vue';
import { useSpotsStore } from './stores/spots';
import { useAuthStore } from './stores/auth';
import Map from './components/Map.vue';
import SpotList from './components/SpotList.vue';
import BaseButton from './components/BaseButton.vue';

const authStore = useAuthStore();
const spotsStore = useSpotsStore();
const mapRef = ref<InstanceType<typeof Map> | null>(null);
const editedLocation = ref<[number, number] | null>(null);
const isCreatingSpot = ref(false);

const handleFocusSpot = (coordinates: [number, number]) => {
  if (mapRef.value) {
    mapRef.value.setCenter(coordinates);
  }
};

const handleBoundsChanged = (bounds: {
  north: number;
  south: number;
  east: number;
  west: number;
}) => {
  spotsStore.fetchSpots(bounds);
};

const handleLocationToEdit = (location: [number, number] | null) => {
  editedLocation.value = location;
};

const handleLocationUpdated = (location: [number, number]) => {
  editedLocation.value = location;
};

const handleStartCreating = () => {
  isCreatingSpot.value = true;
};

const handleCreateFinished = () => {
  isCreatingSpot.value = false;
};
</script>

<template>
  <div id="app-container" class="flex flex-col h-screen">
    <header
      class="bg-gray-800 text-white p-4 flex justify-between items-center flex-shrink-0"
    >
      <h1 class="text-xl">SkateSpot</h1>
      <div v-if="authStore.isAuthenticated">
        <span>Welcome, {{ authStore.user?.name }}</span>
        <BaseButton @click="authStore.logout" class="ml-4">Logout</BaseButton>
      </div>
      <div v-else>
        <BaseButton @click="authStore.login">Login with Google</BaseButton>
      </div>
    </header>
    <div class="flex flex-grow overflow-hidden">
      <aside class="w-80 bg-gray-100 p-4 overflow-y-auto flex-shrink-0">
        <SpotList
          @focus-spot="handleFocusSpot"
          @location-to-edit="handleLocationToEdit"
          :edited-location="editedLocation"
          @start-creating="handleStartCreating"
        />
      </aside>
      <main class="flex-grow relative">
        <Map
          ref="mapRef"
          :spots="spotsStore.spots"
          @bounds-changed="handleBoundsChanged"
          :location-to-edit="editedLocation"
          @location-updated="handleLocationUpdated"
          :is-creating="isCreatingSpot"
          @create-finished="handleCreateFinished"
        />
      </main>
    </div>
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
