import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useReportsStore = defineStore('reports', () => {
    const reportStatus = ref(null);
    const statusLoading = ref(false);
    const statusError = ref(null);

    const summary = ref(null);
    const summaryLoading = ref(false);
    const summaryError = ref(null);

    // Мок статуса
    const mockReportStatus = (id) => ({
        report_id: id,
        status: 'completed',
        progress: 100,
        download_url: `https://example.com/reports/${id}.xlsx`,
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
    });

    // Мок статистики
    const mockSummary = {
        period: { start_date: '2024-01-01', end_date: '2024-01-31' },
        total_weighings: 150,
        total_animals: 50,
        average_weight: 450.5,
        weight_change: '+2.3%',
        by_animal_type: {
            cow: { count: 30, average_weight: 450.5 },
            bull: { count: 20, average_weight: 550.2 },
        },
        daily_weighings: { '2024-01-15': 10, '2024-01-16': 8 },
    };

    // === Генерация отчёта ===
    const generateReport = async (payload) => {
        try {
            await new Promise(resolve => setTimeout(resolve, 600));
            const reportId = 'report-' + Date.now();
            // Устанавливаем начальный статус
            reportStatus.value = {
                report_id: reportId,
                status: 'processing',
                progress: 0,
                download_url: null,
            };
            // Имитация завершения
            setTimeout(() => {
                reportStatus.value = mockReportStatus(reportId);
            }, 2000);
            return { success: true, data: { report_id: reportId } };
        } catch (error) {
            return { success: false, error: 'Не удалось сгенерировать отчёт' };
        }
    };

    // === Проверка статуса ===
    const fetchReportStatus = async (reportId) => {
        statusLoading.value = true;
        statusError.value = null;

        try {
            await new Promise(resolve => setTimeout(resolve, 500));
            reportStatus.value = mockReportStatus(reportId);
            return reportStatus.value;
        } catch (error) {
            statusError.value = 'Ошибка получения статуса';
            console.error(statusError.value);
            throw error;
        } finally {
            statusLoading.value = false;
        }
    };

    // === Скачивание отчёта ===
    const downloadReport = async (reportId) => {
        try {
            await new Promise(resolve => setTimeout(resolve, 300));
            const link = document.createElement('a');
            link.href = `https://example.com/reports/${reportId}.xlsx`;
            link.download = ''; // браузер сам определит имя
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            return { success: true };
        } catch (error) {
            return { success: false, error: 'Ошибка скачивания' };
        }
    };

    // === Загрузка статистики ===
    const fetchSummaryStats = async (params = {}) => {
        summaryLoading.value = true;
        summaryError.value = null;

        try {
            await new Promise(resolve => setTimeout(resolve, 800));
            summary.value = mockSummary;
            return summary.value;
        } catch (error) {
            summaryError.value = 'Ошибка загрузки статистики';
            console.error(summaryError.value);
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