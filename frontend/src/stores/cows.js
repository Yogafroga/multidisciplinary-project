import { defineStore } from 'pinia';
import api from '../services/api.js';
import { ref } from 'vue';

export const useCowsStore = defineStore('cows', () => {
    const history = ref([]);
    const historyLoading = ref(false);
    const historyError = ref(null);

    const detail = ref(null);
    const detailLoading = ref(false);
    const detailError = ref(null);

    // === История взвешиваний ===
    const fetchHistory = async (params = {}) => {
        historyLoading.value = true;
        historyError.value = null;
        try {
            const response = await api.get('/history', { params });
            history.value = response.data;
            return response.data;
        } catch (error) {
            historyError.value = error.response?.data?.message || 'Failed to fetch history';
            console.error('Fetch history error:', historyError.value);
            throw error;
        } finally {
            historyLoading.value = false;
        }
    };

    // === Детали взвешивания ===
    const fetchDetail = async (id) => {
        detailLoading.value = true;
        detailError.value = null;
        try {
            const response = await api.get(`/history/${id}`);
            detail.value = response.data;
            return response.data;
        } catch (error) {
            detailError.value = error.response?.data?.message || 'Failed to fetch detail';
            console.error('Fetch detail error:', detailError.value);
            throw error;
        } finally {
            detailLoading.value = false;
        }
    };

    // === Удаление записи ===
    const deleteRecord = async (id) => {
        try {
            await api.delete(`/history/${id}`);
            history.value.data = history.value.data.filter(item => item.id !== id);
            return { success: true };
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to delete record';
            console.error('Delete error:', errorMsg);
            return { success: false, error: errorMsg };
        }
    };

    // === Загрузка изображения ===
    const uploadImage = async (file, animal_id) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('animal_id', animal_id);

        try {
            const response = await api.post('/upload_images', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            // Добавляем в историю новую запись (если нужно)
            return { success: true, data: response.data };
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Upload failed';
            return { success: false, error: errorMsg };
        }
    };

    // === Загрузка архива ===
    const uploadArchive = async (file, animal_type = null) => {
        const formData = new FormData();
        formData.append('file', file);
        if (animal_type) formData.append('animal_type', animal_type);

        try {
            const response = await api.post('/upload_archive', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            return { success: true, data: response.data };
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Archive upload failed';
            return { success: false, error: errorMsg };
        }
    };

    return {
        // State
        history,
        historyLoading,
        historyError,
        detail,
        detailLoading,
        detailError,

        // Actions
        fetchHistory,
        fetchDetail,
        deleteRecord,
        uploadImage,
        uploadArchive,
    };
});