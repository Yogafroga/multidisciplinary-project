import { defineStore } from 'pinia';
import api from '../services/api.js';
import { ref } from 'vue';

export const useReportsStore = defineStore('reports', () => {
    const reportStatus = ref(null);
    const statusLoading = ref(false);
    const statusError = ref(null);

    const summary = ref(null);
    const summaryLoading = ref(false);
    const summaryError = ref(null);

    // === Генерация отчёта ===
    const generateReport = async (payload) => {
        try {
            const response = await api.post('/reports/generate', payload);
            return { success: true, data: response.data };
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to generate report';
            return { success: false, error: errorMsg };
        }
    };

    // === Проверка статуса отчёта ===
    const fetchReportStatus = async (reportId) => {
        statusLoading.value = true;
        statusError.value = null;
        try {
            const response = await api.get(`/reports/${reportId}/status`);
            reportStatus.value = response.data;
            return response.data;
        } catch (error) {
            statusError.value = error.response?.data?.message || 'Failed to fetch status';
            console.error('Fetch status error:', statusError.value);
            throw error;
        } finally {
            statusLoading.value = false;
        }
    };

    // === Скачивание отчёта ===
    const downloadReport = async (reportId) => {
        try {
            const response = await api.get(`/reports/${reportId}/download`, {
                responseType: 'blob', // важно для скачивания файла
            });

            // Создаём ссылку для скачивания
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${reportId}.xlsx`); // можно уточнить по format
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            return { success: true };
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Download failed';
            return { success: false, error: errorMsg };
        }
    };

    // === Получение сводной статистики ===
    const fetchSummaryStats = async (params = {}) => {
        summaryLoading.value = true;
        summaryError.value = null;
        try {
            const response = await api.get('/statistics/summary', { params });
            summary.value = response.data;
            return response.data;
        } catch (error) {
            summaryError.value = error.response?.data?.message || 'Failed to fetch statistics';
            console.error('Fetch summary error:', summaryError.value);
            throw error;
        } finally {
            summaryLoading.value = false;
        }
    };

    return {
        // State
        reportStatus,
        statusLoading,
        statusError,
        summary,
        summaryLoading,
        summaryError,

        // Actions
        generateReport,
        fetchReportStatus,
        downloadReport,
        fetchSummaryStats,
    };
});