<script setup lang="ts">
import { onMounted, defineEmits, ref, watch } from 'vue';
import { useSpotsStore } from '@/stores/spots';
import type { Spot } from '@/stores/spots';
import { useAuthStore } from '@/stores/auth';
import BaseButton from './BaseButton.vue';
import SpotForm from './SpotForm.vue';

const spotsStore = useSpotsStore();
const authStore = useAuthStore();
const emit = defineEmits([
  'focus-spot',
  'location-to-edit',
  'location-updated',
  'start-creating',
]);

const props = defineProps({
  editedLocation: {
    type: Object as () => [number, number] | null,
    default: null,
  },
});

const isFormVisible = ref(false);
const editingSpot = ref<Spot | null>(null);
const formLocation = ref<[number, number] | null>(null);

onMounted(() => {
  // The fetch is already called in App.vue, so this is redundant
  // spotsStore.fetchSpots();
});

watch(
  () => props.editedLocation,
  (newLocation) => {
    formLocation.value = newLocation;
  }
);

watch(isFormVisible, (isVisible) => {
  if (!isVisible) {
    emit('location-to-edit', null);
  }
});

const handleSpotClick = (spot: Spot) => {
  emit('focus-spot', spot.location.coordinates.slice().reverse());
};

const showCreateForm = () => {
  editingSpot.value = null;
  // For creating, we'll need to get the current map center
  // This is a bit tricky, so for now let's use a default
  // and let the user drag the marker.
  const initialLocation: [number, number] = [51.05, -114.09]; // Default to Calgary
  formLocation.value = initialLocation;
  emit('location-to-edit', initialLocation);
  isFormVisible.value = true;
};

const showEditForm = (spot: Spot) => {
  editingSpot.value = spot;
  const spotLocation: [number, number] = spot.location.coordinates
    .slice()
    .reverse() as [number, number];
  formLocation.value = spotLocation;
  emit('location-to-edit', spotLocation);
  isFormVisible.value = true;
};

const closeForm = () => {
  isFormVisible.value = false;
  editingSpot.value = null;
  formLocation.value = null;
  emit('location-to-edit', null);
};

const handleSave = async (formData: any) => {
  if (!editingSpot.value) return;

  const payload = {
    ...formData,
    location: {
      type: 'Point',
      coordinates: formLocation.value
        ? [formLocation.value[1], formLocation.value[0]]
        : [0, 0], // Lng, Lat
    },
  };

  await spotsStore.updateSpot(editingSpot.value.id, payload);
  closeForm();
};

const handleDelete = async (spotId: string) => {
  if (confirm('Are you sure you want to delete this spot?')) {
    await spotsStore.deleteSpot(spotId);
  }
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold text-gray-800">Skate Spots</h1>
      <BaseButton
        @click="$emit('start-creating')"
        v-if="authStore.isAuthenticated"
      >
        Add Spot
      </BaseButton>
    </div>
    <div class="mb-4">
      <input
        type="text"
        v-model="spotsStore.searchQuery"
        placeholder="Search spots..."
        class="w-full px-3 py-2 border rounded-lg"
      />
    </div>
    <div v-if="spotsStore.isLoading" class="text-center">
      <p class="text-gray-600">Loading spots...</p>
    </div>
    <div v-else-if="spotsStore.error" class="text-red-500 text-center">
      <p>{{ spotsStore.error }}</p>
    </div>
    <div v-else-if="spotsStore.filteredSpots.length === 0" class="text-center">
      <p class="text-gray-600">No spots found.</p>
    </div>
    <ul v-else class="space-y-4">
      <li
        v-for="spot in spotsStore.filteredSpots"
        :key="spot.id"
        class="p-4 bg-white border rounded-lg shadow-sm cursor-pointer hover:bg-gray-50"
        @click="handleSpotClick(spot)"
      >
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">{{ spot.name }}</h2>
            <p class="text-gray-700">{{ spot.description }}</p>
          </div>
          <div
            v-if="authStore.user && authStore.user.id === spot.user_id"
            class="flex space-x-2 flex-shrink-0 ml-4"
          >
            <BaseButton
              @click.stop="showEditForm(spot)"
              variant="secondary"
              size="sm"
            >
              Edit
            </BaseButton>
            <BaseButton
              @click.stop="handleDelete(spot.id)"
              variant="danger"
              size="sm"
            >
              Delete
            </BaseButton>
          </div>
        </div>
      </li>
    </ul>
    <SpotForm
      :is-visible="isFormVisible"
      :spot="editingSpot"
      @close="closeForm"
      @save="handleSave"
    />
  </div>
</template>
