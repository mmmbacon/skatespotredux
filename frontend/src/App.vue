<script setup lang="ts">
import { ref } from 'vue';
import {
  useSpotsStore,
  type Spot,
  type SpotCreatePayload,
} from './stores/spots';
import { useAuthStore } from './stores/auth';
import Map from './components/Map.vue';
import SpotList from './components/SpotList.vue';
import SpotForm from './components/SpotForm.vue';
import BaseButton from './components/BaseButton.vue';

const authStore = useAuthStore();
const spotsStore = useSpotsStore();
const mapRef = ref<InstanceType<typeof Map> | null>(null);

// State for SpotForm
const isFormVisible = ref(false);
const editingSpot = ref<Spot | null>(null);

const handleSpotSelected = (spot: Spot) => {
  if (mapRef.value) {
    const coords: [number, number] = spot.location.coordinates
      .slice()
      .reverse() as [number, number];
    mapRef.value.setCenter(coords);
    mapRef.value.openPopupForSpot(spot.id);
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

const handleStartCreating = () => {
  editingSpot.value = null;
  isFormVisible.value = true;
};

const showEditForm = (spot: Spot) => {
  editingSpot.value = spot;
  isFormVisible.value = true;
};

const closeForm = () => {
  isFormVisible.value = false;
  editingSpot.value = null;
};

const handleSave = async (formData: Omit<Spot, 'id' | 'user_id'>) => {
  if (editingSpot.value) {
    await spotsStore.updateSpot(editingSpot.value.id, formData);
  } else {
    await spotsStore.addSpot(formData as SpotCreatePayload);
  }
  closeForm();
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
          @spot-selected="handleSpotSelected"
          @start-creating="handleStartCreating"
        />
      </aside>
      <main class="flex-grow relative">
        <Map
          ref="mapRef"
          :spots="spotsStore.spots"
          @bounds-changed="handleBoundsChanged"
          @edit-spot="showEditForm"
        />
        <SpotForm
          :is-visible="isFormVisible"
          :spot="editingSpot"
          @close="closeForm"
          @save="handleSave"
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
