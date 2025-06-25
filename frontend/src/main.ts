import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import './style.css';
import axios from 'axios';
import { useAuthStore } from './stores/auth';
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);
app.use(Toast);

// Configure axios base URL
axios.defaults.baseURL = '/';

// Use the auth store outside of a component
const authStore = useAuthStore(pinia);

axios.interceptors.request.use((config) => {
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
});

app.mount('#app');
