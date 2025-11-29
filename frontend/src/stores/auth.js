import { defineStore } from 'pinia';
import api from "../services/api.js";
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null);
    const token = ref(localStorage.getItem('access_token') || null);

    const login = async (username, password) => {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            formData.append('grant_type', 'password');

            const response = await api.post('/auth/token', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });

            token.value = response.data.access_token;
            localStorage.setItem('access_token', token.value);

            return { success: true };
        } catch (error) {
            return { success: false, error: error.response?.data || error.message };
        }
    };

    const register = async (login, password, role = 1) => {
        try {
            const response = await api.post('/auth/create_user', {
                login,
                password,
                role,
            });
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: error.response?.data || error.message };
        }
    };

    const logout = () => {
        token.value = null;
        user.value = null;
        localStorage.removeItem('access_token');
    };

    const isAuthenticated = () => !!token.value;

    return { user, token, login, register, logout, isAuthenticated };
});