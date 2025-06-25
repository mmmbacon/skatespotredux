<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click="$emit('close')"
  >
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" @click.stop>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Share Spot</h3>
        <button
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-800 text-xl"
        >
          &times;
        </button>
      </div>

      <div class="text-center mb-6">
        <div class="bg-gray-100 p-4 rounded-lg mb-4">
          <!-- QR Code placeholder - you can integrate a QR code library here -->
          <div
            class="w-48 h-48 bg-white mx-auto border-2 border-gray-300 flex items-center justify-center"
          >
            <span class="text-gray-500 text-sm"
              >QR Code for {{ spotName }}</span
            >
          </div>
        </div>
        <p class="text-sm text-gray-600 mb-4">
          Scan this QR code to view this spot on your mobile device
        </p>
      </div>

      <div class="flex flex-col space-y-3">
        <button
          @click="handleShare"
          class="flex items-center justify-center space-x-2 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
        >
          <Icon icon="mdi:share-variant" class="w-4 h-4" />
          <span>Share Link</span>
        </button>

        <button
          @click="handlePrint"
          class="flex items-center justify-center space-x-2 bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700 transition-colors"
        >
          <Icon icon="mdi:printer" class="w-4 h-4" />
          <span>Print QR Code</span>
        </button>

        <button
          @click="handleDownload"
          class="flex items-center justify-center space-x-2 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 transition-colors"
        >
          <Icon icon="mdi:download" class="w-4 h-4" />
          <span>Download QR Code</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue';

defineProps<{
  isVisible: boolean;
  spotName: string;
}>();

defineEmits<{
  close: [];
}>();

const handleShare = () => {
  if (navigator.share) {
    navigator.share({
      title: 'Check out this skate spot!',
      text: `Look at this spot: ${spotName}`,
      url: window.location.href,
    });
  } else {
    // Fallback: copy to clipboard
    navigator.clipboard.writeText(window.location.href);
    // You could add a toast notification here
  }
};

const handlePrint = () => {
  window.print();
};

const handleDownload = () => {
  // This would generate and download the QR code image
  // You can integrate a QR code library like qrcode.js here
  console.log('Download QR code functionality would go here');
};
</script>
