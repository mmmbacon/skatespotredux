<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click="$emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 transition-colors"
      @click.stop
    >
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Share Spot</h3>
        <button
          @click="$emit('close')"
          class="text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 text-xl transition-colors"
        >
          &times;
        </button>
      </div>

      <div class="text-center mb-6">
        <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg mb-4">
          <!-- Actual QR Code -->
          <canvas
            ref="qrCanvas"
            class="mx-auto border-2 border-gray-300 dark:border-gray-500 rounded"
            style="max-width: 100%; height: auto"
          />
          <!-- Fallback if QR code fails to generate -->
          <div
            v-if="!qrCodeGenerated"
            class="w-48 h-48 bg-white dark:bg-gray-600 mx-auto border-2 border-gray-300 dark:border-gray-500 flex items-center justify-center"
          >
            <span class="text-gray-500 dark:text-gray-400 text-sm text-center">
              Generating QR code...
              <br />
              <small>If this doesn't appear, try refreshing</small>
            </span>
          </div>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
          Scan this QR code to view
          <strong>{{ spotName }}</strong>
          on your mobile device
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400 break-all">
          {{ shareUrl }}
        </p>
      </div>

      <div class="flex flex-col space-y-3">
        <button
          @click="handleShare"
          class="flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
        >
          <Icon
            icon="mdi:share-variant"
            class="w-4 h-4"
          />
          <span>Share Link</span>
        </button>

        <button
          @click="handleDownload"
          class="flex items-center justify-center space-x-2 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors"
        >
          <Icon
            icon="mdi:download"
            class="w-4 h-4"
          />
          <span>Download QR Code</span>
        </button>

        <button
          @click="handlePrint"
          class="flex items-center justify-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded transition-colors"
        >
          <Icon
            icon="mdi:printer"
            class="w-4 h-4"
          />
          <span>Print QR Code</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { Icon } from '@iconify/vue';
  import { ref, computed, watch, nextTick, onMounted } from 'vue';
  import QRCode from 'qrcode';

  const props = defineProps<{
    isVisible: boolean;
    spotName: string;
    spotId: string;
  }>();

  defineEmits<{
    close: [];
  }>();

  const qrCanvas = ref<HTMLCanvasElement>();
  const qrCodeGenerated = ref(false);

  // Generate a shareable URL for the spot
  const shareUrl = computed(() => {
    const baseUrl = window.location.origin;
    return `${baseUrl}/spot/${props.spotId}`;
  });

  // Test QR code generation on mount
  onMounted(async () => {
    // Test QR code generation
    const testCanvas = document.createElement('canvas');
    try {
      await QRCode.toCanvas(testCanvas, 'https://example.com', {
        width: 100,
        margin: 1,
      });
      console.log('QR code library test successful');
    } catch (error) {
      console.error('QR code library test failed:', error);
    }
  });

  // Reset QR code generated flag when modal opens
  watch(
    () => props.isVisible,
    async visible => {
      if (visible) {
        qrCodeGenerated.value = false;
        // Wait a bit for the modal to render
        await nextTick();
        await new Promise(resolve => setTimeout(resolve, 100));

        if (qrCanvas.value && shareUrl.value) {
          try {
            console.log('Generating QR code for URL:', shareUrl.value);
            await QRCode.toCanvas(qrCanvas.value, shareUrl.value, {
              width: 200,
              margin: 2,
              color: {
                dark: '#000000',
                light: '#FFFFFF',
              },
            });
            console.log('QR code generated successfully');
            qrCodeGenerated.value = true;
          } catch (error) {
            console.error('Error generating QR code:', error);
            qrCodeGenerated.value = false;
          }
        } else {
          console.log('Canvas or URL not ready:', {
            canvas: !!qrCanvas.value,
            url: shareUrl.value,
          });
        }
      }
    },
    { immediate: true }
  );

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Check out this skate spot: ${props.spotName}`,
          text: `Look at this spot: ${props.spotName}`,
          url: shareUrl.value,
        });
      } catch (error) {
        console.log('Share cancelled or failed:', error);
        fallbackCopyToClipboard();
      }
    } else {
      fallbackCopyToClipboard();
    }
  };

  const fallbackCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl.value);
      // TODO: Add toast notification here
      console.log('URL copied to clipboard');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const handleDownload = () => {
    if (!qrCanvas.value) return;

    // Create download link
    const link = document.createElement('a');
    link.download = `${props.spotName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_qr_code.png`;
    link.href = qrCanvas.value.toDataURL('image/png');

    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrint = () => {
    if (!qrCanvas.value) return;

    // Create a new window for printing
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const imageUrl = qrCanvas.value.toDataURL('image/png');

    printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>QR Code - ${props.spotName}</title>
      <style>
        body {
          margin: 0;
          padding: 20px;
          text-align: center;
          font-family: Arial, sans-serif;
        }
        .qr-container {
          margin: 20px auto;
          max-width: 300px;
        }
        img {
          max-width: 100%;
          height: auto;
          border: 2px solid #ccc;
          border-radius: 8px;
        }
        h1 {
          color: #333;
          margin-bottom: 10px;
        }
        .url {
          font-size: 12px;
          color: #666;
          word-break: break-all;
          margin-top: 10px;
        }
        @media print {
          body { margin: 0; }
        }
      </style>
    </head>
    <body>
      <div class="qr-container">
        <h1>${props.spotName}</h1>
        <img src="${imageUrl}" alt="QR Code for ${props.spotName}" />
        <div class="url">${shareUrl.value}</div>
      </div>
    </body>
    </html>
  `);

    printWindow.document.close();
    printWindow.focus();

    // Wait for image to load before printing
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 500);
  };
</script>
