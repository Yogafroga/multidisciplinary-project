<!-- frontend/src/views/LoginView.vue -->
<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>Вход</h2>

      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>Логин</label>
          <input v-model="form.username" type="text" required />
        </div>

        <div class="field">
          <label>Пароль</label>
          <input v-model="form.password" type="password" required />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>

      <p v-if="error" class="error">{{ error }}</p>

      <p class="switch">
        Нет аккаунта?
        <router-link to="/register">Зарегистрироваться</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore} from "../stores/auth.js";

const router = useRouter();
const auth = useAuthStore();

const form = ref({
  username: '',
  password: '',
});

const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  loading.value = true;
  error.value = '';

  const result = await auth.login(form.value.username, form.value.password);

  loading.value = false;

  if (result.success) {
    router.push('/main');
  } else {
    error.value = result.error.detail || 'Ошибка входа';
  }
};
</script>

<style scoped>

</style>