<template>
  <div class="view">
    <h1>Отчёты и статистика</h1>

    <button @click="generateReport">Сгенерировать отчёт</button>
    <div v-if="reportId">ID отчёта: <strong>{{ reportId }}</strong></div>

    <div v-if="reportId" style="margin-top: 20px;">
      <button @click="checkStatus">Проверить статус</button>
      <div v-if="status">{{ status.status }} ({{ status.progress }}%)</div>
      <button v-if="status?.download_url" @click="downloadReport">Скачать</button>
    </div>

    <hr />

    <button @click="loadStats">Показать статистику</button>
    <div v-if="stats" style="margin-top: 10px; white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 6px;">
      {{ JSON.stringify(stats, null, 2) }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const reportId = ref('');
const status = ref(null);
const stats = ref(null);

// Генерация отчёта
const generateReport = () => {
  reportId.value = 'report-' + Date.now();
  status.value = { status: 'processing', progress: 0, download_url: null };
  // Имитация завершения через 2 сек
  setTimeout(() => {
    status.value = {
      status: 'completed',
      progress: 100,
      download_url: `https://example.com/reports/${reportId.value}.xlsx`,
    };
  }, 2000);
};

// Проверка статуса
const checkStatus = () => {
  if (!status.value) {
    alert('Сначала сгенерируйте отчёт');
  }
};

// Скачивание
const downloadReport = () => {
  const a = document.createElement('a');
  a.href = status.value.download_url;
  a.download = '';
  a.click();
};

// Загрузка статистики
const loadStats = () => {
  stats.value = {
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
};
</script>

<style scoped>
.view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #271f12;
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
</style>