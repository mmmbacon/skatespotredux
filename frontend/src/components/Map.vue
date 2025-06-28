<template>
  <div class="map-container">
    <div v-if="isMounted" class="map-instance">
      <l-map
        ref="mapRef"
        v-model:zoom="zoom"
        :center="center"
        :zoom-control-position="'bottomright'"
        @ready="onMapReady"
      >
        <!-- Mapbox tiles if token is available, otherwise OpenStreetMap -->
        <l-tile-layer
          v-if="mapboxToken"
          :key="mapboxStyle"
          :url="`https://api.mapbox.com/styles/v1/mapbox/${mapboxStyle}/tiles/256/{z}/{x}/{y}@2x?access_token=${mapboxToken}`"
          :attribution="'Map data &copy; <a href=\'https://www.openstreetmap.org/\'>OpenStreetMap</a> contributors, Imagery © <a href=\'https://www.mapbox.com/\'>Mapbox</a>'"
          @tileerror="onTileError"
          @tileload="onTileLoad"
        />
        <l-tile-layer
          v-else
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          layer-type="base"
          name="OpenStreetMap"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        <!-- Loop through spots and create markers -->
        <l-marker
          v-for="spot in spots"
          :key="spot.id + (props.activeSpotId === spot.id ? '-active' : '')"
          :ref="(el) => setMarkerRef(el, spot.id)"
          :lat-lng="
            [spot.location.coordinates[1], spot.location.coordinates[0]] as [
              number,
              number,
            ]
          "
          @click="$emit('spot-selected', spot)"
          :icon="
            String(props.activeSpotId) === String(spot.id)
              ? blueIcon
              : yellowIcon
          "
          :class="
            String(props.activeSpotId) === String(spot.id)
              ? 'selected-marker'
              : ''
          "
        >
          <l-tooltip
            :direction="'top'"
            :offset="[0, -10]"
            :sticky="false"
            :permanent="String(props.activeSpotId) === String(spot.id)"
            :key="
              String(props.activeSpotId) === String(spot.id)
                ? 'active-tooltip'
                : 'tooltip-' + spot.id
            "
            class="spot-tooltip"
          >
            <div class="flex items-center space-x-2">
              <span class="font-bold text-blue-600 mr-1">{{ spot.score }}</span>
              <span class="font-semibold">{{ spot.name }}</span>
            </div>
          </l-tooltip>
        </l-marker>
        <!-- Draggable marker for editing -->
        <l-marker
          v-if="editableLocation"
          :lat-lng="editableLocation"
          :draggable="true"
          @dragend="handleMarkerDrag"
        >
        </l-marker>

        <!-- Marker for creating a new spot -->
        <l-marker
          v-if="isCreating && newSpotLocation"
          ref="newMarkerRef"
          :lat-lng="newSpotLocation"
          :draggable="true"
          @dragend="handleNewMarkerDrag"
          :icon="yellowIcon"
        >
          <l-popup :close-on-click="false" :close-button="false">
            <div class="w-48">
              <h3 class="font-bold mb-2">Create New Spot</h3>
              <div class="text-xs text-gray-500 mb-2">
                Drag pin to locate spot
              </div>
              <input
                v-model="newSpotName"
                placeholder="Spot Name"
                class="w-full px-2 py-1 border rounded-md mb-2"
              />
              <textarea
                v-model="newSpotDescription"
                placeholder="Description (optional)"
                class="w-full px-2 py-1 border rounded-md mb-2"
                rows="2"
              ></textarea>
              <BaseButton @click="handleCreateSpot" size="sm" variant="default"
                >Save</BaseButton
              >
            </div>
          </l-popup>
        </l-marker>

        <!-- Preview marker for context menu spot creation -->
        <l-marker
          v-if="createModal.visible"
          :lat-lng="[createModal.lat, createModal.lng]"
          :icon="previewIcon"
          :z-index-offset="1000"
        >
          <l-tooltip :permanent="true" direction="top" class="preview-tooltip">
            <div class="text-center">
              <div class="font-semibold text-green-600">📍 New Spot Location</div>
              <div class="text-xs text-gray-600">{{ formatCoordinates(createModal.lat, createModal.lng) }}</div>
            </div>
          </l-tooltip>
        </l-marker>
      </l-map>
    </div>
    
    <!-- Context Menu -->
    <ContextMenu
      :visible="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
      :original-x="contextMenu.originalX"
      :original-y="contextMenu.originalY"
      :lat="contextMenu.lat"
      :lng="contextMenu.lng"
      :show-dot-only="createModal.visible"
      @add-spot="handleContextMenuAddSpot"
    />
    
    <!-- Spot Create Modal -->
    <SpotCreateModal
      :visible="createModal.visible"
      :lat="createModal.lat"
      :lng="createModal.lng"
      @close="handleCloseCreateModal"
      @create="handleCreateSpotFromModal"
    />
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  onMounted,
  onUnmounted,
  defineProps,
  defineExpose,
  defineEmits,
  watch,
  nextTick,
  computed,
} from 'vue';
import {
  LMap,
  LTileLayer,
  LMarker,
  LIcon,
  LPopup,
  LTooltip,
} from '@vue-leaflet/vue-leaflet';
import 'leaflet/dist/leaflet.css';
import type { PropType } from 'vue';
import type { Spot } from '@/stores/spots';
import { useSpotsStore } from '@/stores/spots';
import { useThemeStore } from '@/stores/theme';
import type { SpotCreatePayload } from '@/stores/spots';
import BaseButton from './BaseButton.vue';
import CommentList from './CommentList.vue';
import CommentForm from './CommentForm.vue';
import ContextMenu from './ContextMenu.vue';
import SpotCreateModal from './SpotCreateModal.vue';
import { useToast } from 'vue-toastification';
import L from 'leaflet';

// This is a common fix for icon path issues with bundlers
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl: iconUrl,
  iconRetinaUrl: iconRetinaUrl,
  shadowUrl: shadowUrl,
});

const redIcon = new L.Icon({
  iconUrl:
    'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const blueIcon = new L.Icon({
  iconUrl:
    'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const yellowIcon = new L.Icon({
  iconUrl:
    'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-grey.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const previewIcon = new L.Icon({
  iconUrl:
    'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const spotsStore = useSpotsStore();
const themeStore = useThemeStore();
const toast = useToast();

// Define props
const props = defineProps({
  spots: {
    type: Array as PropType<Spot[]>,
    required: true,
    default: () => [],
  },
  locationToEdit: {
    type: Object as PropType<[number, number] | null>,
    default: null,
  },
  isCreating: {
    type: Boolean,
    default: false,
  },
  activeSpotId: {
    type: [String, Number],
    default: null,
  },
});

const emit = defineEmits([
  'bounds-changed',
  'location-updated',
  'create-finished',
  'edit-spot',
  'spot-selected',
  'ready',
]);
const editableLocation = ref<[number, number] | null>(null);

watch(
  () => props.locationToEdit,
  (newVal) => {
    editableLocation.value = newVal;
  }
);

const handleMarkerDrag = (e: any) => {
  const latlng = e.target.getLatLng();
  editableLocation.value = [latlng.lat, latlng.lng];
  emit('location-updated', editableLocation.value);
};

const zoom = ref(11);
const isMounted = ref(false);
// Try to get saved location from localStorage, otherwise use default
const getSavedLocation = (): [number, number] => {
  const saved = localStorage.getItem('userLocation');
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length === 2) {
        return parsed as [number, number];
      }
    } catch (e) {
      // Invalid saved location, use default
    }
  }
  return [39.8283, -98.5795]; // Default center
};

const center = ref<[number, number]>(getSavedLocation());

// Watch for center changes and update map view (but avoid infinite loops)
watch(center, (newCenter, oldCenter) => {
  if (mapRef.value && newCenter !== oldCenter) {
    const map = (mapRef.value as any).leafletObject;
    // Only update if the center actually changed significantly
    const distance = Math.abs(newCenter[0] - oldCenter[0]) + Math.abs(newCenter[1] - oldCenter[1]);
    if (distance > 0.001) { // Only update if moved more than ~100m
      map.setView(newCenter, 11);
      // Force map refresh after center change and emit bounds
      setTimeout(() => {
        map.invalidateSize();
        // Emit bounds changed to trigger spot loading
        const bounds = map.getBounds();
        emit('bounds-changed', {
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest(),
        });
      }, 100);
    }
  }
});
const mapRef = ref(null);
const markerRefs = ref<Record<string, any>>({});

const setMarkerRef = (el: any, spotId: string) => {
  if (el) {
    markerRefs.value[spotId] = el;
  }
};

const openPopupForSpot = (spotId: string) => {
  const marker = markerRefs.value[spotId];
  if (marker) {
    marker.leafletObject.openPopup();
  }
};

const newSpotName = ref('');
const newSpotDescription = ref('');
const newSpotLocation = ref<[number, number] | null>(null);
const newMarkerRef = ref(null);

// Context menu state
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  originalX: 0,
  originalY: 0,
  lat: 0,
  lng: 0,
});

// Create modal state
const createModal = ref({
  visible: false,
  lat: 0,
  lng: 0,
});

watch(
  () => props.isCreating,
  (creating) => {
    if (creating) {
      const map = (mapRef.value as any)?.leafletObject;
      if (map) {
        const center = map.getCenter();
        newSpotLocation.value = [center.lat, center.lng];
        nextTick(() => {
          (newMarkerRef.value as any)?.leafletObject.openPopup();
        });
      }
    } else {
      newSpotLocation.value = null;
      newSpotName.value = '';
      newSpotDescription.value = '';
    }
  }
);

const handleNewMarkerDrag = (e: any) => {
  const latlng = e.target.getLatLng();
  newSpotLocation.value = [latlng.lat, latlng.lng];
  nextTick(() => {
    (newMarkerRef.value as any)?.leafletObject.openPopup();
  });
};

const handleCreateSpot = async () => {
  if (newSpotName.value && newSpotLocation.value) {
    const payload: SpotCreatePayload = {
      name: newSpotName.value,
      description: newSpotDescription.value,
      location: {
        type: 'Point',
        coordinates: [newSpotLocation.value[1], newSpotLocation.value[0]], // Lng, Lat
      },
    };
    await spotsStore.addSpot(payload);
    emit('create-finished');
    toast.success('Spot created successfully!');
  }
};

const handleAddComment = async (spotId: string, content: string) => {
  await spotsStore.addComment(spotId, content);
  toast.success('Comment added!');
};

const handleDelete = async (spotId: string) => {
  if (confirm('Are you sure you want to delete this spot?')) {
    await spotsStore.deleteSpot(spotId);
    toast.success('Spot deleted successfully!');
  }
};

// Context menu handlers
const handleContextMenuAddSpot = () => {
  createModal.value = {
    visible: true,
    lat: contextMenu.value.lat,
    lng: contextMenu.value.lng,
  };
  // Context menu will automatically show only the dot when modal is visible
};

const handleCloseCreateModal = () => {
  createModal.value.visible = false;
  contextMenu.value.visible = false; // Hide the context menu dot when modal closes
};

const handleCreateSpotFromModal = async (payload: { name: string; description: string; lat: number; lng: number }) => {
  const spotPayload: SpotCreatePayload = {
    name: payload.name,
    description: payload.description,
    location: {
      type: 'Point',
      coordinates: [payload.lng, payload.lat], // Lng, Lat for GeoJSON
    },
  };
  await spotsStore.addSpot(spotPayload);
  createModal.value.visible = false;
  contextMenu.value.visible = false; // Hide the context menu dot when spot is created
  toast.success('Spot created successfully!');
};

// Helper function to format coordinates
const formatCoordinates = (lat: number, lng: number): string => {
  return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
};

onMounted(() => {
  // By setting this flag in onMounted, we ensure the map component
  // is only rendered on the client, avoiding SSR issues.
  isMounted.value = true;
  
  // Add global click handler to hide context menu
  document.addEventListener('click', hideContextMenu);

  // Get user's location and center map there (only if we don't have a recent saved location)
  const savedLocation = localStorage.getItem('userLocation');
  const savedTimestamp = localStorage.getItem('userLocationTimestamp');
  const isLocationFresh = savedTimestamp && (Date.now() - parseInt(savedTimestamp)) < 300000; // 5 minutes
  
  if (navigator.geolocation && (!savedLocation || !isLocationFresh)) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLocation: [number, number] = [position.coords.latitude, position.coords.longitude];
        
        // Save location to localStorage
        localStorage.setItem('userLocation', JSON.stringify(userLocation));
        localStorage.setItem('userLocationTimestamp', Date.now().toString());
        
        center.value = userLocation;
        
        // If map is already loaded, update its view immediately
        if (mapRef.value) {
          const map = (mapRef.value as any).leafletObject;
          map.setView(userLocation, 11);
          // Force map to refresh/invalidate to show markers
          setTimeout(() => {
            map.invalidateSize();
            // Emit bounds changed to trigger spot loading
            const bounds = map.getBounds();
            emit('bounds-changed', {
              north: bounds.getNorth(),
              south: bounds.getSouth(),
              east: bounds.getEast(),
              west: bounds.getWest(),
            });
          }, 100);
        }
      },
      (error) => {
        // Location access denied or failed, using saved/default location
      },
      {
        enableHighAccuracy: false,
        timeout: 5000,
        maximumAge: 300000 // 5 minutes cache
      }
    );
  }
});

// Store the click handler for cleanup
const hideContextMenu = (event: Event) => {
  // Don't hide if clicking on the context menu itself
  if (event.target && (event.target as Element).closest('.context-menu')) {
    return;
  }
  contextMenu.value.visible = false;
};

onUnmounted(() => {
  document.removeEventListener('click', hideContextMenu);
});

const onMapReady = () => {
  if (mapRef.value) {
    const map = (mapRef.value as any).leafletObject;
    
    // Force initial refresh and emit bounds to trigger spot loading
    setTimeout(() => {
      map.invalidateSize();
      // Emit initial bounds to trigger spot loading
      const bounds = map.getBounds();
      emit('bounds-changed', {
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest(),
      });
      }, 200);
    
    map.on('moveend', () => {
      const bounds = map.getBounds();
      emit('bounds-changed', {
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest(),
      });
    });
    
    // Add right-click context menu
    map.on('contextmenu', (e: any) => {
      e.originalEvent.preventDefault();
      e.originalEvent.stopPropagation();
      contextMenu.value = {
        visible: true,
        x: e.originalEvent.clientX, // Keep for compatibility
        y: e.originalEvent.clientY, // Keep for compatibility
        originalX: e.originalEvent.clientX, // Original click position
        originalY: e.originalEvent.clientY, // Original click position
        lat: e.latlng.lat,
        lng: e.latlng.lng,
      };
    });
    
    // Hide context menu on regular click
    map.on('click', () => {
      contextMenu.value.visible = false;
    });
  }
};

const setCenter = (newCenter: [number, number]) => {
  center.value = newCenter;
  // Also update the actual map if it exists
  if (mapRef.value) {
    const map = (mapRef.value as any).leafletObject;
    map.setView(newCenter, 11);
  }
};

const centerOnCalgary = () => {
  const calgaryCoords: [number, number] = [51.0447, -114.0719];
  setCenter(calgaryCoords);
};

const panToWithOffset = (lat: number, lng: number, offsetX: number) => {
  const map = (mapRef.value as any)?.leafletObject;
  if (!map) return;
  // Convert lat/lng to container point
  const targetPoint = map.latLngToContainerPoint([lat, lng]);
  // Offset horizontally (positive offsetX moves pin right, negative moves left)
  const offsetPoint = L.point(targetPoint.x + offsetX, targetPoint.y);
  // Convert back to lat/lng
  const offsetLatLng = map.containerPointToLatLng(offsetPoint);
  map.panTo(offsetLatLng, { animate: true });
};

const mapboxToken = import.meta.env.VITE_MAPBOX_API_TOKEN;

// Computed property for Mapbox style based on theme
const mapboxStyle = computed(() => {
  const isDark = themeStore.isDark;
  if (isDark) {
    // Use Navigation Guidance Night for dark mode
    return 'navigation-guidance-night-v4';
  } else {
    // Use basic streets style for light mode
    return 'streets-v11';
  }
});





// Tile loading event handlers
const onTileError = (error: any) => {
  // Mapbox tile error - could add user-facing error handling here if needed
};

const onTileLoad = (event: any) => {
  // Mapbox tile loaded successfully
};

defineExpose({
  setCenter,
  openPopupForSpot,
  panToWithOffset,
  centerOnCalgary,
});
</script>

<style scoped>
.map-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}
.map-instance {
  width: 100%;
  height: 100%;
  z-index: 0;
  cursor: crosshair;
}

/* Ensure tooltips are visible above other elements */
:deep(.spot-tooltip) {
  z-index: 1000 !important;
}

:deep(.leaflet-tooltip) {
  z-index: 1000 !important;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  font-size: 12px;
  white-space: nowrap;
}

:deep(.leaflet-tooltip-top:before) {
  border-top-color: #ccc;
}

/* Ensure selected marker is on top */
:deep(.selected-marker) {
  z-index: 1001 !important;
}

:deep(.selected-marker .leaflet-marker-icon) {
  z-index: 1001 !important;
}

/* Custom cursor styles for the map */
:deep(.leaflet-container) {
  cursor: crosshair !important;
}

:deep(.leaflet-marker-icon) {
  cursor: pointer !important;
}

:deep(.leaflet-popup) {
  cursor: default !important;
}

:deep(.leaflet-control) {
  cursor: pointer !important;
}

/* Preview marker tooltip styling */
:deep(.preview-tooltip) {
  z-index: 10000 !important;
}

:deep(.preview-tooltip .leaflet-tooltip) {
  background: rgba(255, 255, 255, 0.95) !important;
  border: 2px solid #10b981 !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  padding: 8px 12px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  z-index: 10000 !important;
}
</style>
