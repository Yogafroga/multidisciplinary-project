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

        <!-- Заголовки из head -->
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
        <!-- Чекбокс строки -->
        <td class="checkbox-td">
          <div class="custom-checkbox" @click="toggleRow(item.id)">
            <CheckboxChecked v-if="selectedItems.includes(item.id)" />
            <CheckboxUnchecked v-else />
          </div>
        </td>

        <!-- Данные и действия -->
        <td v-for="field in head" :key="field.key">
          <!-- Фото (только название файла) -->
          <template v-if="field.key === 'photo'">
            {{ item.original_name ? getFileName(item.original_name) : '—' }}
          </template>

          <!-- Дата -->
          <template v-else-if="field.key === 'date'">
            {{ formatDate(item.created_at) }}
          </template>

          <!-- Время -->
          <template v-else-if="field.key === 'time'">
            {{ formatTime(item.created_at) }}
          </template>

          <!-- Вес -->
          <template v-else-if="field.key === 'weight'">
            {{ item.weight }} кг
          </template>

          <!-- Действия -->
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

          <!-- Остальные поля -->
          <template v-else>
            {{ item[field.key] }}
          </template>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- Пагинация -->
    <div v-if="!loading" class="pagination">
      <button
          class="icon-btn"
          :disabled="currentPage === 1"
          @click="prevPage"
      >
        <previousIcon />
      </button>
      <span>{{ currentPage }} / {{ pagesCount }}</span>
      <button
          class="icon-btn"
          :disabled="currentPage >= pagesCount"
          @click="nextPage"
      >
        <nextIcon />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useCowsStore } from '../../stores/cows.js';
import { jsPDF } from 'jspdf';
import * as XLSX from 'xlsx';

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
const props = defineProps({
  type: {
    type: String,
    default: 'weighings', // 'weighings' | 'operation'
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

// --- Вычисляем, какое состояние загружается/ошибается
const loading = computed(() => {
  return props.type === 'operation'
      ? cowsStore.batchStats.loading
      : cowsStore.history.loading;
});

const error = computed(() => {
  return props.type === 'operation'
      ? cowsStore.batchStats.error
      : cowsStore.history.error;
});

// --- Пагинация: общее количество страниц ---
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
      params.start_date = new Date(props.filterDateRange.start).toISOString().split('T')[0];
    }

    if (props.filterDateRange?.end) {
      params.end_date = new Date(props.filterDateRange.end).toISOString().split('T')[0];
    }

    console.log('FETCH HISTORY PARAMS:', params);
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
      // Парсим дату и время в один объект Date
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
    created_at: new Date(item.created_at), // Убедимся, что это Date
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

// --- Экспорт ---
const downloadPDF = (item) => {
  const doc = new jsPDF();
  doc.setFontSize(16);
  doc.text(`Запись ID: ${item.animal_id || 'Batch ' + item.id}`, 10, 10);
  doc.setFontSize(12);
  doc.text(`Вес: ${item.weight || item.total_weight} кг`, 10, 20);
  doc.text(`Дата: ${formatDate(item.created_at)} ${formatTime(item.created_at)}`, 10, 30);
  doc.save(`record_${item.animal_id || item.id}.pdf`);
};

const downloadExcel = (item) => {
  const worksheet = XLSX.utils.json_to_sheet([item]);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Запись');
  XLSX.writeFile(workbook, `record_${item.animal_id || item.id}.xlsx`);
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

// --- Фильтры и сброс страницы ---
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

// --- Вспомогательные функции ---
const getFileName = (url) => {
  if (!url) return '—';
  return url.split('/').pop();
};
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/bigTable';
</style>