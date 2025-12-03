import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useCowsStore = defineStore('cows', () => {
    // State
    const history = ref({
        page: 1,
        limit: 20,
        total: 0,
        total_pages: 1,
        data: [],
    });
    const historyLoading = ref(false);
    const historyError = ref(null);

    const detail = ref(null);
    const detailLoading = ref(false);
    const detailError = ref(null);

    // Мок-данные
    const mockHistoryData = [
        {
            id: 1,
            animal_id: '001',
            animal_tag: '123ABC',
            weight: 450.5,
            weight_units: 'kg',
            confidence: 0.92,
            image_url: 'https://via.placeholder.com/150',
            created_at: '2024-01-15T10:30:00Z',
            created_by: 'admin',
            batch_id: 'batch-001',
        },
        {
            id: 2,
            animal_id: '002',
            animal_tag: '456DEF',
            weight: 460.1,
            weight_units: 'kg',
            confidence: 0.89,
            image_url: 'https://via.placeholder.com/150',
            created_at: '2024-01-16T11:00:00Z',
            created_by: 'admin',
            batch_id: 'batch-002',
        },
    ];

    const mockDetailData = (id) => ({
        id,
        animal_id: '001',
        animal_tag: '123ABC',
        weight: 450.5,
        weight_units: 'kg',
        confidence: 0.92,
        image_url: 'https://via.placeholder.com/400',
        detection_data: {
            bbox: [100, 200, 300, 400],
            landmarks: [[150, 220], [250, 220], [200, 280]],
            dimensions: { length: 180.5, height: 150.2, girth: 210.3 }
        },
        created_at: '2024-01-15T10:30:00Z',
        created_by: 'admin',
        updated_at: '2024-01-15T10:30:00Z'
    });

    // Actions

    const fetchHistory = async (params = {}) => {
        historyLoading.value = true;
        historyError.value = null;

        try {
            // Имитация задержки API
            await new Promise(resolve => setTimeout(resolve, 800));
            history.value = {
                ...history.value,
                data: mockHistoryData,
                total: mockHistoryData.length,
                page: params.page || 1,
                limit: params.limit || 20,
            };
            return history.value;
        } catch (error) {
            historyError.value = 'Ошибка загрузки истории';
            console.error(historyError.value);
            throw error;
        } finally {
            historyLoading.value = false;
        }
    };

    const fetchDetail = async (id) => {
        detailLoading.value = true;
        detailError.value = null;

        try {
            await new Promise(resolve => setTimeout(resolve, 500));
            detail.value = mockDetailData(id);
            return detail.value;
        } catch (error) {
            detailError.value = 'Ошибка загрузки деталей';
            console.error(detailError.value);
            throw error;
        } finally {
            detailLoading.value = false;
        }
    };

    const deleteRecord = async (id) => {
        try {
            // Имитация удаления
            await new Promise(resolve => setTimeout(resolve, 300));
            history.value.data = history.value.data.filter(item => item.id !== id);
            return { success: true };
        } catch (error) {
            return { success: false, error: 'Не удалось удалить запись' };
        }
    };

    const uploadImage = async (file, animal_id) => {
        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            const newEntry = {
                id: Date.now(),
                animal_id,
                weight: (450 + Math.random() * 30).toFixed(1),
                confidence: (0.85 + Math.random() * 0.1).toFixed(2),
                created_at: new Date().toISOString(),
                image_url: 'https://via.placeholder.com/150/green',
            };
            history.value.data.unshift(newEntry);
            return { success: true, data: newEntry };
        } catch (error) {
            return { success: false, error: 'Ошибка загрузки изображения' };
        }
    };

    const uploadArchive = async (file, animal_type = null) => {
        try {
            await new Promise(resolve => setTimeout(resolve, 1500));
            return {
                success: true,
                data: {
                    archive_id: 'archive-' + Date.now(),
                    total_images: 3,
                    processed_images: 3,
                    failed_images: 0,
                    summary: {
                        total_weight: 1350.5,
                        average_weight: 450.17,
                        animal_count: 3,
                    },
                    details: [
                        { filename: 'cow1.jpg', animal_id: '001', weight: 450.5, status: 'success' },
                        { filename: 'cow2.jpg', animal_id: '002', weight: 460.1, status: 'success' },
                        { filename: 'cow3.jpg', animal_id: '003', weight: 439.9, status: 'success' },
                    ]
                }
            };
        } catch (error) {
            return { success: false, error: 'Ошибка загрузки архива' };
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