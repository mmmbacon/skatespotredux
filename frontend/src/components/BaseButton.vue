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
      return 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600';
    case 'danger':
      return 'bg-red-600 text-white hover:bg-red-700';
    case 'outline':
      return 'border border-gray-300 dark:border-gray-600 bg-transparent shadow-sm hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white';
    case 'default':
    default:
      return 'bg-black dark:bg-white text-white dark:text-black hover:bg-black/90 dark:hover:bg-gray-100';
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
