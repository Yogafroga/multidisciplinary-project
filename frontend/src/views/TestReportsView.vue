<template>
  <div class="view">
    <h1>📊 Отчёты и статистика</h1>

    <!-- Генерация отчёта -->
    <button @click="generateReport">Сгенерировать отчёт</button>

    <!-- Отображение ID отчёта -->
    <div v-if="reports.reportStatus" class="report-id">
      ID отчёта: <strong>{{ reports.reportStatus.report_id }}</strong>
    </div>

    <!-- Проверка статуса и скачивание -->
    <div v-if="reports.reportStatus" class="status-section" style="margin-top: 20px;">
      <button @click="checkStatus">Проверить статус</button>

      <div class="status-info" v-if="reports.reportStatus">
        Статус: <strong>{{ reports.reportStatus.status }}</strong>
        <span v-if="reports.reportStatus.progress !== undefined">
          ({{ reports.reportStatus.progress }}%)
        </span>
      </div>

      <button
          v-if="reports.reportStatus?.download_url"
          @click="handleDownload"
      >
        Скачать отчёт
      </button>
    </div>

    <hr />

    <!-- Статистика -->
    <button @click="loadStats">Показать статистику</button>
    <div
        v-if="reports.summary"
        class="summary-output"
        style="
          margin-top: 10px;
          white-space: pre-wrap;
          background: #f5f5f5;
          padding: 10px;
          border-radius: 6px;
          font-family: monospace;
          font-size: 12px;
        "
    >
      {{ JSON.stringify(reports.summary, null, 2) }}
    </div>
  </div>
</template>

<script setup>
import { useReportsStore } from '../stores/reports.js';

// Подключаем стор
const reports = useReportsStore();

// === Методы ===

// Генерация отчёта
const generateReport = async () => {
  await reports.generateReport({
    format: 'excel',
    animal_ids: ['001'],
    start_date: '2024-01-01',
    end_date: '2024-01-31',
    report_type: 'summary',
  });
};

// Проверка статуса
const checkStatus = async () => {
  if (!reports.reportStatus?.report_id) return;
  await reports.fetchReportStatus(reports.reportStatus.report_id);
};

// Скачивание — передаём ID явно
const handleDownload = async () => {
  if (!reports.reportStatus?.report_id) return;
  await reports.downloadReport(reports.reportStatus.report_id);
};

// Загрузка статистики
const loadStats = async () => {
  await reports.fetchSummaryStats();
};
</script>

<style scoped>
.view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

button {
  padding: 8px 16px;
  margin: 5px;
  background: #4cc9f0;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

button:hover {
  background: #3a86ff;
}

.report-id {
  margin-top: 10px;
  font-weight: 500;
}
</style>