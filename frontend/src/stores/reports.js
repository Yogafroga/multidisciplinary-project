// stores/reports.js
import { defineStore } from 'pinia';
import api from '../services/api.js';
import { ref } from 'vue';

export const useReportsStore = defineStore('reports', () => {
    // === Генерация отчёта ===
    const generateReport = async (payload) => {
        try {
            const response = await api.post('/reports/generate', payload);
            return { success: true, data: response.data };
        } catch (error) {
            const message = error.response?.data?.detail || 'Не удалось сгенерировать отчёт';
            return { success: false, error: message };
        }
    };

    return {
        generateReport,
    };
});