<script setup lang="ts">
  import { ref, onMounted, computed } from 'vue';
  import { useSpotsStore, type Spot, type SpotCreatePayload } from './stores/spots';
  import { useAuthStore } from './stores/auth';
  import { useThemeStore } from '@/stores/theme';
  import Map from './components/Map.vue';
  import SpotList from './components/SpotList.vue';
  import SpotForm from './components/SpotForm.vue';
  import BaseButton from './components/BaseButton.vue';
  import SpotDetailsSidebar from './components/SpotDetailsSidebar.vue';
  import { Icon } from '@iconify/vue';

  const authStore = useAuthStore();
  const spotsStore = useSpotsStore();
  const themeStore = useThemeStore();
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
    return spotsStore.spots.find(s => s.id === selectedSpot.value?.id) || null;
  });

  function handleSpotSelected(spot: Spot) {
    // Always reference the store's spot object for reactivity
    const storeSpot = spotsStore.spots.find(s => s.id === spot.id);
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
    console.log('handleFormSubmit called with payload:', payload);
    console.log('editingSpot:', editingSpot.value);

    if (editingSpot.value) {
      console.log('Updating spot with short ID:', editingSpot.value.short_id);
      await spotsStore.updateSpot(editingSpot.value.short_id, payload);
    } else {
      console.log('Creating new spot');
      await spotsStore.addSpot(payload);
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

  // Handle URL parameters for QR code functionality
  const handleUrlParameters = async () => {
    const path = window.location.pathname;
    const spotMatch = path.match(/^\/spot\/([a-zA-Z0-9]+)$/);

    if (spotMatch) {
      const spotId = spotMatch[1];

      // Wait for initial spots to load
      if (spotsStore.spots.length === 0) {
        await spotsStore.fetchSpots();
      }

      // Find the spot by short_id
      const spot = spotsStore.spots.find(s => s.short_id === spotId);
      if (spot) {
        handleSpotSelected(spot);
      }

      // Clean up the URL to remove the spot path
      const cleanUrl = window.location.origin;
      window.history.replaceState({}, document.title, cleanUrl);
    }
  };

  onMounted(async () => {
    themeStore.initializeTheme();
    await handleUrlParameters();
  });
</script>

<template>
  <div class="h-screen flex flex-col bg-white dark:bg-gray-900 transition-colors">
    <!-- Header -->
    <header
      class="bg-white dark:bg-gray-800 shadow-lg px-4 py-2 flex items-center justify-between z-50 transition-colors"
    >
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        <span>skatespot</span>
        <span class="text-blue-600 dark:text-blue-600">.app</span>
      </h1>
      <div class="flex items-center space-x-4">
        <button
          @click="themeStore.toggleTheme"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          :title="themeStore.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <Icon
            :icon="themeStore.isDark ? 'mdi:weather-sunny' : 'mdi:weather-night'"
            class="w-5 h-5 text-gray-600 dark:text-gray-300"
          />
        </button>
        <BaseButton
          v-if="!authStore.isAuthenticated"
          @click="authStore.login"
          color="primary"
        >
          Login with Google
        </BaseButton>
        <span
          v-else
          class="flex items-center space-x-2"
        >
          <img
            :src="authStore.user?.avatar_url"
            alt="avatar"
            class="w-8 h-8 rounded-full"
            v-if="authStore.user?.avatar_url"
          />
          <span class="text-gray-900 dark:text-white">
            {{ authStore.user?.name || authStore.user?.email }}
          </span>
          <BaseButton
            @click="authStore.logout"
            variant="secondary"
          >
            Logout
          </BaseButton>
        </span>
      </div>
    </header>
    <!-- Main content: flex row -->
    <div class="flex flex-1 min-h-0">
      <!-- Left Sidebar -->
      <div
        class="h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 w-[352px] flex-shrink-0 shadow-xl z-20 transition-colors"
      >
        <div class="flex items-center justify-between px-4 pt-4 pb-0">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Spots</h2>
          <BaseButton
            v-if="authStore.isAuthenticated"
            @click="handleStartCreating"
            size="sm"
          >
            Add Spot
          </BaseButton>
        </div>
        <SpotList
          @start-creating="handleStartCreating"
          @spot-selected="handleSpotSelected"
          :selectedSpotId="selectedSpotFromStore?.id"
        />
      </div>
      <!-- Map -->
      <div class="flex-1 relative min-w-0">
        <Map
          ref="mapRef"
          :spots="spotsStore.spots"
          :isCreating="isCreating"
          :activeSpotId="selectedSpotFromStore?.id"
          @bounds-changed="handleBoundsChanged"
          @spot-selected="handleSpotSelected"
          @ready="handleMapReady"
          @create-finished="handleCreateFinished"
        />
      </div>
      <!-- Right Sidebar (in flex flow) -->
      <div
        v-if="selectedSpotFromStore"
        class="h-full w-96 bg-white dark:bg-gray-800 shadow-xl z-20 flex flex-col border-l border-gray-200 dark:border-gray-700 transition-colors"
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
      :isVisible="isFormOpen && !!editingSpot"
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
      -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
