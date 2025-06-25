import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false);

  const toggleTheme = () => {
    isDark.value = !isDark.value;
    // Save to localStorage
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
    // Apply theme to document
    applyTheme();
  };

  const applyTheme = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const initializeTheme = () => {
    // Check localStorage first
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      isDark.value = savedTheme === 'dark';
    } else {
      // Check system preference
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    applyTheme();
  };

  return {
    isDark,
    toggleTheme,
    applyTheme,
    initializeTheme,
  };
});
