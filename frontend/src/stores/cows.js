import { defineStore } from 'pinia';
import { ref } from 'vue'; // ✅ Добавлен импорт
import api from '../services/api.js';

export const useCowsStore = defineStore('cows', () => {
    // --- Состояние ---
    const history = ref({
        data: [],
        page: 1,
        limit: 20,
        total: 0,
        total_pages: 1,
        loading: false,
        error: null,
    });

    const calculatedGroup = ref(null);

    const setCalculatedGroup = (summary) => {
        calculatedGroup.value = summary;
    }

    const clearCalculatedGroup = () => {
        calculatedGroup.value = null; // ✅ правильно
    }

    // --- Загрузка файлов ---
    const uploadImage = async (file, animal_id, onProgress) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('animal_id', animal_id);

        try {
            const response = await api.post('/upload_images', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (event) => {
                    if (!event.total) return;
                    const percent = Math.round((event.loaded * 100) / event.total);
                    onProgress?.(event.loaded, percent);
                }
            });

            return { success: true, data: response.data };
        } catch (error) {
            const message = error.response?.data?.detail?.[0]?.msg || 'Ошибка загрузки изображения';
            return { success: false, error: message };
        }
    };

    const uploadArchive = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/upload_archive', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            return { success: true, data: response.data };
        } catch (error) {
            const message = error.response?.data?.detail?.[0]?.msg || 'Ошибка загрузки архива';
            return { success: false, error: message };
        }
    };

    // --- История взвешиваний ---
    const fetchHistory = async (params = {}) => {
        history.value.loading = true;
        history.value.error = null;

        try {
            const { data } = await api.get('/api/history', { params });

            history.value.data = data.data ?? [];
            history.value.page = data.page ?? 1;
            history.value.limit = data.limit ?? 20;
            history.value.total = data.total ?? 0;
            history.value.total_pages = data.total_pages ?? 1;

            return data;
        } catch (error) {
            const message =
                error.response?.data?.detail ||
                error.message ||
                'Ошибка загрузки истории';

            history.value.error = message;
            console.error('[CowsStore] fetchHistory error:', message);
            throw error;
        } finally {
            history.value.loading = false;
        }
    };

    const fetchHistoryByAnimalId = async (animal_id) => {
        try {
            const response = await api.get(`/api/history/${animal_id}`);
            return response.data;
        } catch (error) {
            const message = error.response?.data?.detail?.[0]?.msg || 'Животное не найдено';
            console.error('[CowsStore] fetchHistoryByAnimalId error:', message);
            throw error;
        }
    };

    const deleteHistoryRecord = async (id) => {
        try {
            const response = await api.delete(`/api/history/${id}`);
            history.value.data = history.value.data.filter(item => item.id !== id);
            return { success: true, message: response.data?.message };
        } catch (error) {
            const message = error.response?.data?.detail?.[0]?.msg || 'Не удалось удалить запись';
            console.error('[CowsStore] deleteHistoryRecord error:', message);
            return { success: false, error: message };
        }
    };

    return {
        history,
        uploadImage,
        uploadArchive,
        fetchHistory,
        fetchHistoryByAnimalId,
        deleteHistoryRecord,
        calculatedGroup,
        setCalculatedGroup,
        clearCalculatedGroup,
    };
});