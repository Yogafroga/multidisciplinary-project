import { defineStore } from 'pinia';
import api from '../services/api.js';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null);
    const token = ref(localStorage.getItem('access_token') || null);

    /**
     * Вход: получение токена
     */
    const login = async (username, password) => {
        try {
            // Используем URLSearchParams вместо FormData
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);
            params.append('grant_type', 'password');

            const response = await api.post('/auth/token', params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            const { access_token } = response.data;
            token.value = access_token;
            localStorage.setItem('access_token', access_token);

            user.value = {
                username
            }

            return { success: true };
        } catch (error) {
            console.error('[Auth] Ошибка входа:', error.response?.data || error.message);
            return { success: false, error: error.response?.data || { detail: 'Ошибка сети или сервера' } };
        }
    };

    /**
     * Регистрация
     */
    const register = async (login, password, role = 1) => {
        try {
            const response = await api.post('/auth/create_user', {
                login,
                password,
                role,
            });
            return { success: true, data: response.data };
        } catch (error) {
            console.error('[Auth] Ошибка регистрации:', error.response?.data || error.message);
            return { success: false, error: error.response?.data || { detail: 'Ошибка сети или сервера' } };
        }
    };

    /**
     * Выход
     */
    const logout = () => {
        token.value = null;
        user.value = null;
        localStorage.removeItem('access_token');
    };

    /**
     * Проверка авторизации
     */
    const isAuthenticated = () => !!token.value;

    return { user, token, login, register, logout, isAuthenticated };
});