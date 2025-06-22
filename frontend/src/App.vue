<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
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
import SpotDetailsSidebar from './components/SpotDetailsSidebar.vue';

const authStore = useAuthStore();
const spotsStore = useSpotsStore();
const mapRef = ref<InstanceType<typeof Map> | null>(null);

// State for SpotForm
const isFormOpen = ref(false);
const editingSpot = ref<Spot | null>(null);
const selectedSpot = ref<Spot | null>(null);
const isCreating = ref(false);

// Track the last selected spot for recentering
const lastSelectedSpot = ref<Spot | null>(null);

const selectedSpotFromStore = computed(() => {
  if (!selectedSpot.value) return null;
  return spotsStore.spots.find((s) => s.id === selectedSpot.value?.id) || null;
});

function handleSpotSelected(spot: Spot) {
  // Always reference the store's spot object for reactivity
  const storeSpot = spotsStore.spots.find((s) => s.id === spot.id);
  selectedSpot.value = storeSpot || spot;
  lastSelectedSpot.value = storeSpot || spot;
  // Center the map on the selected spot, offsetting for half the left sidebar
  if (mapRef.value && spot.location && spot.location.coordinates) {
    // coordinates: [lng, lat] -> panToWithOffset expects [lat, lng]
    mapRef.value.panToWithOffset(
      spot.location.coordinates[1],
      spot.location.coordinates[0],
      176 // half sidebar width in px
    );
  }
}

const handleBoundsChanged = (bounds: {
  north: number;
  south: number;
  east: number;
  west: number;
}) => {
  spotsStore.fetchSpots(bounds);
};

const handleStartCreating = () => {
  isCreating.value = true;
  selectedSpot.value = null;
  editingSpot.value = null;
  isFormOpen.value = false;
};

function handleCreateFinished() {
  isCreating.value = false;
}

function closeSidebar() {
  selectedSpot.value = null;
  // Optionally, re-center the map on the last selected spot (if needed)
  if (
    mapRef.value &&
    lastSelectedSpot.value &&
    lastSelectedSpot.value.location &&
    lastSelectedSpot.value.location.coordinates
  ) {
    mapRef.value.setCenter([
      lastSelectedSpot.value.location.coordinates[1],
      lastSelectedSpot.value.location.coordinates[0],
    ]);
  }
}

function openEditForm(spot: Spot) {
  editingSpot.value = spot;
  isFormOpen.value = true;
}

function closeForm() {
  isFormOpen.value = false;
  editingSpot.value = null;
}

async function handleFormSubmit(payload: SpotCreatePayload) {
  if (editingSpot.value) {
    await spotsStore.updateSpot(editingSpot.value.id, payload);
  } else {
    await spotsStore.createSpot(payload);
  }
  closeForm();
}

const handleMapReady = () => {
  const map = mapRef.value?.$refs?.mapRef?.leafletObject;
  if (map) {
    const bounds = map.getBounds();
    spotsStore.fetchSpots({
      north: bounds.getNorth(),
      south: bounds.getSouth(),
      east: bounds.getEast(),
      west: bounds.getWest(),
    });
  }
};
</script>

<template>
  <div class="h-screen flex flex-col">
    <!-- Header -->
    <header
      class="bg-white shadow px-4 py-2 flex items-center justify-between z-10"
    >
      <h1 class="text-2xl font-bold">
        <span>skatespot</span><span class="text-blue-600">.app</span>
      </h1>
      <div>
        <BaseButton v-if="!authStore.isAuthenticated" @click="authStore.login"
          >Login with Google</BaseButton
        >
        <span v-else class="flex items-center space-x-2">
          <img
            :src="authStore.user?.avatar_url"
            alt="avatar"
            class="w-8 h-8 rounded-full"
            v-if="authStore.user?.avatar_url"
          />
          <span>{{ authStore.user?.name || authStore.user?.email }}</span>
          <BaseButton @click="authStore.logout" variant="secondary"
            >Logout</BaseButton
          >
        </span>
      </div>
    </header>
    <!-- Main content: flex row -->
    <div class="flex flex-1 min-h-0">
      <!-- Left Sidebar -->
      <div
        class="h-full bg-gray-50 border-r border-gray-200 w-[352px] flex-shrink-0 shadow-xl z-20"
      >
        <div class="flex items-center justify-between px-4 pt-4 pb-2">
          <h2 class="text-2xl font-bold">Spots</h2>
          <BaseButton @click="handleStartCreating" size="sm"
            >Add Spot</BaseButton
          >
        </div>
        <SpotList
          @start-creating="handleStartCreating"
          @spot-selected="handleSpotSelected"
        />
      </div>
      <!-- Map -->
      <div class="flex-1 relative min-w-0">
        <Map
          ref="mapRef"
          :spots="spotsStore.spots"
          :isCreating="isCreating"
          @bounds-changed="handleBoundsChanged"
          @spot-selected="handleSpotSelected"
          @ready="handleMapReady"
          @create-finished="handleCreateFinished"
        />
      </div>
      <!-- Right Sidebar (in flex flow) -->
      <div
        v-if="selectedSpotFromStore"
        class="h-full w-96 bg-white shadow-xl z-20 flex flex-col border-l border-gray-200"
      >
        <SpotDetailsSidebar
          :spot="selectedSpotFromStore"
          @close="closeSidebar"
          @edit-spot="openEditForm"
        />
      </div>
    </div>
    <!-- Spot Form Modal (only for editing) -->
    <SpotForm
      :spot="editingSpot"
      :isVisible="isFormOpen && editingSpot"
      @save="handleFormSubmit"
      @close="closeForm"
    />
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
