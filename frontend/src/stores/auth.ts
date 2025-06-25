import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

interface User {
  id: string;
  email: string;
  name?: string;
  picture?: string;
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'));
  const user = ref<User | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  function setToken(value: string | null) {
    token.value = value;
    if (value) {
      localStorage.setItem('token', value);
    } else {
      localStorage.removeItem('token');
    }
  }

  async function fetchUser() {
    if (!token.value) return;
    try {
      const { data } = await axios.get('/api/auth/google/me', {
        withCredentials: true,
      });
      user.value = data;
    } catch (err) {
      console.error('Failed to fetch current user', err);
      logout(); // Use logout action to clear state
    }
  }

  function login() {
    window.location.href = '/api/auth/google/login';
  }

  function logout() {
    setToken(null);
    user.value = null;
  }

  function checkTokenFromUrl() {
    const url = new URL(window.location.href);
    const tokenParam = url.searchParams.get('token');
    if (tokenParam) {
      setToken(tokenParam);
      // Clean up URL to remove token query param
      url.searchParams.delete('token');
      window.history.replaceState({}, '', url.pathname);
      // Fetch user right after getting token
      fetchUser();
    }
  }

  // Initial check when the store is instantiated
  fetchUser();
  checkTokenFromUrl();

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    fetchUser,
    checkTokenFromUrl,
  };
});
