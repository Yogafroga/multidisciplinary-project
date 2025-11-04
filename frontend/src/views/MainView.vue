<!-- frontend/src/views/MainView.vue -->
<template>
  <div class="main-container">
    <header class="main-header">
      <h1>Добро пожаловать!</h1>
      <button @click="logout" class="logout-btn">Выйти</button>
    </header>

    <main class="main-content">
      <p>Вы успешно вошли в систему.</p>
      <p>Токен: <code>{{ token?.slice(0, 20) }}...</code></p>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore} from "../stores/auth.js";
import { useRouter } from 'vue-router';
import { computed } from 'vue';

const auth = useAuthStore();
const router = useRouter();

const token = computed(() => auth.token);

const logout = () => {
  auth.logout();
  router.push('/login');
};
</script>

<style scoped>

</style>