<!-- frontend/src/views/LoginView.vue -->
<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>Вход</h2>

      <form @submit.prevent="handleLogin">
        <div class="field">
          <Label for-id="username" required>Логин</Label>
          <Input id="username" v-model="form.username" type="email" :error="errors.usernameError"  placeholder="Введите логин" required />
        </div>

        <div class="field">
          <Label for-id="password" required>Пароль</Label>
          <Input id="password" v-model="form.password" type="password" :error="errors.passwordError" placeholder="Введите пароль" required />
        </div>
        <Button
          tupe="button"
          variant="primary"
          :loading="loading"
          :disabled="loading"
          @click="handleLogin"
          >
          Войти
        </Button>
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
import Button from '../components/button.vue';
import Input from '../components/input.vue';
import Label from '../components/lable.vue';


const router = useRouter();
const auth = useAuthStore();

const form = ref({
  username: '',
  password: '',
});

const errors = ref({
  usernameError: '',
  passwordError: ''
});

const loading = ref(false);
const error = ref('');

const handleLogin = async () => {

  errors.value.usernameError = '';
  errors.value.passwordError = '';
  error.value = '';

  let hasError = false;
  if(!form.value.username) {
    errors.value.usernameError = 'Введите логин';
    hasError = true;
  }

  if(!form.value.password) {
    errors.value.passwordError = 'Введите пароль';
    hasError = true;
  }

  if (hasError) {
    return;
  }

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