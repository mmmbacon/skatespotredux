import { ref, onMounted } from 'vue';
import axios from 'axios';

const token = ref<string | null>(localStorage.getItem('token'));
const user = ref<{
  id: string;
  email: string;
  name?: string;
  picture?: string;
} | null>(null);

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
    const { data } = await axios.get('http://localhost:3000/auth/google/me', {
      headers: { Authorization: `Bearer ${token.value}` },
      withCredentials: true,
    });
    user.value = data;
  } catch (err) {
    console.error('Failed to fetch current user', err);
    logout();
  }
}

function login() {
  // Redirect to backend OAuth login
  window.location.href = 'http://localhost:3000/auth/google/login';
}

function logout() {
  setToken(null);
  user.value = null;
}

onMounted(() => {
  // If redirected from backend after successful OAuth
  const url = new URL(window.location.href);
  const tokenParam = url.searchParams.get('token');
  if (tokenParam) {
    setToken(tokenParam);
    // Clean up URL to remove token query param
    url.searchParams.delete('token');
    window.history.replaceState({}, '', url.pathname);
  }
  fetchUser();
});

export function useAuth() {
  return { token, user, login, logout };
}
