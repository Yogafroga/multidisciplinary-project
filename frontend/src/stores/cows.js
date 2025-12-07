import { defineStore } from 'pinia';
import api from '../services/api.js';

export const useCowsStore = defineStore('cows', () => {
    /**
     * Загружает одно изображение
     * @param {File} file - изображение (jpg, png)
     * @param {string} animal_id - ID животного
     * @returns {Promise<{ success: boolean, data?: any, error?: string }>}
     */
    const uploadImage = async (file, animal_id) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('animal_id', animal_id);

        try {
            const response = await api.post('/upload_images', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            return { success: true, data: response.data };
        } catch (error) {
            const message = error.response?.data?.detail?.[0]?.msg || 'Ошибка загрузки изображения';
            return { success: false, error: message };
        }
    };

    /**
     * Загружает ZIP-архив
     * @param {File} file - ZIP-файл
     * @returns {Promise<{ success: boolean, data?: any, error?: string }>}
     */
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

    return {
        uploadImage,
        uploadArchive,
    };
});