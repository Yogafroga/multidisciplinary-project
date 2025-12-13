<template>
  <div class="table-wrapper">
    <!-- Загрузка -->
    <div v-if="cowsStore.history.loading" class="loading">
      Загрузка данных...
    </div>

    <!-- Ошибка -->
    <div v-else-if="cowsStore.history.error" class="error">
      Ошибка: {{ cowsStore.history.error }}
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
          <th v-for="field in head" :key="field.key" class="sortable" :class="{ 'sorted': sort.key === field.key }"
            @click="field.sortable && toggleSort(field.key)">
            <div class="th-block">
              {{ field.title }}
              <SortIcon v-if="field.sortable" class="sort-icon" :class="{
                'active-asc': sort.key === field.key && sort.order === 'asc',
                'active-desc': sort.key === field.key && sort.order === 'desc',
              }" />
            </div>
          </th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="item in displayedItems" :key="item.id" :class="{ 'selected-row': selectedItems.includes(item.id) }">
          <!-- Чекбокс строки -->
          <td class="checkbox-td">
            <div class="custom-checkbox" @click="toggleRow(item.id)">
              <CheckboxChecked v-if="selectedItems.includes(item.id)" />
              <CheckboxUnchecked v-else />
            </div>
          </td>

          <!-- Данные и действия -->
          <td v-for="field in head" :key="field.key">
            <!-- Фото -->
            <img v-if="field.key === 'photo'" :src="item.image_url" :alt="`Фото ${item.animal_id}`"
              style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />

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
                <button class="action-btn info" title="Скачать PDF" @click="downloadPDF(item)">
                  <Pdf_M />
                </button>
                <button class="action-btn excel" title="Скачать Excel" @click="downloadExcel(item)">
                  <File_M />
                </button>
                <button class="action-btn delete" title="Удалить запись" @click="deleteRecord(item.id)">
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
    <div v-if="!cowsStore.history.loading" class="pagination">
      <button class="icon-btn" :disabled="currentPage === 1" @click="prevPage">
        <previousIcon />
      </button>
      <span>{{ currentPage }} / {{ pagesCount }}</span>
      <button class="icon-btn" :disabled="currentPage >= pagesCount" @click="nextPage">
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
import TrashIcon from '../../assets/icons/main/Trash.vue'; // Создайте этот компонент

const cowsStore = useCowsStore();
const props = defineProps({
  type: {
    type: String,
    default: 'weighings', // 'weighings' | 'operation'
  },
  filterId: {
    type: [String, Number],
    default: ''
  },
  filterDateRange: {
    type: Object,
    default: () => ({ start: null, end: null })
  },
});

// --- Заголовки ---
const head = computed(() => {
  if (props.type === 'operation') {
    return [
      { title: 'Номер бирки', key: 'animal_id', sortable: true },
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

const pagesCount = computed(() => Math.max(1, Math.ceil(cowsStore.history.total / limit.value)));

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

// --- Загрузка данных ---
const loadData = async () => {
  const params = {
    page: currentPage.value,
    limit: limit.value,
    sort: sort.value.key,
    order: sort.value.order.toUpperCase(),
  };

  if (
    props.filterId !== null &&
    props.filterId !== undefined &&
    props.filterId.toString().trim() !== ''
  ) {
    params.animal_id = String(props.filterId).trim();
  }

  if (props.filterDateRange?.start) {
    params.start_date = new Date(props.filterDateRange.start)
      .toISOString()
      .split('T')[0];
  }

  if (props.filterDateRange?.end) {
    params.end_date = new Date(props.filterDateRange.end)
      .toISOString()
      .split('T')[0];
  }

  console.log('FETCH HISTORY PARAMS:', params);
  await cowsStore.fetchHistory(params);
};


onMounted(() => {
  loadData();
});

// --- Отображаемые данные ---
const displayedItems = computed(() => {
  if (!cowsStore.history.data) return [];

  return cowsStore.history.data.map((item) => ({
    ...item,
    id: item.id,
    animal_id: item.animal_id,
    weight: item.weight,
    image_url: item.image_url,
    created_at: item.created_at,
  }));
});

// --- Форматирование даты и времени ---
const formatDate = (iso) => {
  const d = new Date(iso);
  return d.toLocaleDateString('ru-RU');
};

const formatTime = (iso) => {
  const d = new Date(iso);
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
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

// --- Выделение строк ---
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
  doc.text(`Запись ID: ${item.animal_id}`, 10, 10);
  doc.setFontSize(12);
  doc.text(`Вес: ${item.weight} кг`, 10, 20);
  doc.text(`Дата: ${formatDate(item.created_at)} ${formatTime(item.created_at)}`, 10, 30);

  if (item.image_url) {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    img.src = item.image_url;
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      const dataUrl = canvas.toDataURL('image/jpeg');
      doc.addImage(dataUrl, 'JPEG', 10, 40, 50, 50);
      doc.save(`record_${item.animal_id}.pdf`);
    };
    img.onerror = () => {
      doc.save(`record_${item.animal_id}.pdf`);
    };
  } else {
    doc.save(`record_${item.animal_id}.pdf`);
  }
};

const downloadExcel = (item) => {
  const worksheet = XLSX.utils.json_to_sheet([item]);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Запись');
  XLSX.writeFile(workbook, `record_${item.animal_id}.xlsx`);
};

// --- Удаление записи ---
const deleteRecord = async (id) => {
  if (!confirm('Удалить эту запись?')) return;

  const res = await cowsStore.deleteHistoryRecord(id);
  if (res.success) {
    alert('Запись удалена');
    // Перезагрузим текущую страницу
    loadData();
  } else {
    alert('Ошибка: ' + res.error);
  }
};

watch(
  () => [props.filterId, props.filterDateRange],
  () => {
    currentPage.value = 1; // сбрасываем страницу
    loadData();
  },
  { deep: true }
)

</script>

<style scoped lang="scss">
@use '../../assets/styles/components/bigTable';

.actions-td {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &.delete {
    color: #d32f2f;

    &:hover {
      background-color: #ffebee;
    }
  }

  &.info {
    color: #1976d2;

    &:hover {
      background-color: #e3f2fd;
    }
  }

  &.excel {
    color: #2e7d32;

    &:hover {
      background-color: #e8f5e9;
    }
  }
}
</style>