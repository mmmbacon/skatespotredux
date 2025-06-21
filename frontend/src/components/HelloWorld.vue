<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

defineProps<{ msg: string }>();

const count = ref(0);
const status = ref<string>('checking...');

onMounted(async () => {
  try {
    const { data } = await axios.get('/health');
    status.value = data.status ?? 'unknown';
  } catch (error) {
    status.value = 'error';
    console.error('Health check failed', error);
  }
});
</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">count is {{ count }}</button>
    <p>
      Edit
      <code>components/HelloWorld.vue</code> to test HMR
    </p>
  </div>

  <p>
    Check out
    <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank"
      >create-vue</a
    >, the official Vue + Vite starter
  </p>
  <p>
    Learn more about IDE Support for Vue in the
    <a
      href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support"
      target="_blank"
      >Vue Docs Scaling up Guide</a
    >.
  </p>
  <p class="read-the-docs">Click on the Vite and Vue logos to learn more</p>
  <p>Backend status: {{ status }}</p>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
