<template>
  <div class="map-container">
    <div v-if="isMounted" class="map-instance">
      <l-map ref="map" v-model:zoom="zoom" :center="[40.7128, -74.006]">
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          layer-type="base"
          name="OpenStreetMap"
        ></l-tile-layer>

        <!-- Loop through spots and create markers -->
        <l-marker
          v-for="spot in spots"
          :key="spot.id"
          :lat-lng="spot.location.coordinates.slice().reverse()"
        >
          <l-popup>
            <b>{{ spot.name }}</b
            ><br />{{ spot.description }}
          </l-popup>
        </l-marker>
      </l-map>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, PropType } from 'vue';
import 'leaflet/dist/leaflet.css';
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet';
import L from 'leaflet';
import type { Spot } from '@/stores/spots'; // Import the Spot interface

// This is a common fix for icon path issues with bundlers
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl: iconUrl,
  iconRetinaUrl: iconRetinaUrl,
  shadowUrl: shadowUrl,
});

// Define props
const props = defineProps({
  spots: {
    type: Array as PropType<Spot[]>,
    required: true,
    default: () => [],
  },
});

const zoom = ref(12);
const isMounted = ref(false);

onMounted(() => {
  // By setting this flag in onMounted, we ensure the map component
  // is only rendered on the client, avoiding SSR issues.
  isMounted.value = true;
});
</script>

<style scoped>
.map-container,
.map-instance {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  height: 100%;
  width: 100%;
}
</style>
