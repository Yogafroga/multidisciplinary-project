<!-- frontend/src/views/RegisterView.vue -->
<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>Регистрация</h2>

      <form @submit.prevent="handleRegister">
        <div class="field">
          <label>Логин</label>
          <input v-model="form.login" type="text" required />
        </div>

        <div class="field">
          <label>Пароль</label>
          <input v-model="form.password" type="password" required />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Создание...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>

      <p class="switch">
        Уже есть аккаунт?
        <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import {useAuthStore} from "../stores/auth.js";

const router = useRouter();
const auth = useAuthStore();

const form = ref({
  login: '',
  password: '',
});

const loading = ref(false);
const error = ref('');
const success = ref('');

const handleRegister = async () => {
  loading.value = true;
  error.value = '';
  success.value = '';

  const result = await auth.register(form.value.login, form.value.password);

  loading.value = false;

  if (result.success) {
    success.value = 'Аккаунт создан! Теперь войдите.';
    setTimeout(() => router.push('/login'), 2000);
  } else {
    error.value = result.error.detail?.[0]?.msg || 'Ошибка регистрации';
  }
};
</script>

<style scoped>

</style>