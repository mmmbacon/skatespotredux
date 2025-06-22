<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'default' | 'outline' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  type?: 'button' | 'submit' | 'reset';
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  type: 'button',
  size: 'md',
});

const baseClasses =
  'inline-flex items-center rounded-md font-medium shadow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2';

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'secondary':
      return 'bg-gray-200 text-gray-800 hover:bg-gray-300';
    case 'danger':
      return 'bg-red-600 text-white hover:bg-red-700';
    case 'outline':
      return 'border border-input bg-transparent shadow-sm hover:bg-accent hover:text-accent-foreground';
    case 'default':
    default:
      return 'bg-black text-white hover:bg-black/90';
  }
});

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-2 py-1 text-xs';
    case 'lg':
      return 'px-4 py-2 text-lg';
    case 'md':
    default:
      return 'px-3 py-2 text-sm';
  }
});

const classes = computed(() => {
  return `${baseClasses} ${variantClasses.value} ${sizeClasses.value}`;
});
</script>

<template>
  <button :type="props.type" :class="classes"><slot /></button>
</template>
