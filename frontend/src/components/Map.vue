<template>
  <div class="map-container">
    <l-map ref="map" v-model:zoom="zoom" :center="[40.7128, -74.006]">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
      ></l-tile-layer>
    </l-map>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import 'leaflet/dist/leaflet.css';
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet';

const zoom = ref(12);
</script>

<style scoped>
.map-container {
  height: 100vh;
  width: 100vw;
}
</style>
