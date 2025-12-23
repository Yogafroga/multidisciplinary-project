<template>
  <div class="table-wrapper">
    <!-- Загрузка -->
    <div v-if="loading" class="loading">
      Загрузка данных...
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="error">
      Ошибка: {{ error }}
      <button @click="loadData">Повторить</button>
    </div>

    <!-- Таблица -->
    <table v-else class="data-table">
      <thead>
      <tr>
        <!-- Чекбокс "Выбрать все" -->
        <th class="checkbox-th">
          <div class="th-block">
            Выбрать
            <div class="custom-checkbox" @click="toggleSelectAll">
              <CheckboxChecked v-if="allPageSelected" />
              <CheckboxUnchecked v-else />
            </div>
          </div>
        </th>

        <!-- Заголовки -->
        <th
            v-for="field in head"
            :key="field.key"
            class="sortable"
            :class="{ 'sorted': sort.key === field.key }"
            @click="field.sortable && toggleSort(field.key)"
        >
          <div class="th-block">
            {{ field.title }}
            <SortIcon
                v-if="field.sortable"
                class="sort-icon"
                :class="{
                  'active-asc': sort.key === field.key && sort.order === 'asc',
                  'active-desc': sort.key === field.key && sort.order === 'desc',
                }"
            />
          </div>
        </th>
      </tr>
      </thead>

      <tbody>
      <tr
          v-for="item in displayedItems"
          :key="item.id"
          :class="{ 'selected-row': selectedItems.includes(item.id) }"
      >
        <td class="checkbox-td">
          <div class="custom-checkbox" @click="toggleRow(item.id)">
            <CheckboxChecked v-if="selectedItems.includes(item.id)" />
            <CheckboxUnchecked v-else />
          </div>
        </td>

        <td v-for="field in head" :key="field.key">
          <template v-if="field.key === 'photo'">
            {{ item.original_name ? getFileName(item.original_name) : '—' }}
          </template>

          <template v-else-if="field.key === 'date'">
            {{ formatDate(item.created_at) }}
          </template>

          <template v-else-if="field.key === 'time'">
            {{ formatTime(item.created_at) }}
          </template>

          <template v-else-if="field.key === 'weight'">
            {{ item.weight }} кг
          </template>

          <template v-else-if="field.key === 'action'">
            <div class="actions-td">
              <button
                  class="action-btn info"
                  title="Скачать PDF"
                  @click="downloadPDF(item)"
              >
                <Pdf_M />
              </button>
              <button
                  class="action-btn excel"
                  title="Скачать Excel"
                  @click="downloadExcel(item)"
              >
                <File_M />
              </button>
              <button
                  class="action-btn delete"
                  title="Удалить запись"
                  @click="deleteRecord(item.id)"
              >
                <TrashIcon />
              </button>
            </div>
          </template>

          <template v-else>
            {{ item[field.key] }}
          </template>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- Пагинация -->
    <div v-if="!loading" class="pagination">
      <button class="icon-btn" :disabled="currentPage === 1" @click="prevPage">
        <previousIcon />
      </button>
      <span>{{ currentPage }} / {{ pagesCount }}</span>
      <button class="icon-btn" :disabled="currentPage >= pagesCount" @click="nextPage">
        <nextIcon />
      </button>
    </div>

    <!-- Кнопка "Экспорт выбранных" -->
    <div v-if="selectedItems.length > 0" class="bulk-actions">
      <Button variant="download" @click="downloadSelected('pdf')">Экспорт PDF</Button>
      <Button variant="download" @click="downloadSelected('excel')">Экспорт Excel</Button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useCowsStore } from '../../stores/cows.js';
import { useReportsStore } from '../../stores/reports.js';
import Button from '../../components/ui/button.vue';

// Иконки
import previousIcon from '../../assets/icons/main/Left.vue';
import nextIcon from '../../assets/icons/main/Right.vue';
import CheckboxUnchecked from '../../assets/icons/main/Check_Box_Blank.vue';
import CheckboxChecked from '../../assets/icons/main/Check_Box.vue';
import SortIcon from '../../assets/icons/main/Chevron_Both.vue';
import File_M from '../../assets/icons/files/X_M.vue';
import Pdf_M from '../../assets/icons/files/Pdf_M.vue';
import TrashIcon from '../../assets/icons/main/Trash.vue';

const cowsStore = useCowsStore();
const reportsStore = useReportsStore();

const props = defineProps({
  type: {
    type: String,
    default: 'weighings',
  },
  filterId: {
    type: [String, Number],
    default: '',
  },
  filterDateRange: {
    type: Object,
    default: () => ({ start: null, end: null }),
  },
});

// --- Заголовки ---
const head = computed(() => {
  if (props.type === 'operation') {
    return [
      { title: 'Количество', key: 'count', sortable: true },
      { title: 'Ср. вес', key: 'average_weight', sortable: true },
      { title: 'Общий вес', key: 'total_weight', sortable: true },
      { title: 'Дата', key: 'date', sortable: true },
      { title: 'Время', key: 'time', sortable: true },
      { title: 'Действия', key: 'action', sortable: false },
    ];
  }

  return [
    { title: 'Фото', key: 'photo', sortable: false },
    { title: 'Номер бирки', key: 'animal_id', sortable: true },
    { title: 'Дата', key: 'date', sortable: true },
    { title: 'Время', key: 'time', sortable: true },
    { title: 'Вес/кг', key: 'weight', sortable: true },
    { title: 'Действия', key: 'action', sortable: false },
  ];
});

// --- Пагинация ---
const currentPage = ref(1);
const limit = ref(10);

// --- Сортировка ---
const sort = ref({ key: 'created_at', order: 'desc' });

const toggleSort = (key) => {
  if (sort.value.key === key) {
    sort.value.order = sort.value.order === 'asc' ? 'desc' : 'asc';
  } else {
    sort.value.key = key;
    sort.value.order = 'asc';
  }
  currentPage.value = 1;
  loadData();
};

// --- Состояния ---
const loading = computed(() => {
  return props.type === 'operation' ? cowsStore.batchStats.loading : cowsStore.history.loading;
});

const error = computed(() => {
  return props.type === 'operation' ? cowsStore.batchStats.error : cowsStore.history.error;
});

const pagesCount = computed(() => {
  return props.type === 'operation'
      ? Math.max(1, Math.ceil(cowsStore.batchStats.total / limit.value))
      : Math.max(1, Math.ceil(cowsStore.history.total / limit.value));
});

// --- Загрузка данных ---
const loadData = async () => {
  if (props.type === 'operation') {
    await cowsStore.fetchBatchStats({
      page: currentPage.value,
      limit: limit.value,
    });
  } else {
    const params = {
      page: currentPage.value,
      limit: limit.value,
      sort: sort.value.key,
      order: sort.value.order.toUpperCase(),
    };

    if (props.filterId && String(props.filterId).trim() !== '') {
      params.animal_id = String(props.filterId).trim();
    }

    if (props.filterDateRange?.start) {
      params.start_date = formatDateISO(props.filterDateRange.start);
    }

    if (props.filterDateRange?.end) {
      params.end_date = formatDateISO(props.filterDateRange.end);
    }

    await cowsStore.fetchHistory(params);
  }
};

onMounted(() => {
  loadData();
});

// --- Отображаемые данные ---
const displayedItems = computed(() => {
  if (props.type === 'operation') {
    return (cowsStore.batchStats.items || []).map((item) => {
      let createdAt = null;
      if (item.create_date) {
        const [year, month, day] = item.create_date.split('-').map(Number);
        const [hour = 0, minute = 0, second = 0] = (item.create_time || '00:00:00').split(':').map(Number);
        createdAt = new Date(year, month - 1, day, hour, minute, second);
      }

      return {
        id: item.batch_number,
        count: item.photo_count,
        average_weight: item.avg_weight ? Math.round(item.avg_weight) : '—',
        total_weight: Math.round(item.total_weight || 0),
        created_at: createdAt,
      };
    });
  }

  return (cowsStore.history.data || []).map((item) => ({
    id: item.id,
    animal_id: item.animal_id,
    weight: Math.round(item.weight),
    original_name: item.original_name,
    created_at: new Date(item.created_at),
  }));
});

// --- Форматирование даты и времени ---
const formatDate = (date) => {
  if (!date || isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('ru-RU');
};

const formatTime = (date) => {
  if (!date || isNaN(date.getTime())) return '—';
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
};

const formatDateISO = (date) => {
  if (!date) return null;
  const d = new Date(date);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

// --- Пагинация ---
const nextPage = () => {
  if (currentPage.value < pagesCount.value) {
    currentPage.value++;
    loadData();
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    loadData();
  }
};

// --- Выбор строк ---
const selectedItems = ref([]);

const allPageSelected = computed(() =>
    displayedItems.value.length > 0 &&
    displayedItems.value.every((i) => selectedItems.value.includes(i.id))
);

const toggleRow = (id) => {
  const idx = selectedItems.value.indexOf(id);
  if (idx > -1) selectedItems.value.splice(idx, 1);
  else selectedItems.value.push(id);
};

const toggleSelectAll = () => {
  if (allPageSelected.value) {
    selectedItems.value = [];
  } else {
    selectedItems.value = displayedItems.value.map((i) => i.id);
  }
};

const generateAndDownloadReport = async (ids, format) => {
  if (!Array.isArray(ids) || ids.length === 0) {
    alert('Нет записей для экспорта');
    return;
  }

  let payload = {
    format,
    report_type: 'summary',
    include_images: false,
  };

  // 🔥 Если это батчи (operations)
  if (props.type === 'operation') {
    const allDetectionIds = [];

    // Проходим по каждому выбранному batch_number
    for (const batchNumber of ids) {
      // Ищем батч в store
      const batch = cowsStore.batchStats.items.find(b => b.batch_number === batchNumber);
      if (batch && Array.isArray(batch.detection_ids)) {
        allDetectionIds.push(...batch.detection_ids); // добавляем все ID взвешиваний
      }
    }

    if (allDetectionIds.length === 0) {
      alert('Нет данных для экспорта: выбранные батчи не содержат взвешиваний');
      return;
    }

    payload.include_weighs = allDetectionIds; // ✅ передаём как ID взвешиваний
  }

  // 🔥 Если это отдельные взвешивания (weighings)
  if (props.type === 'weighings') {
    payload.include_weighs = ids;
  }

  console.log('Отправляем payload:', payload); // 🔥 для проверки

  const res = await reportsStore.generateReport(payload);
  if (!res.success) {
    alert('Ошибка генерации: ' + res.error);
    return;
  }

  const reportId = res.data.report_id;
  console.log('Отчёт сгенерирован, ID:', reportId);

  // Ждём 10 секунд (можно улучшить позже)
  await new Promise((resolve) => setTimeout(resolve, 10000));

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Токен не найден');
      return;
    }

    const url = `${import.meta.env.VITE_API_BASE_URL}/reports/${reportId}/download`;
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200) {
      const blob = await response.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${reportId}.${format === 'excel' ? 'xlsx' : 'pdf'}`;
      a.click();
      URL.revokeObjectURL(a.href);
    } else {
      alert(`Ошибка скачивания: ${response.status}`);
    }
  } catch (error) {
    console.error('Ошибка скачивания:', error);
    alert('Не удалось скачать файл');
  }
};

// --- Экспорт по одной записи ---
const downloadPDF = async (item) => {
  await generateAndDownloadReport([item.id], 'pdf');
};

const downloadExcel = async (item) => {
  await generateAndDownloadReport([item.id], 'excel');
};

// --- Экспорт выбранных строк ---
const downloadSelected = async (format) => {
  await generateAndDownloadReport(selectedItems.value, format);
};

// --- Удаление записи ---
const deleteRecord = async (id) => {
  if (!confirm('Удалить эту запись?')) return;

  const res = await cowsStore.deleteHistoryRecord(id);
  if (res.success) {
    alert('Запись удалена');
    loadData();
  } else {
    alert('Ошибка: ' + res.error);
  }
};

// --- Фильтры ---
watch(
    () => [props.filterId, props.filterDateRange],
    () => {
      currentPage.value = 1;
      if (props.type !== 'operation') {
        loadData();
      }
    },
    { deep: true }
);

// --- Вспомогательные ---
const getFileName = (url) => {
  if (!url) return '—';
  return url.split('/').pop();
};

// --- Эмит выбранных ---
const emits = defineEmits(['update:selectedItems']);
watch(selectedItems, (newVal) => {
  emits('update:selectedItems', newVal);
});
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/bigTable';
</style>