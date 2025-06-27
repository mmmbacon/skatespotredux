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
      </l-map>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  onMounted,
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
const center = ref<[number, number]>([39.8283, -98.5795]); // Geographic center of US (default before geolocation)
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

onMounted(() => {
  // By setting this flag in onMounted, we ensure the map component
  // is only rendered on the client, avoiding SSR issues.
  isMounted.value = true;

  // Get user's location and center map there
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        center.value = [position.coords.latitude, position.coords.longitude];
        console.log('Centered on user location:', center.value);
      },
      (error) => {
        console.log('Location access denied or failed, using default');
      }
    );
  }
});

const onMapReady = () => {
  if (mapRef.value) {
    const map = (mapRef.value as any).leafletObject;
    
    console.log('Map ready, current center:', center.value);
    
    map.on('moveend', () => {
      const bounds = map.getBounds();
      emit('bounds-changed', {
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest(),
      });
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
  console.log('Manually centering on Calgary:', calgaryCoords);
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

// Debug logging
console.log('Mapbox token loaded:', mapboxToken ? 'YES' : 'NO');
console.log('Token length:', mapboxToken?.length || 0);
console.log('Theme:', themeStore.isDark ? 'Dark' : 'Light');
console.log('Mapbox style:', mapboxStyle.value);
console.log('Mapbox URL:', `https://api.mapbox.com/styles/v1/mapbox/${mapboxStyle.value}/tiles/{z}/{x}/{y}?access_token=${mapboxToken}`);

// Debug spots coordinates
watch(() => props.spots, (spots) => {
  console.log('Spots received:', spots.length);
  spots.forEach(spot => {
    console.log(`${spot.name}: [${spot.location.coordinates[0]}, ${spot.location.coordinates[1]}] -> [lat: ${spot.location.coordinates[1]}, lng: ${spot.location.coordinates[0]}]`);
  });
}, { immediate: true });

// Tile loading event handlers
const onTileError = (error: any) => {
  console.error('Mapbox tile error:', error);
};

const onTileLoad = (event: any) => {
  console.log('Mapbox tile loaded successfully');
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
</style>
