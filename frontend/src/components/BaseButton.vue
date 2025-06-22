<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'default' | 'outline';
  type?: 'button' | 'submit' | 'reset';
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'outline',
  type: 'button',
});

const classes = computed(() => {
  if (props.variant === 'default') {
    return 'inline-flex items-center rounded-md bg-black text-white px-3 py-2 text-sm font-medium shadow hover:bg-black/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2';
  }
  // outline
  return 'inline-flex items-center rounded-md border border-input bg-background px-3 py-2 text-sm font-medium text-white shadow hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2';
});
</script>

<template>
  <button :type="props.type" :class="classes"><slot /></button>
</template>
