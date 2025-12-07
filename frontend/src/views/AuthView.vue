<template>
  <div class="auth">
    <div class="auth__card">
      <div class="auth__header">
        <Logo class="auth__logo" />
      </div>

      <div class="auth__content">
        <!-- Форма входа -->
        <form v-if="mode === 'login'" class="auth__form" @submit.prevent="handleLogin">
          <div class="auth__field">
            <Label class="auth__label" for-id="username" required>Логин</Label>
            <Input class="auth__input" id="username" v-model="loginForm.username" type="text"
                   :error="errors.usernameError" placeholder="Введите логин" required />
          </div>

          <div class="auth__field">
            <Label class="auth__label" for-id="password" required>Пароль</Label>
            <Input class="auth__input" id="password" v-model="loginForm.password" type="password"
                   :error="errors.passwordError" placeholder="Введите пароль" required />
          </div>

          <Button class="auth__submit" type="submit" variant="primary" :loading="loading" :disabled="loading">
            Войти
          </Button>

          <p class="auth__switch">
            Нет аккаунта?
            <a class="auth__switch-link" @click.prevent="goTo('register')">Зарегистрироваться</a>
          </p>

          <p v-if="error" class="auth__error">{{ error }}</p>
        </form>

        <!-- Форма регистрации -->
        <form v-else class="auth__form" @submit.prevent="handleRegister">
          <div class="auth__field">
            <Label class="auth__label" for-id="reg-login" required>Логин</Label>
            <Input class="auth__input" id="reg-login" v-model="registerForm.login" type="text"
                   :error="errors.registerLogin" placeholder="Введите логин" required />
          </div>

          <div class="auth__field">
            <Label class="auth__label" for-id="reg-password" required>Пароль</Label>
            <Input class="auth__input" id="reg-password" v-model="registerForm.password" type="password"
                   :error="errors.registerPassword" placeholder="Введите пароль" required />
          </div>

          <!-- <div class="auth__field">
            <Label class="auth__label" for-id="reg-confirm" required>Подтверждение пароля</Label>
            <Input class="auth__input" id="reg-confirm" v-model="registerForm.confirmPassword" type="password"
              :error="errors.registerConfirmPassword" placeholder="Повторите пароль" required />
          </div> -->

          <div class="auth__checkbox">
            <label class="auth__checkbox-label">
              <input type="checkbox" v-model="registerForm.agree" class="auth__checkbox-input" />
              Я принимаю условия
              <a href="#" class="auth__link">Пользовательского соглашения</a>
              и даю согласие на <a href="#" class="auth__link">персональных данных</a>
            </label>

            <p v-if="errors.agreeError" class="auth__error">{{ errors.agreeError }}</p>
          </div>

          <Button class="auth__submit" type="submit" variant="primary" :loading="loading" :disabled="loading">
            Зарегистрироваться
          </Button>

          <p class="auth__switch">
            Уже есть аккаунт?
            <a class="auth__switch-link" @click.prevent="goTo('login')">Войти</a>
          </p>

          <p v-if="success" class="auth__success">{{ success }}</p>
          <p v-if="error" class="auth__error">{{ error }}</p>
        </form>
      </div>
    </div>

    <div class="auth__illustration">
      <img class="auth__cow" src="../assets/images/cow.svg" alt="cow" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from "../stores/auth.js"

import Button from '../components/ui/button.vue'
import Input from '../components/ui/input.vue'
import Label from '../components/ui/label.vue'
import Logo from '../assets/icons/logo/Logo-big.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

// режим: 'login' или 'register'
const mode = ref(route.path === '/register' ? 'register' : 'login')

watch(() => route.path, (p) => {
  mode.value = p === '/register' ? 'register' : 'login'
})

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  login: '',
  password: '',
  confirmPassword: '',
  agree: false
})

const errors = ref({
  usernameError: '',
  passwordError: '',
  registerLogin: '',
  registerPassword: '',
  registerConfirmPassword: '',
  agreeError: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')

const goTo = (m) => {
  mode.value = m
  error.value = ''
  success.value = ''

  if (m === 'login') router.push('/login').catch(() => { })
  else router.push('/register').catch(() => { })
}

// Логика входа — без проверки сложности
const handleLogin = async () => {
  errors.value.usernameError = ''
  errors.value.passwordError = ''
  error.value = ''

  let hasError = false
  if (!loginForm.value.username.trim()) {
    errors.value.usernameError = '*Введите логин'
    hasError = true
  }
  if (!loginForm.value.password) {
    errors.value.passwordError = '*Введите пароль'
    hasError = true
  }
  if (hasError) return

  loading.value = true
  const res = await auth.login(loginForm.value.username, loginForm.value.password)
  loading.value = false

  if (res.success) {
    router.push('/main')
  } else {
    error.value = res.error?.detail || '*Ошибка входа'
  }
}

// Логика регистрации — без валидации пароля и без сравнения
const handleRegister = async () => {
  errors.value.registerLogin = ''
  errors.value.registerPassword = ''
  errors.value.agreeError = ''
  error.value = ''
  success.value = ''

  let hasError = false

  if (!registerForm.value.login.trim()) {
    errors.value.registerLogin = '*Введите логин'
    hasError = true
  }

  if (!registerForm.value.password) {
    errors.value.registerPassword = '*Введите пароль'
    hasError = true
  }

  if (!registerForm.value.agree) {
    errors.value.agreeError = '*Необходимо принять условия'
    hasError = true
  }

  if (hasError) return

  loading.value = true
  const res = await auth.register(registerForm.value.login, registerForm.value.password, 1)
  loading.value = false

  if (res.success) {
    success.value = 'Аккаунт создан! Перенаправление на вход...'
    setTimeout(() => {
      goTo('login')
      registerForm.value.login = ''
      registerForm.value.password = ''
      success.value = ''
    }, 1400)
  } else {
    error.value = res.error?.detail || res.error?.message || '*Ошибка регистрации'
  }
}
</script>

<style scoped lang="scss">
@use '../assets/styles/components/AuthView';
</style>